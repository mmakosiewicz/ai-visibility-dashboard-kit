# 3 · The average hides the story

**A stable overall number almost always contains one cluster collapsing and
another improving. The headline is for reporting; every decision comes from the
per-prompt or per-cluster view.**

## The shape of it

Overall mention rate flat for three weeks. Underneath:

```
keyword research    ████████████████████  strong, slightly up
on-page             ███████████████       stable
local SEO           ████                  half what it was
AI visibility       ██                    new entrants taking the space
```

Nothing in the headline moves, because the clusters offset. Two real problems
sit in plain sight, invisible.

## Four places it bites

**Across sub-niches.** The case above. This is why
[question 3](../01-questions/03-niches.md) reports per subgroup and refuses to
average across them: the subgroups have different prompt counts, so a pooled
number is mostly the biggest subgroup wearing a disguise.

**Across surfaces.** Per-surface mention rates spread widely. A pooled number
can hold steady while you lose an entire surface — and if that surface is the
one your buyers use, the pooled number is actively misleading.

**Across prompts within a cluster.** Five prompts, one collapsing, four steady:
the cluster average moves 4%, the collapsed prompt moves 100%. The per-prompt
table is where that shows.

**Across metrics that shouldn't share an axis.** Mention rate and position move
independently — see [position](../04-metrics/position.md). A "visibility score"
that blends them can sit perfectly still while both halves move in opposite
directions. This is the main reason I don't compute a composite score.

## Why averages are seductive here

Because the alternative is a lot of rows, and rows feel like a worse dashboard
than a number. They aren't. The number is for the weekly update; the rows are
the product.

There's also a subtler pull: a per-cluster view makes you responsible for things
you can't fix quickly. A single headline lets everyone feel the situation is
roughly under control. That's precisely the failure mode.

## The fix

- **Per-prompt or per-cluster is the default view.** The aggregate is a
  headline, explicitly labelled as such.
- **Sort worst-first.** Alphabetical sorting reintroduces the problem: the
  collapsing row hides in the middle.
- **Show sample size per row**, so people can tell a real drop from three noisy
  answers.
- **Never average across groups with different prompt counts.** Report them
  side by side.
- **Flag divergence.** If a cluster moves more than the aggregate by some
  margin, say so on the card. That's the one piece of automation worth building
  here — it's the difference between a reader having to scan for the story and
  being handed it.

## The rule

> Report the aggregate. Decide from the rows.

And when someone quotes the aggregate at you as evidence that things are fine,
the per-cluster table is the answer.
