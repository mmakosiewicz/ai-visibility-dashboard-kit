# Pipeline

How data gets from Brand Radar into the cards, once a day, without a surprising
bill or a 30-second timeout.

```
  ┌──────────┐   ┌────────┐   ┌───────────┐   ┌─────────┐   ┌──────┐
  │  1 PULL  │──▶│ 2 HASH │──▶│  3 GRADE  │──▶│ 4 STORE │──▶│5 SERVE│
  │  answers │   │ & skip │   │ LLM pass  │   │ snapshot│   │ cards │
  └──────────┘   └────────┘   └───────────┘   └─────────┘   └──────┘
       │              │             │
       │              │             └─ claims + verdict cache (question 6)
       │              └─ most answers are unchanged: reuse their grading
       └─ + operational pulls (bots, page dates) stored as extras
```

## 1 · Pull

One request loop per surface, paginated, for all custom prompts on the report.
Target one snapshot per day.

Things that will bite you:

- **Be explicit about which surfaces you request.** An omitted model filter can
  silently default to a single surface. You won't notice until a chart looks
  suspiciously smooth.
- **Not every surface comes from one endpoint.** One of mine isn't exposed by
  the main read API and needs a separate raw call with its own auth. Design the
  pull layer to merge heterogeneous sources into one answer shape.
- **A missing surface must not fail the run.** Record the error on the snapshot
  (`progress.claude_pull_error = ...`) and continue with the surfaces you got.
  A hard failure means no data for the day, which is strictly worse than partial
  data with a recorded gap. Check that field when a surface silently vanishes.
- **Tags may come back as ids from one endpoint and names from another.** Keep
  both maps.
- **Firewalled/allowlisted hosts and missing credentials look identical.**
  A missing API key returned the provider's own 403 even though the network
  allowed the call. Two different fixes, one symptom — check the credential
  before the firewall.

Also pull, on their own cadence: bot analytics (question 9), page dates
(question 10), tracked-page list (question 11, cached ~24h — it changes rarely
but silently).

## 2 · Hash and skip

```
answer_hash = sha1(question | surface | response_text)
```

If an answer is byte-identical to one already graded, **reuse its grading
output** and skip the LLM entirely. Most days, most answers are unchanged.

Two rules:

- **Only reuse clean gradings.** Never propagate a grading that carried an
  error, or one bad run poisons your history indefinitely.
- **Re-grade when the definition changes, not when the text does.** If you add a
  field or tighten an instruction, select rows by `eval_version` and re-grade
  just those. This is why version-stamping graded fields matters.

This one mechanism is the difference between an affordable daily cadence and a
bill you have to justify.

## 3 · Grade

Two LLM passes, described in [`grading.md`](grading.md):

- **extraction** — every answer: mentioned, position, brands, sentiment,
  winner, tool recommendation, negative themes and quotes
- **fact check** — claims extracted and verdicted against the fact sheet
  (question 6), with a verdict cache keyed by `(fingerprint, factsheet_version)`

Run with bounded concurrency (I use ~6 workers) and update
`snapshots.progress` every few completions so a long run is observable while
it's still going.

**Retry with backoff and JSON mode.** Transient empty completions and parse
failures were silently degrading my gradings until I added retries — they don't
announce themselves, they just produce a slightly wrong number.

**Give the model enough completion budget.** A long list answer plus reasoning
tokens overran my first limit and returned empty completions, which looked like
a model failure rather than a truncation.

## 4 · Store

One snapshot per run, with `status` moving `running → ok | error`, and
`progress` as a JSONB the worker updates as it goes.

Also store, as `extras`:

- the **fully computed board** (`kind='board'`) — makes the 30-day trend one
  cheap query instead of recomputing thirty boards
- **operational pulls** (`kind='crawl_health'`, `kind='freshness'`) — these are
  irreproducible; a trailing 30-day window queried today cannot be
  reconstructed next month

## 5 · Serve

The read path, and the one hard constraint: **a web request cannot take 30
seconds.** Whatever your stack, something upstream will time out.

- **Compute per request, cache per scope.** A scoped result is immutable until a
  newer snapshot lands, so an LRU keyed by
  `(start, end, surface, newest_snapshot_id)` is safe and self-invalidating.
- **Progressive rendering.** Core cards first, expensive panels after, sequenced
  into a few lanes instead of firing every heavy query at once.
- **Long operations return a job id and the client polls.** This applies to
  refresh, to fact-sheet imports, and to any page-fetching work. Cold combined
  core render in my build is ~1.7s; warm is ~0.03s.

## Cadence

| Job | When | Why |
|---|---|---|
| Answer pull + grade | daily, ~45min after the source finishes scanning | the report scans daily; weekly sampling throws away 6 of 7 days |
| Tracked-page list | daily, cached 24h | changes rarely, silently |
| Bot analytics | daily, trailing 30d | spiky; needs a window |
| Page dates | as pages enter the citation set | expensive per page |
| Fact sheet review | manual | a human approves every fact |
| Alerts | daily, after the refresh | never before — you'd alert on yesterday |

**Match your cadence to the source's.** Mine scans daily and completes around a
known time; the refresh runs shortly after. My first version sampled weekly,
which discarded 6 of 7 days and made the error-lifecycle statuses
("spreading", "resolved") meaningless.

**Alerts run after the refresh, not on their own schedule.** Otherwise they
alert on stale data and people stop believing them.

## Failure modes worth handling explicitly

| Failure | Handling |
|---|---|
| one surface's pull fails | record on snapshot, continue with the rest |
| LLM returns unparseable JSON | retry with backoff; mark the row, never reuse it |
| a run overlaps the previous one | refuse to start a second concurrent refresh; report "already running" |
| the fact sheet changed mid-run | version is stored per verdict, so old verdicts stay attributable |
| a source's schema changes | validate at the boundary (Pydantic or equivalent) and fail loudly on the pull, not silently three cards downstream |
