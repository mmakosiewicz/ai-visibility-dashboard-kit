# Sentiment and narrative metrics

Powers [question 7](../01-questions/07-narrative-risk.md). The least
metric-shaped card on the board — its real output is quotes, not numbers.

## Definitions

```
sentiment ∈ {positive, neutral, mixed, negative, null}   -- toward us, per answer
negative_rate = answers with sentiment in (negative, mixed) / all answers
```

`null` when we aren't mentioned — sentiment is conditional on presence, like
[position](position.md).

## Counting `mixed` as negative

A choice, and I'd defend it: a "mixed" answer about a paid product is an answer
containing an objection, and objection-handling is what this card feeds.

But it's a choice, so:

- **Write it on the card.** "negative rate (negative + mixed)".
- **Also show the full composition** — positive / neutral / mixed / negative as
  shares. Composition shifts are more informative than the single rate: mixed
  rising while negative falls is a real improvement that the headline hides.

## The rate is high by construction

These prompts are adversarial on purpose (`<brand> bad reviews`, `is <brand>
worth it`). So the negative rate is not "how negative is AI about us" — it's
**"how negative does AI get when the user is already sceptical"**, which is the
case worth knowing.

Two consequences:

- **Never compare it to a neutral prompt set's sentiment.** Different
  instrument, different population.
- **Report it with the prompt set visible.** Out of context it reads as a crisis.

## Themes: frequency, then normalisation

```
theme_count[t] = answers whose negative_themes include t
```

Models phrase the same criticism differently across a week — "expensive",
"pricey", "costs more than competitors" — splitting one theme into three rows
and hiding the real frequency.

Minimum viable handling:

- lowercase everything before counting
- review the theme list periodically; the long tail is usually the same handful
  of complaints rewritten
- consider mapping to a small fixed taxonomy of known objections, with an
  "other" bucket you actually read

Don't over-engineer this. The theme count is a router; the quotes are the payload.

## Quotes must be verified verbatim

Ask a model for verbatim quotes and it will sometimes paraphrase. That's fatal
here, because these quotes go into enablement material: one invented quote
destroys trust in the whole card.

So verify programmatically — keep only quotes that appear in the answer text
under normalisation (unify curly quotes, en/em dashes, collapse whitespace,
lowercase), and silently drop the rest.

```python
def verify_quotes(quotes, answer_text):
    norm = normalise(answer_text)
    return [q for q in quotes if normalise(q) in norm][:4]
```

Cap the count and the length — four quotes of ~25 words each is plenty, and long
"quotes" are usually reconstructions.

## Narrative sources

The metric that makes this card actionable rather than merely discouraging:

```
for answers in this question:
  citation split by class (owned / competitor / ugc / other)
  pages ranked by appearances in NEGATIVE answers, not total citations
```

That ranking separates criticism the models generate from criticism they're
reading off a specific page. A UGC thread or a competitor's comparison page
appearing repeatedly in negative answers is a concrete target; a theme with no
source concentration is a positioning problem instead.

Rank by `in_negative` first, `citations` second. Ranking by total citations
surfaces the category's biggest pages, which tells you nothing about narrative.

## Reading it honestly

- **A criticism isn't a finding until it repeats.** One negative answer on one
  surface on one day is noise. Wait for the theme across surfaces.
- **Sentiment is per-answer, not per-mention.** An answer can praise you in one
  sentence and criticise you in the next; that's what `mixed` is for.
- **True criticisms belong to enablement, false ones to
  [question 6](../01-questions/06-fact-fidelity.md).** Sorting each theme into
  one of those two buckets is the actual work this card produces.
- **Don't chase the rate down.** The goal isn't a lower negative rate on
  adversarial prompts — it's knowing which objection arrives before the call.
