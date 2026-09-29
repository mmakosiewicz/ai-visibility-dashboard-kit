# Data model

The most transferable part of this spec. Get the schema right and every metric
becomes a query; get it wrong and you'll be re-pulling history to answer
questions you didn't anticipate.

Postgres DDL in [`schema.sql`](schema.sql). This file is the reasoning.

## Four rules

**1. Store answers, not scores.**

The single most important decision. Every table here exists so that one day you
can re-grade history. Your grading prompt *will* change — mine changed
substantially three times — and if you stored only "mention rate: 62%" you've
permanently lost the ability to recompute it under the new definition.

**2. One snapshot per run, and every answer belongs to one.**

A snapshot is a dated, immutable collection. Metrics for a date range are
computed by pooling snapshots, never by mutating rows. This is what makes
"what did the board say on the 3rd" answerable.

**3. Grading output goes in JSONB next to the answer.**

Not in columns. The shape of what you extract changes constantly; JSONB absorbs
that without migrations. Promote a field to a real column only when you need to
filter or index on it at scale (I did exactly that for the task-recommendation
fields).

**4. Claims are first-class rows with a stable identity.**

Fact-checking is the one place where per-answer JSONB isn't enough, because you
need to recognise *the same error* across days despite rewording. That requires
a fingerprint and its own table. Everything good about the fact-fidelity card
(cost control, error lifecycle, per-prompt accuracy) comes from this.

## The tables

| Table | Holds | Grain |
|---|---|---|
| `snapshots` | one run: status, progress, errors | per run |
| `answers` | the answer text, its sources, its grading | per (snapshot, prompt, surface) |
| `extras` | expensive computed blobs (board cache, operational pulls) | per (snapshot, kind) |
| `page_dates` | per-URL dates, citation counts, brand data, bot data | per URL |
| `page_content` | fetched page text, for verification | per URL |
| `claims` | one graded claim from one answer | per claim |
| `claim_cache` | verdict reuse keyed by (fingerprint, factsheet version) | per claim identity |
| `error_history` | lifecycle of a distinct error | per fingerprint |
| `facts` | the fact sheet under human review | per fact |
| `verifications` | "does this page actually state this claim" | per (claim, page) |
| `meta` | small key/value state (cached lists, cursors) | per key |

## Why `answers` looks like that

```sql
question   text      -- the prompt, verbatim
model      text      -- the AI surface
tag_id     text      -- prompt tag as the source gave it
rq         text      -- derived: which research question
subgroup   text      -- derived: which sub-niche
response   text      -- the full answer text
sitelinks  jsonb     -- cited sources [{url, title}]
answer_hash text     -- sha1(question|model|response)
eval       jsonb     -- grading output
```

- **`rq` and `subgroup` are denormalised** from `tag_id` at write time. Derived,
  yes — but it makes every card query trivial and lets you re-map tags without
  re-pulling.
- **`answer_hash` is the cost-control mechanism.** If an answer is byte-identical
  to one already graded, reuse the grading. Most days most answers are
  unchanged, so this is the difference between a trivial bill and a real one.
- **`sitelinks` as JSONB, not a child table.** They're always read with the
  answer and never queried independently. A child table adds a join to every
  query and buys nothing.
- **Store the answer text even when you think you won't need it.** Every
  interesting question I got later ("what exactly did it say about X") needed it.

## Fields that earned their own columns

```sql
search_volume         int      -- prompt demand; enables demand-weighted priority
tool_recommended      boolean  -- question 4's denominator
tool_names            jsonb
tool_eval_version     smallint -- which definition graded this row
response_md           text     -- answer text WITH inline citation links
```

`tool_eval_version` is the pattern worth copying: **version-stamp any graded
field whose definition might tighten.** When I sharpened what counts as a tool
recommendation, that column is what let me re-grade only the stale rows instead
of all of history.

`response_md` exists because the clean answer text had inline citation markers
stripped. Those markers tell you *which claim* a source backed — much stronger
than "this page was cited somewhere in this answer" — so it's worth storing the
raw copy separately when your source offers one.

## Claim identity

```
fingerprint = normalise(claim_text) + sorted(fact_ids it was judged against)
```

Normalisation lowercases, unifies quotes and dashes, and collapses whitespace —
but **preserves numbers**, because `$249` and `$279` must remain distinct
claims. That's the whole trick: paraphrases collapse, different facts don't.

Include the fact ids in the fingerprint so that the same sentence judged against
a different fact is a different claim. Without that, a fact-sheet correction
makes old verdicts look like they still apply.

## Denormalised caches, on purpose

Two places where I store computed output rather than recomputing:

- **`extras(snapshot_id, kind='board')`** — the full computed board per
  snapshot. Makes the trend chart and the KPI history strip a single cheap query
  over history, instead of recomputing 30 days of metrics on every page load.
  (The strip is described in
  [`05-cards/board-chrome.md`](../05-cards/board-chrome.md) — it's essentially
  free once this cache exists, and unaffordable without it.)
- **`extras(snapshot_id, kind='crawl_health'|'freshness')`** — operational pulls
  whose external trailing-window state *cannot be reconstructed* later. If you
  don't store the answer at pull time, that day's crawl health is simply gone.

Both are deliberate denormalisation. The rule: cache what's expensive or
irreproducible, recompute everything else.

## Storage shape, at my volume

~480 answers/day × answer text and sources. Answers dominate, and full text is
what you're paying for. Worth it — see rule 1 — but plan for it, and consider
archiving raw text beyond some horizon while keeping grading output forever.
