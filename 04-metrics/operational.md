# Operational metrics

For [question 9 (crawl health)](../01-questions/09-crawl-health.md) and
[question 10 (citation freshness)](../01-questions/10-citation-freshness.md).
These come from logs and pages, not from AI answers, and they behave differently
from everything else on the board.

## Error share (AI bots)

```
error_share = (4xx + 5xx requests) / all AI-bot requests, over a trailing window
```

Bucket the codes rather than reporting raw counts:

| Bucket | Codes | Reading |
|---|---|---|
| ok | 200, 304, 206 | served — 304 and 206 are healthy, not partial failures |
| accepted | 202 | queued; watch, don't panic |
| redirect | 301, 302, 307, 308 | works, wasteful at volume |
| client error | 4xx | actionable |
| server error | 5xx | actionable, urgently |

Rules:

- **Trailing window (30 days), never a single day.** Bot traffic is spiky.
- **State the window on the card**, with dates. An operational metric with an
  unstated window gets compared against an answer metric with a different
  window.
- **Rate is not severity.** 0.4% that's all 500s on your pricing page beats 3%
  that's 404s on retired blog URLs. The ranked error-path table is the
  actionable half; the headline is just a trigger.

## Stale share and median age

```
stale_share = cited pages older than 12 months / cited pages WITH A KNOWN DATE
median_age  = median(age in months) over the same population
```

- **Unknown dates are their own bucket**, reported next to both numbers. A card
  saying "8% stale" over 40 dated pages while 60 more have no date is not
  telling the truth.
- **Median age is the better trend line.** The 12-month threshold steps; the
  median moves smoothly.
- **Split cited pages from crawled pages** if you can. Cited pages are the
  worklist; crawled pages are context.

Date priority — the substance of this metric — is in
[question 10](../01-questions/10-citation-freshness.md#getting-the-date-right).
Short version: reader-visible "Updated:" beats JSON-LD `dateModified` beats the
provider's timestamp, because `dateModified` moves on any file touch and
over-trusting it under-reports staleness.

## Scope independence — the rule that surprises people

**Operational metrics must ignore the board's date-range and AI-surface
filters.**

- An AI *surface* means nothing for a server log or a page date. There is no
  "crawl health on Gemini".
- The board's snapshot range would hide data pulled today for a trailing window
  that doesn't align with it.

So these cards carry their own window control and say so on their face. The
alternative — silently ignoring the global filter — is worse: the user changes
the filter, the number doesn't move, and they conclude the dashboard is broken.

Design note in [`05-cards/scope.md`](../05-cards/scope.md).

## Store them at pull time — they're irreproducible

Answer-derived metrics can be recomputed from stored answers forever.
Operational ones **cannot**: a trailing-30-day bot window queried today cannot
be reconstructed next month. If you don't store the result when you pull it,
that day's crawl health is simply gone.

Hence `extras(snapshot_id, kind='crawl_health'|'freshness')` in the
[schema](../03-data-model/schema.sql). This is deliberate denormalisation with a
real justification, which is the only kind worth having.

One consequence for pooled ranges: when a range spans many snapshots, the
answer-derived metrics pool all of them, but operational extras come from the
**final** snapshot only — their external trailing-window state can't be pooled
meaningfully. Say that in the UI, or the two halves of the board look
inconsistent.

## Don't put these on the same axis as visibility metrics

Error share and stale share are gates. They belong in their own group, visually
separated, read first when something is inexplicable and otherwise checked
weekly. Plotting them alongside mention rate invites someone to correlate them
on a 30-day chart, which is not a thing these numbers support.
