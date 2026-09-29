# Sample size: one day is not a measurement

Not a bug you can ship — a habit. But it's the question I got asked most, and
the one that decides whether people trust the dashboard or learn to ignore it.

## The problem

The same prompt asked twice on the same day can return different answers.
Models are non-deterministic, indexes update, and answers get regenerated. So
the daily line is noisy **by construction**, and some of every day-to-day move
is nothing at all.

Which means the most common way a dashboard destroys its own credibility is:
someone sees a 6-point drop, investigates, finds nothing, and concludes the
data is unreliable. They're half right — the data is fine, the reading was
wrong.

## What to do about it

**Pool days.** Every answer-derived metric takes a list of snapshots and pools
the underlying answers. Pool numerators and denominators, then divide — never
average the daily percentages, which weights a thin day equally with a full one.

**Establish your own threshold empirically.** Resample your own history: take N
days, compute the metric, repeat with a different N days, and see where the
metric stops moving under resampling. That N is your floor. Mine came out
meaningfully above one day and below two weeks — but it's a property of *your*
prompt-set size and surface count, so measure it rather than copying a number.

**Default the date range to the pooled window**, not to today. The default view
should be the trustworthy one; a single day should require deliberately asking
for it.

**Show sample size everywhere** — per card, per table row. A per-prompt rate
over 7 answers needs the 7 visible next to it.

**Warn on thin slices.** A single-surface filter cuts the sample to roughly a
seventh. Show the warning and the delta against the all-surface baseline, so a
thin number is always read as a comparison.

## Reading a change honestly

| Signal | Reading |
|---|---|
| one day, one prompt, one surface | noise |
| one day, one prompt, all surfaces | worth a look, not a conclusion |
| pooled window, one cluster diverging from the aggregate | real |
| a metric outside its historical range for several consecutive days | real |
| a step change on the day you edited the prompt set | your own change — annotate the chart |

That last row matters more than it looks. Every prompt-set change produces a
step in the data that will be investigated as an event unless you date it and
mark it.

## What pooling doesn't fix

- **A structurally small prompt set.** Five prompts pooled over thirty days is
  still five prompts; you have precision about a narrow instrument.
- **A missing surface.** If a surface silently stops returning answers, pooling
  hides it. That's why per-prompt platform coverage exists as a column in
  [question 3](../01-questions/03-niches.md) — it drops from 7/7 to 6/7
  immediately.
- **A changed prompt.** An edited prompt is a new series. Don't pool across the
  edit.

## The rule

> Measure the pool, not the day.

And when someone asks "why did it drop yesterday", the right first answer is
usually "it didn't — look at the pooled window" followed by checking that no
surface went missing.
