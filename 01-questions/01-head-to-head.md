# 1 · Head-to-head: when AI compares us to a competitor, do we win?

## The question

"A prospect asks ChatGPT *us vs Competitor X*. What does it say?"

This is the question Sales asks most, because it's the one they can't answer
from a browser — one person checking one prompt once tells you nothing about
what a thousand prospects see.

## Why it exists

It's the only question whose answer maps directly onto a live deal. A rep in a
competitive cycle wants to know which comparison they're losing, on which
surface, and why — and the "why" has to be a sentence they can respond to, not
a score.

## The prompts

Comparison prompts, one per competitor pair, in both phrasings people actually
type:

```
ahrefs vs semrush
ahrefs or semrush
ahrefs vs moz
ahrefs or moz
ahrefs vs se ranking
ahrefs brand radar vs profound
```

Both `vs` and `or` for each major competitor, because they don't return the
same answers — `or` skews toward a recommendation, `vs` toward a feature table.
Around 10 prompts covering 5–6 competitors is enough; add a pair when a
competitor starts showing up in deals, not when marketing starts worrying about
them.

Include your own product-level comparisons (`our product X vs their product Y`)
where you compete at feature level rather than suite level.

## What gets graded

Per answer, from the LLM pass:

| Field | Meaning |
|---|---|
| `mentioned` | are we named at all (should be ~100% here — we're in the prompt) |
| `position` | 1-based order of first appearance among named brands |
| `verdict_winner` | the single tool the answer overall recommends, lowercase — **`null` when it names none** |
| `sentiment` | toward us, when mentioned |
| `brands` | every brand named, in order |

`verdict_winner` is the field this whole question turns on, and the `null` case
is the majority. See [How it lies](#how-it-lies).

A second, optional extraction — **"recommended for what"** — pulls the *use
case* each tool is recommended for ("Ahrefs for backlinks, Semrush for PPC").
That's the field reps actually want: not "we lost" but "we're framed as the
backlink tool and they're framed as the all-rounder."

## The metric

**Win rate = wins ÷ (wins + losses)**, where a win is an answer whose
`verdict_winner` is us and a loss is an answer naming someone else.

Answers naming no winner are **excluded from the denominator** and reported
separately as `no verdict`. Full reasoning in
[`04-metrics/win-rate.md`](../04-metrics/win-rate.md) — it's the single most
important definition in this repo.

Also track, per prompt: answers, mention rate, the win/loss/no-verdict split
across surfaces, and who you lose to.

## What the card shows

```
headline:  win rate · wins · losses · no verdict
caption:   "win rate = wins / decided comparisons (N of M had a clear verdict)"
           "loses to: <competitor list>"
table:     one row per comparison prompt —
           prompt · answers · mention % · position · winner split · sentiment
drilldown: per-prompt, the per-surface verdict split (never one representative
           answer — see below)
extra:     "recommended for what" — use-case framing per tool
```

The caption isn't decoration. A win rate with an invisible denominator gets
quoted in a deck within a week, and it will be wrong.

## The action

- **Competitor leads a specific comparison** → that's a content brief, not an
  alarm: the comparison page for that pair, addressing the framing the answers
  actually use.
- **A competitor leads almost every day** → not an alert, a strategy problem.
  Don't build an alert for a standing condition; it trains people to ignore
  the channel.
- **Position slipping while win rate holds** → we're being listed later. Usually
  a source problem (question 5), not a positioning problem.
- **A flip** — competitor ahead in recent scans having not been ahead before —
  is the only thing worth an email. Everything else is a dashboard read.

## How it lies

**Most answers don't pick a winner.** In my data, a large majority of comparison
answers name nobody — they list options and hedge. If you divide wins by *all*
answers, your "win rate" mostly measures how diplomatic the models are being
this week, and it'll drift when a model updates its refusal behaviour with no
change in your standing. Denominator = decided answers only.

**One answer is not the verdict.** My first version displayed `winners[0]` —
literally the first row the database returned — as "the winner" for a prompt.
That's neither a majority nor an average; it's an arbitrary surface's opinion
presented as fact. Show the split across all surfaces (`3 us / 2 them / 2 no
verdict`) or a genuine mode, never a single sampled row.

**`vs` and `or` are different prompts.** Averaging them hides that one phrasing
consistently loses. Keep them as separate rows.

**Winner ≠ sentiment.** An answer can recommend a competitor while describing
you positively, and the reverse. Two fields, two meanings; don't collapse them.
