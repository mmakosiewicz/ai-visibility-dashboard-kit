# 12 · Citation attention: which pages keep coming up, across everything?

> **Status: experimental.** This one is labelled as such on my own board, and I'd
> build it last. It's included because the question it answers — "what are the
> pages that matter across *all* of this, regardless of which prompt group they
> came from" — is the one people ask once they've used the other eleven for a
> few weeks.

## The question

Questions 5 and 11 are both scoped: question 5 splits citations by class within
a prompt group, question 11 tracks a list of pages you chose in advance. Neither
answers "across every prompt we track, which pages does AI keep returning to,
and are they ours?"

## Why it exists

It's the discovery counterpart to question 11's watchlist. Question 11 tells you
how your chosen pages are doing; this tells you **which pages you should have
chosen**. Everything on my tracked-page list after the first month came out of
this card.

It's also the card that reveals the long tail: pooled across all prompt groups,
the same handful of third-party pages recur far more than any single card would
show.

## The data source

The citation lists already stored with every answer — pooled across **all**
research questions, not per question. No LLM. Page metadata (DR, traffic,
publish date) enriched from your source's index; brand-per-page data fetched on
demand when a row is expanded.

## What gets computed

The ranking unit is the crucial decision:

```
source appearance = one credit per (page, answer)
                    repeated links to the same page inside one answer count ONCE
rank              = source appearances DESC, then days seen DESC
```

Per row: the page, its class (ours / competitor / UGC / other), source
appearances, days seen, DR, UR, traffic, publish date, and — loaded when
expanded — the exact citation total from your source's own index plus which
brands the page mentions.

## What the card shows

```
headline:  cited pages · source appearances · days in range · page N of M
tabs:      all · ours · competitors · UGC          (page class)
tabs:      all brands · <your brand> · <each competitor>   (which brand the page mentions)
table:     100 rows per page, ranked globally within the active filter
drilldown: per page — prompt-level reach, and per-surface attention signals
action:    add to the fixing list
```

Two design choices worth copying:

- **Paginate, don't truncate.** Every page in the range is reachable, ranked
  globally within the filter. A "top 20" view hides exactly the long tail this
  card exists to expose.
- **Two independent filter rows.** Page *class* (who owns it) and page *brand*
  (who it mentions) are different questions, and the interesting cell is the
  intersection: third-party pages that mention a competitor but not you.

## The action

- **High-attention page that mentions you** → outreach, top of the queue.
- **High-attention page that mentions a competitor and not you** → the gap list.
  This is the single most useful output of the card.
- **High-attention page of your own** → protect it: keep it fresh
  ([question 10](10-citation-freshness.md)), and check its facts
  ([question 6](06-fact-fidelity.md)).
- **Anything persistently high here that isn't on your tracked list** → add it
  ([question 11](11-tracked-pages.md)).

## How it lies

**"Source appearance" is not "cited".** Your source's link list is a *source
list* — the pages available to the answer. Some surfaces additionally mark
whether a link was actually cited; at least one provides no such status at all.
So this metric measures *attention*, not confirmed citation, and the two are
different claims. Expose the confirmed/unconfirmed/unknown split rather than
implying precision you don't have.

**Brand-per-page data is incomplete.** Pages that haven't been checked are
**excluded from brand filters until opened** — so a brand-filtered count is a
count of *checked* pages, not of all pages. Say so on the card, or the filter
silently under-reports. (And respect the three states:
[`null` is not `[]`](../07-gotchas/null-is-not-empty.md).)

**Mixed vintages in one row.** Appearances and days-seen follow the selected
date range; DR, traffic and publish date are *current* values, not historical to
the range. That's a defensible trade-off — refetching historical SEO metrics per
page is infeasible — but the column headers must say "DR now", "traffic now" or
someone will read the row as a snapshot.

**No weighting whatsoever.** No accuracy, sentiment, or causation weighting,
and no page reading. A page can top this ranking while being irrelevant or
hostile. It's a reach metric; combine it with question 6 and 7 before acting.

**Pooling across prompt groups favours the largest group.** Your biggest prompt
set contributes the most citations, so the global ranking leans toward it. Use
the class and brand filters to cut through that, and sanity-check a top page by
opening its prompt-level breakdown.
