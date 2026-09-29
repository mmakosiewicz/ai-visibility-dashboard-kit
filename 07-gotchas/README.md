# Four ways these numbers will mislead you

Each of these produced a wrong conclusion in my build before I caught it. Two
of them I caught only because someone challenged a number that looked fine.

| | Trap | One-line version |
|---|---|---|
| 1 | [Citations are not mentions](citations-are-not-mentions.md) | the pages AI cites about your category mostly don't mention you |
| 2 | [`null` is not `[]`](null-is-not-empty.md) | "no data" and "no mention" are different answers |
| 3 | [The average hides the story](averages-hide.md) | a stable headline usually contains one cluster collapsing |
| 4 | [A page next to a claim is a lead, not a verdict](page-next-to-a-claim.md) | that page is often the one *correcting* the error |

## What they have in common

Three of the four are the same failure in different clothing: **a number that
looks like a measurement of the world but is partly a measurement of your own
method.**

- Rank by citations and you're measuring your source's index, not your presence.
- Collapse `null` into `[]` and you're measuring your data coverage, not reality.
- Average across clusters and you're measuring your prompt-set composition.
- Match URLs by path and you're measuring four companies at once.

The defence is the same in each case: **state the denominator, keep "unknown" as
its own value, and never let a derived number stand in for the thing it was
derived from.**

## A fifth, which isn't a trap but a discipline

**Sample size.** One day of answers is not a measurement — see
[sample-size.md](sample-size.md). The same prompt asked twice in a day can give
different answers, so the daily line is noisy by construction. Pool days before
reading a change as a change.

I'm keeping it separate from the four because it's not a bug you can ship; it's
a habit you either have or don't.
