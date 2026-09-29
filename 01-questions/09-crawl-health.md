# 9 · Crawl health: can AI bots even reach our content?

## The question

"Before we optimise anything — are the AI crawlers actually getting our pages?"

## Why it exists

This is a **gate, not a workstream**. Every other question on the board assumes
the models can read your content. If AI bots are getting 404s and 500s on a
section of your site, nothing you write for that section can land, and the
prompt-level metrics will look like a positioning problem when they're an
infrastructure problem.

It's the cheapest win on the board and the one nobody builds, because it isn't
about AI answers at all — it's server logs.

## The data source

Not prompts. This comes from **bot analytics** — request logs filtered to AI
crawlers and agents. In my build, Ahrefs Web Analytics, filtered on bot category
`AI Crawler` / `AI Agent`, over a trailing 30-day window.

Any log source works as long as you can filter by bot identity and get status
codes plus paths. What you need:

| Dimension | Use |
|---|---|
| bot category / name | isolate AI crawlers from search crawlers and scrapers |
| HTTP status code | the actual health signal |
| path or host | *where* the errors are — without this the card isn't actionable |

## What gets computed

No grading. Bucket the status codes:

| Bucket | Codes | Reading |
|---|---|---|
| ok | 200, 304, 206 | served (304/206 are fine — cached and partial) |
| accepted | 202 | queued; watch it, don't panic |
| redirect | 301, 302, 307, 308 | works, but wasteful at volume |
| client error | 4xx | **the number that matters** |
| server error | 5xx | **the number that matters more** |

Then the actionable half: **top paths/hosts returning 4xx or 5xx to AI bots**,
ranked by request count, with the top bot name per row.

## The metric

**Error share = (4xx + 5xx) ÷ all AI-bot requests** over the window.

Deliberately simple, deliberately operational. Two properties I'd insist on:

- **Trailing window, not snapshot.** Bot traffic is spiky; a single day tells
  you nothing.
- **Not filtered by the board's date range or platform selector.** This is
  server-side reality, unrelated to which AI surface you're currently looking
  at. Scope independence matters — see [`05-cards/scope.md`](../05-cards/scope.md).

## What the card shows

```
headline:  total AI-bot requests · ok % · redirect % · client error % ·
           server error %
table:     status-code breakdown, ranked by volume
table:     top error paths — path · errors · top bot hitting it
window:    stated explicitly ("last 30 days: <from> → <to>")
```

Small thing that matters: put the window on the card. An operational metric with
an unstated window gets compared against an answer-based metric with a different
window, and the comparison is meaningless.

## The action

- **Any 5xx to AI bots** → engineering ticket, same day. There is no
  interpretation needed.
- **4xx concentrated on one path pattern** → usually a retired section still
  being crawled, or a robots/auth rule catching bots it shouldn't.
- **Heavy redirects at volume** → not broken, but you're spending crawl budget
  on hops. Worth fixing for large sites.
- **Error share trending up with no deploy** → someone changed a rule
  (WAF, rate limit, bot blocker). This card is how you find out.

## How it lies

**Bot identity is self-reported and spoofable.** Traffic claiming to be an AI
crawler may not be. For this card's purpose — "are we serving errors to things
that say they're AI crawlers" — that's acceptable, but don't use these counts as
a traffic or demand metric.

**Filters silently fail on some log APIs.** A regex filter on bot category was
accepted and *silently ignored* by one endpoint I used, returning all bots; an
equality filter worked. Validate that your filter actually filtered — compare a
filtered total against an unfiltered one once, by hand.

**Rate ≠ severity.** A 0.4% error rate that is entirely 500s on your pricing
page is worse than 3% that's all 404s on retired blog URLs. Always read the path
table, never the headline alone.

**Absence of errors isn't proof of access.** Bots can be served a 200 with a
JavaScript shell and no content. This card says "the request succeeded", not
"the content was readable" — that's what [question 10](10-citation-freshness.md)
and the citation data indirectly test.
