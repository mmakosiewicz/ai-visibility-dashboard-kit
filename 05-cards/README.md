# Card anatomy

The design knowledge nobody writes down, and the difference between "I have
metrics" and "I have a dashboard someone uses".

One card per research question. Every card has the same four-layer structure,
and the fourth layer is the one that makes the difference.

## The four layers

```
┌────────────────────────────────────────────────────────────────┐
│ 1  HEADLINE     3–6 numbers, one of them the metric that       │
│                 matters. Plus a trend sparkline.               │
│                 Answers: how are we doing?                     │
├────────────────────────────────────────────────────────────────┤
│ 2  CAPTION      one sentence defining the headline metric,     │
│                 with its denominator spelled out.              │
│                 Answers: what does that number mean?           │
├────────────────────────────────────────────────────────────────┤
│ 3  WORKLIST     a table, one row per prompt / page / error.    │
│                 Sorted worst-first.                            │
│                 Answers: where is the problem?                 │
├────────────────────────────────────────────────────────────────┤
│ 4  DRILLDOWN    per row, the evidence — the actual answers,    │
│                 the quotes, the sources, the per-surface split.│
│                 Answers: what do I do about it?                │
└────────────────────────────────────────────────────────────────┘
```

Miss layer 3 and you have a report. Miss layer 4 and nobody trusts layer 3
enough to act on it.

## Layer 1 — headline

- **3 to 6 numbers.** Fewer and the card feels thin; more and none of them are
  read.
- **One is primary** and visually dominant (mine: ~30px, the rest ~18px). If you
  can't say which number is primary, the card doesn't know what it's for.
- **Counts next to rates.** "58% (362 of 1,202)". A rate alone invites
  over-reading a tiny sample.
- **A sparkline, not a chart.** Direction over ~30 days, with the current value
  and the delta. A full chart here competes with the worklist for attention.
- **Delta against a baseline** when a filter is active — showing "48% (−7 vs all
  surfaces)" is what makes a filtered view interpretable.

## Layer 2 — caption

One sentence. Its whole job is to make the headline unquotable-out-of-context:

> win rate = wins / decided comparisons (362 of 1,202 had a clear verdict)

> N of M answers recommended a named tool; K of those included us.
> Process-only answers are not counted as losses.

I resisted these as clutter at first. They're the highest-value text on the
board, because a percentage with an invisible denominator *will* end up in a
deck without its denominator.

## Layer 3 — worklist

The table that turns the card into a tool.

- **One row per actionable unit** — prompt, page, error, theme. Not per answer.
- **Sorted worst-first by default.** Alphabetical sorting is a small betrayal:
  it makes the reader do the ranking you should have done.
- **Include the sample size per row.** Per-prompt numbers over 7 answers are
  noisy, and the row count is the honest warning.
- **Show splits, not single sampled values.** `3 us / 2 them / 2 none`, never
  one arbitrary surface's verdict presented as the answer. This was a real bug
  of mine — see [win rate](../04-metrics/win-rate.md#never-display-one-answer-as-the-winner).
- **Demand data if you have it.** Search volume next to a prompt converts a list
  of problems into a prioritised list.

## Layer 4 — drilldown

Collapsed by default, one click. Contains the evidence:

- the actual answer text, per surface
- verbatim quotes (for narrative themes)
- the cited sources for those answers
- the per-surface breakdown of whatever the row aggregates
- a link out to the source tool for manual verification

Two implementation notes that cost me bug reports:

- **Preserve open/closed state across re-renders.** My board re-renders when any
  panel finishes loading; blindly rewriting the container snapped every open
  drilldown shut a few seconds after the user clicked it. Track open rows and
  restore.
- **Link out generously.** A deep link to the source report is what lets someone
  verify a number they don't believe. That's not a failure of the dashboard —
  it's how it earns trust.

## Every card ends in an action

Not decoration. A small block that says what to do when this number is bad, and
a way to record the decision. Mine has a "save to fixing list" button on
worklist rows; the shortlist is a page someone works through.

The test for any card: **if this number is bad, what happens next?** If you
can't answer in one sentence, cut the card. A dashboard of unactionable metrics
is a reporting obligation that gradually stops being opened.

## Card titles: plain English, tag the internals

```
"Fact accuracy"                                     ← plain
"Is what AI says about features & pricing true?"    ← the question
"RQ6"                                               ← small grey tag
```

Question numbers are useful for cross-referencing a writeup and terrible as
titles. Lead with a human title, keep the identifier as a small grey tag.

## Typography, minimally

One type scale, nothing below 11px. My original board had 117 instances of
9–10px text — technically legible, actually skipped. And one brand, one colour,
everywhere: if a competitor is orange in the share-of-voice table, it's orange
in the citation table too.

## Layout order

Not by question number (mine renders 1→11 because that's build order, which is
a mistake I kept). Group by what the reader is doing:

1. **Am I there?** — presence cards
2. **Do I win when I'm there?** — competitive cards
3. **Is what's said about me right?** — accuracy and narrative
4. **Why?** — sources, tracked pages
5. **Is anything structurally broken?** — operational gates

Groups 1–2 are for reporting; 3–4 generate the work; 5 is what you check first
when something makes no sense.

## See also

- [`scope.md`](scope.md) — global filters, and which cards must ignore them
- [`worklists.md`](worklists.md) — turning findings into a queue someone works
- [`board-chrome.md`](board-chrome.md) — the KPI history strip, the status line,
  the Actions block, and which things should be screens instead of cards
