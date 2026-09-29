# Board chrome: the parts that aren't cards

Three whole-board elements that sit outside any single card. Easy to omit from a
spec, and two of them are what make the board usable day to day.

## 1 · The KPI history strip

A row of small tiles above the cards — one per core metric, each showing the
current value, the change versus the previous day in range, a sparkline of the
selected days, and the drift across the whole range.

```
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Head-to-head  ▲2 │ │ Category mention │ │ Fact errors   ▼1 │
│ 58%              │ │ 71%              │ │ 4.2%             │
│ ╱╲╱──╲╱          │ │ ──╲╱─╲──         │ │ ╲──╱╲──          │
│ 14 days · +3 in  │ │ 14 days · flat   │ │ 14 days · −2 in  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

One tile per metric you'd actually report — mine has ten: head-to-head win rate,
category mention and position, niche mention and position, task capture, owned
citation share, fact errors, narrative negativity, adjacent-category mention.

Design rules that came out of using it:

- **Direction has a sign convention per metric.** "Up" is good for mention rate
  and bad for fact errors. Store `upGood` per metric and colour accordingly, or
  the strip teaches people the wrong reflex.
- **Two deltas, not one.** Versus the previous day (volatile) *and* drift across
  the selected range (meaningful). The second is what people act on.
- **Clip the history to the selected range**, rather than showing out-of-range
  history in a shaded band. I tried the band; it just raised "what am I looking
  at" every time.
- **State the number of days** on each tile. It's the honest sample-size
  disclosure, per metric, for free.
- **Tooltip the scope.** "Keyword research, web analytics, on-page, local SEO,
  bot analytics, AI visibility" on the niche tile — otherwise nobody remembers
  what "niche mention" covers.

Cheap to build if you cached the computed board per snapshot
([data model](../03-data-model/README.md#denormalised-caches-on-purpose)): the
whole strip is one query over history.

## 2 · The status line

One line under the header that always carries text. Sounds trivial; it fixed a
real problem.

Rules, both learned by shipping the opposite:

- **It never goes empty.** When nothing is happening it shows a quiet resting
  summary. An element that collapses to zero height shifts the entire page
  below it every time state changes — which reads as flicker.
- **Reserve its height** (`min-height`) so it can't collapse even mid-swap.
- **One writer, and don't rewrite an identical string.** A polling loop that
  re-renders the same text every few seconds causes visible repaint churn.
- **Three tones:** idle / busy / error. Enough to convey state, few enough that
  nobody has to learn a colour code.

## 3 · The Actions block

Every answer-derived card ends in a collapsed "Actions" block: not a
recommendation engine, just **deep links into the source tool**, filtered to
that question, with one sentence saying what to do in each.

Four links per card, which is the set that turned out to matter:

| Link | What to do there |
|---|---|
| **Other cited pages** | where you're mentioned: fix outdated statements, pitch new capabilities. Where you're absent: pitch inclusion. Prioritise by citations, then DR, then traffic |
| **Owned cited pages** | find topical gaps where no page of yours answers the question; refresh stale ones |
| **Competitor cited pages** | study how they position against you; feed content, messaging and product |
| **UGC pages** | find the forum/review threads and join them — answer questions, correct errors |

Why this beats generated advice: the link is **scoped to the question you're
looking at**, so it lands on a filtered view rather than the tool's homepage.
That's the difference between "I should look into this" and doing it.

Building those deep links means constructing your source tool's URL filter
params per research question — fiddly, and worth it. If your source's UI can't
be deep-linked that precisely, the fallback is a copyable filter description.

## Separate screens, not cards

Three things deliberately live on their own routes rather than as cards:

| Screen | Why separate |
|---|---|
| **Fact sheet review** | a review queue with its own workflow (import, diff, approve/reject). Card-sized it would be unusable |
| **Saved fixing list** | the cross-card worklist — see [worklists.md](worklists.md) |
| **Structured source-of-truth** (experimental) | a parallel, unfinished system; kept out of the main board on purpose |

The rule I'd state: **a card answers a question; a screen supports a workflow.**
If the thing has its own multi-step state, it's a screen.

One useful piece of chrome for the fact sheet: a **staleness pill** on the card
that grades against it — "fact sheet: N facts, fetched 6 days ago" turning red
past two weeks. Ground truth going stale silently is how an accuracy card starts
lying, and the pill is the cheapest possible guard.
