# Case study 2: the same spec on a payments report

The first example (SEO tools, 194 prompts, [the SEO-tools case](seo-tools.md)) shaped
every default in this spec. This one contradicts most of them, which is why it
is here. Same pipeline, same schema, same grader template, same card anatomy.
Built in one afternoon by forking the first board and changing the brand config.

## The report

| | |
|---|---|
| Brand / cohort | Stripe vs PayPal, Square |
| Prompts | 50, **untagged**, tracked since 8 Sep 2026 |
| Surfaces | ChatGPT, Gemini, Perplexity, Copilot, Google AI Overviews, Google AI Mode |
| Shapes | branded **0** · conquest 2 · list 5 · task 40 · category 3 |
| Answers | ~300/day; 6,044 stored and 5,524 unique answers graded for ≈ $1.30 |

## What changed, and why

| Decision | SEO-tools board | Payments board | Driven by |
|---|---|---|---|
| Grouping | 16 tags from the source, 6 sections | **7 groups assigned in the build config**, 4 sections; source untouched | no tags on the report; 50 prompts can't carry 12 questions |
| Headline metric | win rate | **capture** (share of tool-naming answers that name us) | 0 branded prompts, 40 task prompts |
| Win rate | per prompt: only prompts naming the brand | **per answer**: any decided verdict, minus the one rival-vs-rival prompt | see [02-prompts/shapes.md](../02-prompts/shapes.md) |
| Fact fidelity | built (fact sheet exists) | **dropped** — no fact sheet, and no branded prompt to hang it on | brand.yaml `fact_sheet: false` |
| Narrative risk | its own card (10 adversarial prompts) | no card; sentiment shown as a secondary chip | 0 adversarial prompts |
| Grader | no disambiguation | two disambiguation lines; Braintree/Venmo kept separate | "Square" collides; PayPal owns rivals |
| Cohort matching | substring was harmless | **exact token** — "squarespace" appeared 36 times and is not Square | entity collision |
| Rivals named | tool names, falling back to all brands | **tool names only** | fallback listed Visa, Netflix and Spotify as rivals (they appear as examples in payments answers) |

## The seven groups

| Group | Prompts | Primary metric | Why |
|---|---|---|---|
| Shortlists | 6 | mention rate + position | the only list-shaped prompts |
| Build & integrate | 11 | capture | developers asking how; "no tool named" is a legitimate outcome |
| Subscriptions & marketplaces | 6 | capture | merged from two groups of 3 — too small alone |
| Global payments | 9 | capture | |
| Compliance | 5 | capture | |
| Fraud & disputes | 7 | capture | |
| Operations & troubleshooting | 6 | **owned-citation share** | whose docs answer "why did my webhook fail" is the question |


## What the first week showed (21–27 Sep 2026, so you can judge the shape of the output)

- Stripe mentioned in 61% of answers; among the recommended tools in 80% of
  answers that recommend one; 54% share of voice against PayPal (808 mentions)
  and Square (299).
- Win rate 83% (124 of 149 decided) — but only 149 of 2,100 answers pick a
  winner at all, which is the expected shape for a task-heavy set.
- Weakest: Fraud & disputes (capture 49%; Verifi and Ethoca are named instead)
  and Compliance (mentioned in 42%). Perplexity mentions Stripe in 33% of
  answers vs 57–72% elsewhere.
- Two prompts lost every decided verdict: "PayPal alternatives for
  international payments" (7/7 to Wise) and "Best payment solution for
  nonprofits" (6/6 to Zeffy, Givebutter, Donorbox).

Numbers above are one week of one report and are here to show what the cards
look like, not as a benchmark.

## Fit report output

On this report, `scripts/fit_report.py` printed the shape counts, marked
questions 1, 6, 7, 8 and 9 as not answerable, and warned about "stripe",
"square", 0 branded prompts and 50 untagged prompts. That's the list of
decisions in the table above.
