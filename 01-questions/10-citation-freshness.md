# 10 · Citation freshness: how stale are the pages AI cites?

## The question

"The pages AI quotes about us — when were they last actually updated?"

## Why it exists

A page from 2023 being cited today is quoting last year's pricing, last year's
feature set, last year's positioning. Question 6 tells you a wrong fact is
circulating; this card frequently tells you *why*: the source is old and you
never refreshed it.

It's the other operational gate, and it produces the most boring, most reliably
useful worklist on the board: pages to update, ranked by how often AI cites
them.

## The data source

No prompts and no grading. Two inputs:

1. The set of **your own pages that appear in citation data** (from
   [question 5](05-source-influence.md)).
2. A **date per page**, which is the hard part.

## Getting the date right

This is the entire difficulty of the card. Three sources, in priority order:

| Priority | Source | Why this order |
|---|---|---|
| 1 | visible "Updated: <date>" on the page | editor-set, reader-visible — the date a human decided to publish |
| 2 | JSON-LD `dateModified` | machine-set; any touch counts, including automated ones |
| 3 | the data provider's publish/modified timestamp | useful fallback, definitions vary |
| — | else | `unknown`, counted separately — never silently treated as fresh |

Why the order isn't obvious: I found a page whose `dateModified` said April
2026 while its visible line read "Updated: August 2024" — a 20-month gap where
something re-stamped the page with no editorial change. Trusting `dateModified`
alone **under-reports** staleness. Using only the provider's date
**over-reports** it. So: prefer the human-visible date, fall back, and keep
`unknown` as its own bucket.

If you take one implementation note from this card: **fetch and parse the page
yourself** for the visible date and the JSON-LD. Metadata from an index is not a
substitute.

## The metric

**Stale share = cited pages whose best-known date is older than 12 months ÷
cited pages with a known date.**

Plus **median age in months**, which is the better trend line — the 12-month
threshold is arbitrary and steps, whereas the median moves smoothly.

Report the `unknown` count next to both. A card claiming 8% stale out of 40
pages, where 60 more have no date at all, is not telling the truth.

Two populations worth splitting if you can: pages **AI cites** (the priority)
versus pages **AI bots crawl** (the wider set). The first is your worklist; the
second is context.

## What the card shows

```
headline:  cited pages · cited stale 12mo+ · cited median age ·
           crawled stale 12mo+ · crawled median age · date unknown
table:     the stale cited pages — url · best-known date · date source ·
           citations · what it's cited for
drilldown: per page, which prompts cite it and on which surfaces
```

The **date source** column is not a detail. "Stale per visible date, fresh per
`dateModified`" is exactly the case someone will challenge, and showing which
signal you used ends the argument in one look.

## The action

- **Stale page with high citations** → update it. This is the top of the
  content-refresh queue and it needs no further analysis.
- **Stale page carrying pricing or limits** → highest priority; cross-check
  against question 6's error list, they usually agree.
- **Fresh `dateModified` but old visible date** → decide which one you want to
  be true, then make them agree. Mismatched dates confuse models *and* readers.
- **Large `unknown` bucket** → a template problem. Add a visible updated date
  and JSON-LD to the template; it's one change that fixes the whole bucket.

## How it lies

**`dateModified` is not an editorial date.** A CDN touch, a template change or a
sitemap rebuild can update it. It answers "was this file written to", not "was
this content reviewed".

**Freshness is not correctness.** A page updated last week can still state the
wrong price; a three-year-old page can be perfectly accurate. This card
prioritises *candidates* for review — question 6 is what actually judges truth.

**Stale share is sensitive to the denominator.** As you get cited on more pages,
the share moves without any page getting older. Read the median and the absolute
count alongside it.

**Not every old page should be updated.** Some are correctly historical (a
changelog, a 2019 study). A worklist from this card needs a human pass before it
becomes tickets.
