# 11 · Tracked pages: how often is each cited, and do we get named?

## The question

"For the specific pages we care about — our pricing page, our comparison pages,
that one third-party roundup — how often does AI cite them, and when it does,
does our brand actually get named?"

## Why it exists

Questions 2–8 are organised by prompt. This one is organised by **page**, which
is the unit content teams actually work in. It answers "did that page we
published/updated/pitched do anything", and it's the only card that can show a
piece of content earning its way into AI answers over time.

The second half of the question is the interesting half. A page being cited
while your brand goes unnamed is a weaker outcome than it looks: the source was
used, but the brand didn't land.

## The data source

A **registered list of pages you care about** — in Brand Radar, the report's
tracked pages — joined against the citation lists already stored with every
answer ([question 5](05-source-influence.md)).

No LLM, no extra prompts, and — importantly — **no API calls per page view**:
everything is computed from stored snapshots, so it works retroactively over
your whole history and costs nothing to browse.

Which pages to track: your money pages (pricing, plans, core product), your
comparison pages, the third-party pages that came out of question 5's ranking,
and anything you've just published or pitched. Once you have some citation
history, [question 12](12-citation-attention.md) is the better source for this
list — it ranks every page across every prompt group, so it surfaces the ones
you wouldn't have thought to add.

## What gets computed

Per page, two counts that must stay distinct:

| Metric | Meaning |
|---|---|
| `cites` | how many answers cited the page |
| `with_mention` | of those, how many **also named your brand** in the answer text |

Broken down per question and per AI surface.

Plus citation **stability** across days:

| Metric | Meaning |
|---|---|
| `coverage_pct` | % of days in range with at least one citation — the headline |
| `drops` | day-to-day transitions from cited → not cited |

Coverage answers "is this page reliably used"; drops explain why coverage isn't
100%. A page cited every day is load-bearing. A page cited half the days is
being chosen situationally, and that's a different (usually weaker) position.

## The metric

**Mention rate on citations = `with_mention` ÷ `cites`**, per page.

**Coverage = days with ≥1 citation ÷ days in range**, per page.

Report both against absolute citation counts. Coverage without volume is
misleading in the other direction: a page cited once on each of 14 days has
100% coverage and negligible influence.

## What the card shows

```
headline:  total citations · citations where we're named · mention rate ·
           pages cited / pages tracked · avg stability
table:     per page — url · citations · with mention · mention % ·
           coverage % · drops · per-surface split
drilldown: per page, per-question and per-surface breakdown, and the
           specific prompts citing it
link out:  the source report's own tracked-pages view, for manual review
```

`pages cited / pages tracked` is the first thing to look at. If you track 30
pages and 6 are ever cited, the other 24 are the finding.

## The action

- **Tracked page never cited** → it isn't in the answer supply chain. Either
  it's not the format models pull from (feature page vs comparison table), or
  it's not reachable/fresh — check questions 9 and 10 before rewriting it.
- **Cited often, brand rarely named** → the page works as a source but doesn't
  carry you. Usually means your brand appears in a part of the page the answer
  isn't drawing from.
- **Coverage falling on a page that used to be stable** → something changed:
  the page, the competition for that prompt, or the page's content. This is the
  earliest warning signal on the whole board.
- **A newly pitched third-party page starting to appear** → that's your outreach
  actually working, and it's the only place you can see it.

## How it lies

**Citation ≠ mention** — the same trap as question 5, and here it's explicit
rather than hidden, which is exactly why this card is worth having. A page can
be cited constantly in answers that never name you. Read the two columns
together, always.

**Coverage needs a real date range.** Computed over 2 days it's meaningless;
over 30 it's informative. Refuse to render it below some minimum and say why.

**Tracked-page lists go stale.** Pages get retired, redirected, rewritten. A
page showing zero citations may simply not exist any more. Re-validate the list
periodically — I cache it and refresh daily, because it changes rarely but
silently.

**URL normalisation is required, not optional.** Tracked pages often come back
as `example.com/faq` while citations are full URLs with scheme, `www`, query
strings and trailing slashes. Normalise both sides (strip scheme, `www.`, query,
fragment, trailing slash) or your join silently returns nothing and every page
looks uncited.
