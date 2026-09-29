# Win rate

The most-quoted metric on the board and the easiest one to define wrongly. If
you read one metric file, read this one — the same mistake recurs in
[capture](capture.md) and in any "how often do we win X" metric you invent later.

## Definition

```
wins   = answers whose verdict_winner is us
losses = answers whose verdict_winner is some other named brand
none   = answers naming no winner at all

win_rate = wins / (wins + losses)
```

The denominator is **decided answers only**. Answers that name no winner are
excluded and reported as their own number.

## Which answers are eligible at all

Only answers where **you are in the comparison**. Two rules, pick one and put it
in the caption (details in [02-prompts/shapes.md](../02-prompts/shapes.md)):

- **per prompt** — only prompts that name you. Right when your comparisons are
  branded (`ahrefs vs semrush`).
- **per answer** — any decided verdict, excluding prompts that pit two rivals
  against each other. Right when no prompt names you (the payments example).

Counting a rival's win on "is Moz better than Semrush?" as your loss moved one
board's win rate from 69% to 39%.

## Why not wins ÷ all answers

Because most comparison answers don't pick a winner. They list both tools,
describe strengths, and conclude with something like "it depends on your needs".
In my data that's the clear majority of comparison answers.

So if your denominator is all answers:

- **You're mostly measuring model hedging.** The metric is dominated by how
  often models decline to commit, which has nothing to do with your standing.
- **It moves when model behaviour changes.** A model update that makes answers
  more even-handed drops your "win rate" while your actual position is
  unchanged. You will investigate this as a real event. It isn't one.
- **It's not comparable across surfaces.** Surfaces differ a lot in how
  willingly they name a winner, so a per-surface comparison becomes a ranking of
  decisiveness.
- **It understates you.** A number like 20% reads as "we lose 80% of
  comparisons", when the truth might be that we win most of the ones that were
  actually decided.

The decided-only denominator answers the real question — *when AI does pick,
how often does it pick us* — and the `none` count is itself a finding: the share
of comparison traffic where nobody wins is the size of the uncontested surface.

## Report all four numbers

Never the rate alone:

```
win rate 58%   ·   wins 210   ·   losses 152   ·   no verdict 840
caption: "win rate = wins / decided comparisons (362 of 1,202 had a clear verdict)"
```

(Made-up numbers — the shape is the point.) The caption is not optional. A
percentage with an invisible base gets quoted without its base.

## Extracting the winner

The field is `verdict_winner`: the single tool the answer *overall* recommends,
lowercase, or `null`. Two instruction notes that matter:

- **Be explicit that null is expected and correct.** Left implicit, models will
  pick a winner to be helpful, and your "decided" population inflates with
  fabricated verdicts.
- **"Overall" is the operative word.** An answer can say "X is better for
  enterprise" mid-paragraph and still not recommend X overall. You want the
  answer's conclusion, not its strongest local claim.

Normalise brand strings when counting (`Moz Pro`, `Moz Local` → `moz`), or one
competitor splits across rows and its win count is understated.

## Never display one answer as "the winner"

My first version showed `winners[0]` — literally the first database row — as the
winner for each comparison prompt. That's not a majority or an average; it's one
arbitrary surface's opinion presented as the verdict, and it made the whole
table unreliable.

Show either the **split** (`3 us / 2 them / 2 no verdict`) or a genuine **mode**
across the pooled answers. The split is better: it shows disagreement between
surfaces, which is real and interesting.

## Per-prompt, always

An overall win rate hides that you lose one specific comparison consistently.
The per-prompt table with its win/loss/none split is where the work comes from;
the headline is for reporting.

## What counts as a "win" is a choice

Worth deciding explicitly and writing down:

- An answer recommending you **plus** a competitor for different use cases — my
  extractor resolves to one overall winner, which loses that nuance. The
  "recommended for what" extraction (see
  [question 1](../01-questions/01-head-to-head.md)) exists to recover it.
- An answer recommending your **cheaper tier** while praising a competitor's
  suite. Still a win by this definition. Reasonable people would disagree.
- An answer recommending a tool you don't consider a competitor. A loss. Also
  a useful signal about who the models think the market is.

The definition matters less than stating it on the card.
