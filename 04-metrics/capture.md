# Capture and tool-recommendation rate

The denominator lesson from [win rate](win-rate.md), one level up. These two
metrics power [question 4](../01-questions/04-task-recommendations.md).

## Definitions

```
tool_answers    = answers where tool_recommended = true
our_answers     = tool_answers that also name us

capture                  = our_answers / tool_answers
tool_recommendation_rate = tool_answers / all answers
```

**Capture**'s denominator is answers where a recommendation actually happened.
**Tool-recommendation rate**'s denominator is everything — it measures how often
a tool gets named at all.

## Why process-only answers are excluded from capture

Ask "how do I do keyword research" and a large share of answers explain the
*process* and never name a product. Those answers aren't losses. Nobody beat
you; there was no contest.

Count them against you and:

- **you look defeated where you weren't competing** — the metric reads as a
  competitive loss when it's an absence of competition
- **the number tracks model verbosity** — as models get more or less
  tool-happy, your "capture" moves with no change in your standing
- **you can't prioritise** — the whole point of this question is separating
  "a competitor is winning this task" from "nobody is claiming this task", and a
  pooled denominator erases exactly that distinction

I shipped it with the wrong denominator first. The number was uninformative
until the two were split, and then it immediately produced a worklist.

## Tool-recommendation rate is a finding, not a supporting stat

The gap between this rate and 100% is **the size of the uncontested surface** —
the share of task answers where no vendor is named at all. That's usually the
biggest and cheapest opportunity on the board, and it's invisible unless you
compute it deliberately.

Report both, always, in this order:

```
capture 55%  ·  answers recommending a tool 40%  ·  overall mention 26%
caption: "N of M answers recommended a named tool; K of those included us.
          Process-only answers are not counted as losses."
```

(Illustrative numbers throughout this repo — every figure belongs to whoever
runs the measurement.)

## Grading `tool_recommended` is the hard part

This field is a judgement call and needs its own instruction with edge cases
spelled out. Mine:

> true only if the answer tells or suggests the reader to use a NAMED product,
> service, platform, app, extension, or software tool for the task; passing
> mentions and generic unnamed tools are false; free/default tools such as
> Search Console count

Decisions embedded there, each of which changes the number materially:

| Case | Counts? | Why |
|---|---|---|
| "Use Search Console to check indexing" | **yes** | a named tool is a named tool; excluding free first-party tools flatters you |
| "Use a crawler" | no | category noun, not a product |
| "Tools like X exist" | no | passing mention, not a recommendation |
| "You could use X or Y" | yes | a recommendation with options |
| "X is popular for this" | yes, arguably | borderline — decide and document |

Two implementation notes:

- **Version-stamp the field** (`tool_eval_version`). When you tighten the
  definition — you will — that column lets you re-grade only stale rows instead
  of all of history. I had to backfill once.
- **Store `tool_names`.** "Which tools get recommended instead of us" is the
  drilldown that turns this card into a content brief, and it's free once you
  have the field.

## Capture vs mention rate

They answer different questions and both belong on the card:

- **mention rate** — how often we're named at all in task answers, including in
  passing ("Ahrefs also does this")
- **capture** — how often, *when a tool is recommended*, we're one of them

Capture is usually much higher than mention rate, and the gap is instructive: it
means we're recommended when recommendations happen, but often not present in
the answer otherwise.
