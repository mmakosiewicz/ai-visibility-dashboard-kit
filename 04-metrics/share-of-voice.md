# Share of voice: cohort, field, and weighted

Mention rate answers "are we there at all". It says nothing about how much of
the conversation is ours. Share of voice does — but there are two versions of
it, they can disagree wildly, and picking the wrong one produces a number that
flatters you in exactly the situations where you most need the truth.

## The two denominators

```
cohort_share = our mentions / mentions of brands in OUR TRACKED SET
field_share  = our mentions / mentions of EVERY brand named in the answers
```

**Cohort share** answers: *of the tools we track, how much of the conversation
is ours.* It's comparable to what your competitive-tracking tool reports, and
it's stable because the denominator is a list you control.

**Field share** answers: *of everything AI names, how much is us.* It needs no
maintained list and can't flatter you by omission.

## When cohort share is wrong

In any category where the real incumbents aren't in your tracked set.

I built the adjacent-categories card with cohort share first. In categories
we'd just entered, our tracked competitors barely appeared in the answers — so
the cohort denominator was tiny, and the card reported near-total dominance of
conversations we were essentially absent from. The metric wasn't broken; it was
faithfully measuring our share of a conversation that wasn't happening.

The rule I settled on:

| Question | Use | Why |
|---|---|---|
| Core category (2), niches (3), tasks (4) | **cohort share** | your tracked set *is* the competition; comparable to Brand Radar's own SoV |
| Adjacent categories (8) | **field share** | the real players aren't in your list, and never will be |

And whichever you use, **label it on the card**. "Share of voice 71%" with an
unstated denominator is the single most misleadable number in this entire spec.

## Weighted share

Breadth and prominence are different things:

```
share    = mentions / total mentions                  (breadth)
weighted = sum(1/position) credit, normalised          (prominence)
```

A brand can hold high share and low weighted share: mentioned everywhere,
always last. That gap is the interesting signal, and it's the one metric on my
board that reliably surfaces "we're in every list and nobody reads that far".

`1/position` is a choice, not a law. Alternatives: linear decay, or only
crediting the top 3. `1/position` is steep — first place is worth double second
— which I think matches how people read lists. Whatever you pick, use it
consistently and don't compare weighted shares computed with different decays.

## Compute it per question, never pooled

My first version computed one share of voice across all recommendation
questions. That number was just the largest prompt set wearing a disguise: the
niches question has ~30 prompts against the category question's 5, so a pooled
share is 85% niches by construction.

Three separate share-of-voice reports — category, niche, task — each with its
own cohort ranking and its own trend. No cross-question total. If you want one
number for a deck, use the category one and say so.

## Brand-string normalisation is mandatory

Models write brand names inconsistently: product-line variants, sub-brands,
capitalisation, spacing. Left unnormalised, one competitor splits into four rows
and its share is understated fourfold — which inflates yours.

Map variants onto one cohort member with substring patterns:

```python
COHORT = (
  ("ahrefs",     ("ahrefs",)),
  ("semrush",    ("semrush",)),
  ("moz",        ("moz",)),          # merges "Moz Pro", "Moz Local"
  ("se ranking", ("se ranking", "seranking")),
)
```

Note the two-spelling entry. Spacing variants are the most common failure, and
they're silent.

Also collapse your **own** sub-brands (`<Brand> Webmaster Tools` → `<brand>`) or
you'll undercount yourself — the mirror image of the same bug.

## Reading it honestly

- **Share rising while total mentions fall** is not an improvement. The
  conversation shrank. Always read share next to the absolute count.
- **Share is zero-sum within its denominator.** A competitor's bad week raises
  your share with no action on your part. Don't claim credit for it.
- **Cohort share has a ceiling you chose.** If you track six competitors, your
  cohort share is bounded by a market definition you invented. Field share
  doesn't have that property, which is why it's the better reality check even in
  categories where cohort share is the headline.
