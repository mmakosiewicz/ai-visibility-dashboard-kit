# 8 · Adjacent categories: do we show up at all?

## The question

"We've expanded into a new category. When AI answers about it, are we in the
conversation — or invisible?"

## Why it exists

Expansion areas behave nothing like your core category, and measuring them with
core-category metrics produces confidently wrong numbers. This card exists to
keep a separate, honest scoreboard for the places you're new — where the answer
is usually "no, and here's who owns it instead".

It's also the card most likely to tell you something uncomfortable and true.

## The prompts

Small sets per adjacent category — 2–3 prompts each is enough to establish
presence or absence:

```
social media                best social media tools ·
                            social media management tools ·
                            social media analytics software

competitive intelligence    best competitive intelligence tools ·
                            competitor analysis software
```

Keep these as their own subgroups, never merged into
[question 3](03-niches.md). Niches are areas you sell into; adjacent categories
are areas you've *entered*. Different expectations, different reading.

## What gets graded

Same fields as questions 2 and 3. The difference is entirely in the metric.

## The metric

**Field share**, not cohort share:

> our mentions ÷ mentions of *every* brand named in these answers

This is the whole point of the card. In an adjacent category, your tracked
competitor set barely appears — the real players are that category's incumbents,
who were never in your competitor list. A cohort share computed over your
tracked set would read near-100% while you are genuinely absent, because it's
measuring your share of a conversation that isn't happening.

Field share needs no maintained list and can't flatter you by omission.

Report alongside it: **field rank** (where you place among all brands named),
**number of distinct brands** in the field, and the **top brands table** — which
doubles as competitive research you didn't have to commission.

Standard mention rate and position still apply, and in this card mention rate is
usually the headline, because the honest answer is often a single-digit
percentage.

## What the card shows

```
headline:  overall mention rate · field share · field rank · brands in field
table:     one row per adjacent category — category · prompts · mention % ·
           field share · rank · top 3 brands ahead of us
drilldown: per category, the full field ranking and the per-prompt table
```

The "brands ahead of us" column is the useful one. It tells you who the models
consider the category, which is frequently not who your product marketing
considers the competition.

## The action

- **Zero or near-zero mention** → this is a demand-generation question, not an
  AI-visibility one. No amount of prompt-level optimisation fixes not being
  known in a category.
- **Mentioned but ranked far down a long field** → you're in the consideration
  set. Now the standard plays apply (sources, comparison content).
- **A field with few brands and you're absent** → the best opportunity on the
  board: a small field means the category is unformed and cheap to enter.
- **Persistently absent with no product depth** → say so out loud. Better to
  retire the subgroup than to let it drag a headline Sales reads as performance.

## How it lies

**Cohort share will tell you you're winning.** This is the single reason the
card exists as a separate question. I built it with cohort share first and it
reported near-total dominance of a category where we had no product presence at
all. If you take one thing from this file: in adjacent categories, measure
against the whole field.

**Small prompt sets are volatile.** Two or three prompts means one flip moves
the number hugely. Read the direction over weeks, not the value on a day.

**Absence here is often correct.** If you just launched in a category, being
absent from AI answers is the expected state, not a failure. Track it to see
movement, not to grade the team.

**Citation data is nearly useless in these categories.** The pages cited are
that category's incumbents' pages, almost none of which mention you — so a
citation-based worklist produces nothing actionable. This is the clearest live
example of [citations ≠ mentions](../07-gotchas/citations-are-not-mentions.md).
