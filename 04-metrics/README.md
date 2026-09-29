# Metrics

Every metric on the board, its formula, and — the part that actually matters —
its **denominator**.

Three of the four mistakes I made in this project were denominator mistakes.
None of them were visible in the chart; all of them produced numbers that moved
for reasons unrelated to our visibility.

**Which prompts may feed which metric** is the other half of the denominator
question and lives in [02-prompts/shapes.md](../02-prompts/shapes.md). Win rate
on a rival-vs-rival prompt, or sentiment on a how-to prompt, computes fine and
means nothing.

## The full set

| Metric | Formula | Denominator | Detail |
|---|---|---|---|
| **Mention rate** | answers naming us ÷ all answers | all answers for those prompts | below |
| **Position** | mean of first-appearance rank | **answers where we're mentioned** | [position.md](position.md) |
| **Top-three rate** | answers ranking us ≤3 ÷ answers mentioning us | answers mentioning us | [position.md](position.md) |
| **Win rate** | wins ÷ (wins + losses) | **answers naming any winner** | [win-rate.md](win-rate.md) |
| **Capture** | answers recommending us ÷ answers recommending any tool | **answers recommending a named tool** | [capture.md](capture.md) |
| **Tool-recommendation rate** | answers naming any tool ÷ all answers | all answers | [capture.md](capture.md) |
| **Cohort share of voice** | our mentions ÷ tracked-cohort mentions | your competitor set | [share-of-voice.md](share-of-voice.md) |
| **Field share** | our mentions ÷ **all** brands' mentions | every brand named | [share-of-voice.md](share-of-voice.md) |
| **Weighted share** | position-discounted credit, normalised | same as its share | [share-of-voice.md](share-of-voice.md) |
| **Citation split** | citations per class ÷ all citations | all citations | [citation-metrics.md](citation-metrics.md) |
| **Coverage** | days with ≥1 citation ÷ days in range | days in range | [citation-metrics.md](citation-metrics.md) |
| **Wrong-claim rate** | contradicted ÷ checkable claims | checkable claims, **split provoked/unprovoked** | [accuracy.md](accuracy.md) |
| **Negative rate** | negative+mixed answers ÷ all answers | all answers for adversarial prompts | [sentiment.md](sentiment.md) |
| **Error share (bots)** | (4xx + 5xx) ÷ all AI-bot requests | all AI-bot requests in window | [operational.md](operational.md) |
| **Stale share** | pages older than 12mo ÷ pages **with a known date** | pages with a known date | [operational.md](operational.md) |

## Mention rate

```
mention_rate = answers where mentioned=true / all answers for these prompts
```

The only metric safe to read as a single number, and the one to start with.
Notes:

- **Include unmentioned answers in the denominator.** Obvious here, easy to get
  wrong when you filter for analysis and forget to restore the full set.
- **It's per prompt-set.** A pooled mention rate across questions is dominated
  by whichever question has the most prompts. Report it per question.
- **Two prompt sets with different sizes can't be compared.** 6 prompts × 7
  surfaces and 30 prompts × 7 surfaces are not the same instrument.

## Three rules that prevent most errors

**1. Conditional metrics need a stated condition.**

Position, top-three rate and sentiment only exist *when you're mentioned*.
Write the condition into the label on screen — "avg position (when mentioned)" —
not just into the code.

**2. Never impute a value for absence.**

The tempting fix for "we're not in this answer" is to score it as last place,
or as the list length, or as zero. All three turn one metric into a blend of two
different things (presence and prominence) that then moves for both reasons.
Two metrics, reported side by side.

**3. Ratios need their denominator on screen.**

Not in a tooltip. A percentage whose base is invisible will be quoted without
its base within a week — I've watched it happen — and then it's in a deck and
it's wrong. Every ratio card on my board carries a caption like *"win rate =
wins / decided comparisons (N of M had a clear verdict)"*.

## Pooling across days

Every answer-derived metric takes a **list of snapshots** and pools them. One
day and thirty days go through the same code path.

Two things to get right:

- **One snapshot per day.** If a day has two successful runs, pick one (the
  last) or that day gets double weight.
- **Pool the underlying answers, not the daily rates.** Averaging daily
  percentages weights a light day the same as a heavy one. Sum numerators and
  denominators, then divide.

## Per-surface metrics

Every answer-derived metric can be filtered to one AI surface, and the spreads
are wide. Two cautions:

- **Single-surface samples are small** — one seventh of the pool. Show a
  sample-size warning; I display the difference from the all-surface baseline so
  a single-surface view is always read as a delta.
- **Operational metrics have no surface dimension.** Crawl health and freshness
  are server-side facts. Leave them unfiltered and say so, rather than showing a
  filtered-looking number that ignored the filter.

## Metrics I deliberately don't compute

- **A single composite "AI visibility score".** It would move for a dozen
  unrelated reasons and be actionable for none. The twelve questions exist
  because they need twelve different responses.
- **Anything averaged across research questions.** Different prompt-set sizes,
  different intent, different meaning.
- **Cross-country or cross-language comparisons.** Different answer populations
  and different competitors; the numbers are not comparable. Keep markets in
  separate instruments.
