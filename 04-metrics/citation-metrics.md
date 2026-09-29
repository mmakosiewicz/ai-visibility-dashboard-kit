# Citation metrics

Computed from the cited-source lists attached to answers. No LLM, which makes
these the cheapest metrics on the board — and the ones most often ranked wrongly.

Used by [question 5](../01-questions/05-source-influence.md),
[question 11](../01-questions/11-tracked-pages.md) and
[question 12](../01-questions/12-citation-attention.md).

## Citation split

```
split[class] = citations from that class / all citations
classes: owned | competitor | ugc | third_party
```

Classification is by **host**, against lists you maintain (your domains, your
competitors' domains, known UGC/forum/review domains), with everything else
falling to `third_party`.

Two rules:

- **Match on host, not path.** `LIKE '%blog/brand-pricing%'` will also match
  four other companies' pages at the same path and pool them into what looks
  like yours. This cost me a wrong conclusion in a published draft — see
  [`07-gotchas/page-next-to-a-claim.md`](../07-gotchas/page-next-to-a-claim.md).
- **Normalise for grouping, keep the original for linking.** Strip scheme,
  `www.`, query and fragment, and the trailing slash. Keep the raw URL so the
  table's links actually work.

Read owned share **next to total citations**. If owned share rises because the
models cite fewer sources overall, your reach hasn't improved.

## Ranking pages: use answers, not appearances

The wrong ranking is raw citation count. Three progressively better ones:

```
1. appearances        — every time the URL appears in any source list   ✗
2. distinct answers   — one credit per (page, answer)                   ✓
3. + days seen        — as a tie-breaker for persistence                ✓✓
```

Why: a page cited five times inside one answer isn't five times as influential
as a page cited once. And a page cited heavily on a single day is a weaker
result than one cited steadily for a month — the second is structurally embedded
in how that question gets answered.

So: rank by distinct answers, break ties by days seen, and display both.

One naming caution: if your source's link list is a *source list* rather than a
confirmed-citation list (some surfaces mark whether a link was actually cited;
at least one provides no status at all), then what you're ranking is **source
appearances** — attention, not confirmed citation. Two different claims. Expose
the confirmed / unconfirmed / unknown split instead of implying precision you
don't have.

## The ranking trap: citations are not mentions

**The single most important thing in this file.** A page being cited in answers
about your category does not mean the page mentions your brand. In my data a
large share of cited pages never mention us at all — and in adjacent categories
it's nearly all of them.

Consequences if you rank a worklist by citations alone:

- outreach lists full of pages with no hook for you
- "did they remove us" monitoring on pages you were never in — an alert that
  can never fire
- an inflated sense of how much of the conversation you're part of

**Verify mentions per page** against real brand data from your source, then rank.
Full treatment:
[`07-gotchas/citations-are-not-mentions.md`](../07-gotchas/citations-are-not-mentions.md).

And when you do verify, respect the three-state answer: a brand list, an empty
list (looked, found none), and **no data** (didn't look). Collapsing the last
two is its own bug —
[`07-gotchas/null-is-not-empty.md`](../07-gotchas/null-is-not-empty.md).

## Mention rate on citations

For a specific page (question 11):

```
cites        = answers citing this page
with_mention = those answers that ALSO name our brand
mention_rate_on_citations = with_mention / cites
```

A page cited often while your brand goes unnamed is a weaker outcome than the
citation count suggests: the source was used, the brand didn't land. Usually it
means your brand sits in a part of the page the answer isn't drawing from.

## Coverage and drops

```
coverage_pct = days with >= 1 citation / days in range
drops        = day-to-day transitions from cited -> not cited
```

Coverage answers "is this page reliably used". Drops explain why coverage isn't
100%.

Caveats:

- **Needs a real range.** Over 2 days it's noise; over 30 it's informative.
  Refuse to render below a minimum and say why.
- **Coverage without volume misleads.** A page cited once on each of 14 days has
  100% coverage and negligible influence. Show citations alongside.
- **Computed from stored snapshots only** — so it works retroactively over your
  whole history and costs no API calls. That's a direct payoff of storing
  answers rather than scores.

## Per-surface citation data is uneven

Surfaces differ enormously in how many sources they return — some give rich
lists on nearly every answer, others rarely provide any. So:

- A pooled domain ranking is weighted toward the most citation-heavy surface.
- Filtering by surface reshuffles the entire table. That's real, not a bug.
- Don't compare citation *counts* across surfaces as if they measured the same
  thing.

State the coverage skew on the card if you can; it stops the "why is Perplexity
missing from this table" question before it's asked.

## Normalising URLs

Pool `/x` and `/x/`, `http` and `https`, `www.` and bare host. **Do not drop the
whole query string**: `youtube.com/watch?v=…` is one page per video, and
dropping `?v=` merged every video into a single "page" with hundreds of answers
on one board. Keep identifying parameters, drop tracking ones (`utm_*`,
`srsltid`, `gclid`, `fbclid`, `authuser`, `ref`).
