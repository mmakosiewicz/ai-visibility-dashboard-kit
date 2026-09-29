# Worklists

The difference between a dashboard people check and a dashboard people use.

A metric says *how you're doing*. A worklist says *what to do next*, in an order
someone can work through. Every card on my board produces one, and they all
flow into a single saved queue.

## Findings, not metrics

A finding is a row someone could act on:

| Question | A finding looks like |
|---|---|
| 1 head-to-head | "we lose `<us> or <competitor>` on 5 of 7 surfaces" |
| 2 category | "absent from `free seo tools`, the highest-volume prompt in the set" |
| 3 niches | "`local SEO` mention rate is a third of the category average" |
| 4 tasks | "`how to fix crawl errors` names a tool in 20% of answers — uncontested" |
| 5 sources | "this third-party page is cited in 40% of category answers and mentions us" |
| 6 facts | "wrong API price, hard severity, 3 weeks old, now on 4 surfaces" |
| 7 narrative | "'steep learning curve' in 12 answers; here are the verbatim quotes" |
| 9 crawl | "AI bots getting 500s on `/pricing`" |
| 10 freshness | "cited page last updated 19 months ago, carries pricing" |
| 11 tracked | "comparison page we published 6 weeks ago has never been cited" |

Each is a sentence with a subject, a number and an implied owner. If you can't
phrase a row that way, it's a metric, not a finding.

## Ranking: impact × fixability

Two axes, and the second is the one people skip:

**Impact** — intent temperature of the prompt (see
[taxonomy](../02-prompts/taxonomy.md)), search volume, citation volume, number
of surfaces affected, severity.

**Fixability** — who owns the fix and how long it takes:

| Fixability | Example | Owner |
|---|---|---|
| ours, today | wrong number on our own page | content |
| ours, a sprint | new comparison page | content |
| ours, engineering | 5xx to AI bots | eng |
| someone else's, warm | third-party page that already mentions us | outreach |
| someone else's, cold | page that has never mentioned us | outreach |
| not fixable | competitor's own comparison page | counter-content |

A high-impact finding with no owner isn't work, it's a complaint. Sorting by
impact alone produces a queue where the top five items are all "be better known
in a category we just entered".

## Standing priority order

When everything is on fire, this is the sequence I'd defend:

1. **Crawl errors** (question 9) — a gate; everything else is blocked behind it
2. **Hard factual errors on our own pages** (6) — fastest fix, highest damage
3. **Comparison losses on high-volume prompts** (1) — attached to live deals
4. **Absence from high-volume category and niche prompts** (2, 3)
5. **Uncontested task prompts** (4) — biggest surface, slowest payoff
6. **Third-party outreach on warm pages** (5) — high value, long lead time
7. **Narrative themes** (7) — to enablement, not to the content backlog
8. **Stale cited pages** (10) — steady background queue

Technical before content, and content before outreach — not because outreach
matters less, but because you can't evaluate whether outreach worked while a
gate is closed.

## The saved queue

One list, persisted, that anyone can add to from any card. Mine is a
"fixing list" — a button on worklist rows and a page that shows the queue.

What each row needs to carry:

```
what           the finding, as a sentence
where          prompt / page / error identity (so it can be re-checked)
why            the number that made it a finding, at the time it was added
who added it   and when
status         open / in progress / done / won't fix
```

Two properties that matter more than the schema:

- **Snapshot the number at add time.** "Mention rate 22%" at the moment someone
  decided it mattered. Otherwise the row's justification quietly changes under
  it and nobody can tell whether the fix worked.
- **`won't fix` is a real status.** Half the rows on any honest queue are
  deliberate non-actions ("absent from a category we don't sell into"). Without
  that status, people delete rows instead, and you lose the record of the
  decision.

## Re-checking

The loop that closes: for each open row, re-run its specific check against the
latest snapshot and show whether the number moved. That's the only way anyone
learns which interventions work, and it's cheap because the row records exactly
what to re-check.

It also produces the one genuinely motivating artefact in the whole system —
a list of things that got better because someone did something.

## Anti-patterns

- **A worklist that regenerates from scratch every day.** Then it's a feed, not
  a queue, and nothing is ever finished. Generate candidates daily; keep the
  saved queue stable.
- **Auto-creating tickets.** The candidate list has false positives by design
  (see [suspect vs cause](../04-metrics/accuracy.md#suspect-vs-cause)). A human
  pass between finding and ticket is what keeps the card credible.
- **Ranking by volume alone.** Produces a queue of unfixable prestige problems.
- **One queue per card.** Six half-worked lists. One queue, tagged by source.
