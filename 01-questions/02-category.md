# 2 · Category: are we on the "best in category" list — and where?

## The question

"Someone asks for the best tools in our category. Are we in the list, and how
early?"

## Why it exists

This is the baseline. It's the number you report monthly, the one that belongs
in a board deck, and the one every other question is measured against. It's also
the highest-intent surface you have: a category list is a shortlist, and
shortlists decide who gets evaluated.

## The prompts

Broad, category-level, no brand in the prompt:

```
best seo tools
top seo software
seo tools comparison
free seo tools
alternatives to <biggest competitor>
```

Five is enough, and deliberately so — this is a small, stable set you'll compare
across months. Two design notes:

- **`free ...` earns its own prompt.** Free-tier lists are a different
  population, and if you have a free tier being absent there is a specific,
  fixable gap.
- **`alternatives to <competitor>` belongs here**, not with head-to-head. It's a
  list prompt, not a comparison, and it's one of the highest-intent prompts in
  the entire set: the asker has already decided to leave.

Resist growing this set. Category coverage is the thing you want a long stable
history for.

## What gets graded

`mentioned`, `position`, `total_brands`, `brands` (ordered), `sentiment`.

`total_brands` matters more than it looks: position 4 of 5 and position 4 of 20
are not the same result, and the list length moves over time.

## The metric

**Mention rate = answers naming us ÷ all answers for these prompts.** The one
metric that's safe to read as a single number.

**Average position**, computed *only over answers where we're mentioned*. Never
impute a value for absence — see
[`04-metrics/position.md`](../04-metrics/position.md).

Pair it with **share of voice** across your tracked competitor set, which
answers a different question: not "are we there" but "how much of the
conversation is ours". Two flavours worth keeping apart —

- **share** = our mentions ÷ all cohort mentions (breadth)
- **weighted share** = position-discounted credit, normalised (prominence)

A brand with high share and low weighted share is mentioned everywhere and
always last. That gap is the signal.

## What the card shows

```
headline:  mention rate · avg position · answers
table:     per prompt — prompt · search volume · mention % · position ·
           avg brands named · sentiment
extra 1:   search demand for the prompt (is this a prompt anyone types?)
extra 2:   share of voice — cohort table, share vs weighted share
drilldown: which brands appear ahead of us, per prompt
```

Search volume alongside each prompt is worth the effort. It separates "we're
absent from a prompt nobody asks" from "we're absent from the one everybody
asks", and that's a prioritisation input you otherwise have to guess.

## The action

- **Absent from a high-volume category prompt** → the strongest possible
  content signal. Check question 5 for which sources feed that prompt; the fix
  is usually getting into *those*, not publishing another page of your own.
- **Present but late** → prominence work: being listed first in the third-party
  roundups that feed the answers.
- **Mention rate stable, position drifting** → new entrants are being inserted
  ahead of you. Check `total_brands` for list inflation before concluding you
  slipped.

## How it lies

**Cohort share flatters you.** If share of voice is computed over *your tracked
competitor set*, it tells you "of the tools we track, how much is ours" — and
in any category where the real incumbents aren't in your tracked set, that
number can read near-100% while you're effectively absent. Either scope it to
the whole field of brands actually named, or label it explicitly as cohort
share. (For adjacent categories, use field share — see
[question 8](08-adjacent-categories.md).)

**A five-prompt set is volatile.** One prompt flipping moves the headline by
20%. Pool several days before reading a change as a change; see
[`07-gotchas/sample-size.md`](../07-gotchas/sample-size.md).

**"Best" prompts aren't the only category prompts.** `seo tools comparison`
behaves differently from `best seo tools` — comparison phrasings pull tables
and tend to name more brands. Keep them separate rather than assuming they
measure the same thing.
