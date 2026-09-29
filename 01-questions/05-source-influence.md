# 5 · Source influence: whose content does AI cite?

## The question

"When AI answers about our category, whose pages is it reading?"

## Why it exists

Every other question tells you *what* the answer said. This one tells you *why*
— and it's the only question on the board whose findings generate outreach work
rather than content work. If a third-party roundup is cited in a third of the
answers about your category, your visibility in that category is substantially
a function of one page you don't control.

It's also the diagnostic you check first when a number drops with no obvious
cause.

## The prompts

None of its own. This question is computed from the **cited-source lists
attached to every answer** the other questions already pulled. That's what makes
it cheap — no extra prompts, no LLM pass.

## What gets graded

Nothing by an LLM. You need, per answer, the list of cited sources with `url`
and `title`, stored as-is. Then classify each domain:

| Class | Rule |
|---|---|
| `owned` | your domains |
| `competitor` | your tracked competitors' domains |
| `ugc` | Reddit, Quora, HN, forums, review sites |
| `third_party` | everything else — where the interesting work is |

Keep the raw URL list. The classification is derived and will change as you
refine it; the citation list is the fact.

Two storage notes that cost me time:

- **Normalise URLs for grouping** (strip scheme, `www.`, query, fragment,
  trailing slash) but keep the original for linking.
- **Match on host, not path.** `/blog/<brand>-pricing` exists on many domains;
  a `LIKE '%blog/brand-pricing%'` match pools four other companies' pages into
  what looks like yours. See
  [`07-gotchas/page-next-to-a-claim.md`](../07-gotchas/page-next-to-a-claim.md).

## The metric

**Citation split** — owned / competitor / third-party / UGC as a share of all
citations.

Plus a ranked **domain table** and a ranked **page table**. Rank by number of
distinct answers the page appears in, not raw appearances, and use days-seen as
a tie-breaker so a page cited once in fifty answers on one day doesn't outrank
a page cited steadily for a month.

Track owned share over time as the headline — but see the caution below about
reading it as a goal.

## What the card shows

```
headline:  owned % · competitor % · third-party %  (+ total citations)
table 1:   top domains by citations, classified
table 2:   top pages — url · class · citations · answers · days seen ·
           does the page mention us
drilldown: per page, which prompts and surfaces cite it
```

The "does the page mention us" column is the one that makes the table
actionable, and it needs to come from real brand data per page — not inferred
from citation counts. See [How it lies](#how-it-lies).

## The action

- **A third-party page cited heavily that mentions you** → outreach. Highest-
  value work this card produces: you're already in it, so the ask is an update
  or a correction, not an introduction.
- **A third-party page cited heavily that doesn't mention you** → a harder,
  slower pitch. Worth a list, but not the same priority.
- **A competitor page cited heavily** → counter-content, not outreach. You will
  not get them to add you.
- **Owned share very low in a specific subgroup** → your content isn't being
  used as a source there. Usually a format problem (their page is a comparison
  table, yours is a feature page).

## How it lies

**Citations are not mentions.** This is the big one, and it has its own file:
[`07-gotchas/citations-are-not-mentions.md`](../07-gotchas/citations-are-not-mentions.md).
A large share of pages cited in answers about your category never mention your
brand at all. Rank a worklist by citation volume and you'll fill it with pages
that have no hook for you — and any "did they remove us" monitoring built on
that list can never fire, because you were never in them.

**Rising owned share is not automatically good.** If AI cites you more because
it cites *fewer sources overall*, your reach hasn't improved. Read owned share
next to total citations.

**Source lists differ per surface.** Some surfaces return rich citation lists,
some return few, one returns almost none. A domain ranking pooled across
surfaces is therefore weighted toward the chattiest surface. If you filter by
surface, expect the whole table to reshuffle — that's real, not a bug.

**This card is scoped to one prompt group.** For the cross-question view — every
page ranked across all groups, which is how you find the pages worth tracking in
the first place — see [question 12](12-citation-attention.md).

**Inline citations may be stripped.** If your data source strips markdown
citation links out of the answer text, you lose the ability to tell *which
claim* a source backed. Worth storing the raw answer text separately if your
source offers it, because "which page is next to the wrong pricing claim" is a
much stronger question than "which page is cited somewhere in this answer".
