# Adapting the spec to your report

The spec was written on one prompt set. Yours is different, and most of the
mismatch shows up as metrics that compute fine and mean nothing. This section
is the procedure that prevents that. Do it before you build anything.

## 0 · Or: have your prompts read and a board proposed

[`09-proposal/`](../09-proposal/) does steps 1, 3 and 4 below on your actual
prompts and a sample of your actual answers, then waits for you to approve.
Use it when your market isn't SEO tools, payments or standing desks, when your
prompts are untagged, or when the fit report puts a lot in *category*. The
steps below stay the reference for what it's doing.

## 1 · Run the fit report

```
python3 scripts/fit_report.py --prompts prompts.csv --brand brand.yaml
```

`prompts.csv` is your prompt list (Brand Radar's custom-prompt export works:
`query,tags`). `brand.yaml` is a copy of [brand.yaml](brand.yaml) with your
brand filled in. Ten seconds later you know:

- how many prompts you have of each **shape** (branded / conquest / list / task
  / category — [02-prompts/shapes.md](../02-prompts/shapes.md))
- which of the twelve questions your set can answer, and which it can't
- whether your brand or a competitor is also an ordinary word
- what the first build and each day after will cost to grade

Both case studies describe their output ([SEO tools](../10-case-studies/seo-tools.md),
[payments](../10-case-studies/payments.md)). If the report says a question isn't answerable,
don't build the card. A card fed by the wrong shape is worse than no card.

## 2 · Fill brand.yaml

Everything brand-specific lives in one file: name, variants, products to fold,
competitor cohort, owned / competitor / UGC domains, disambiguation lines, the
win-rate rule and its exclusions, and whether you have a fact sheet, bot data or
a tracked-page list. The pipeline reads it; the grader template is filled from
it; nothing else in the repo needs to know your brand.

The two case studies differ exactly here: the SEO-tools one has no
disambiguation lines and a fact sheet; the payments one has two disambiguation
lines ("Square" is also a word), a per-answer win rate and no fact sheet.

## 3 · Choose the grouping

If the source tags prompts, use the tags. If it doesn't (the Stripe report), or
the tags don't match questions, group **in the build config** and leave the
source alone. Rule: at least 5 prompts per group; merge until you get there.
Fifty prompts make about 7 groups, not 12.

## 4 · Pick the headline per group from its shape

| Dominant shape | Headline | Caption states |
|---|---|---|
| branded comparison | win rate | wins of decided verdicts, and how many answers named no winner |
| branded fact / adversarial | wrong-claim rate (with fact sheet) or negative rate | of answers mentioning you |
| conquest | mention rate | of graded answers on rival-named prompts |
| list | mention rate + position | position only where mentioned |
| task | capture | of answers that name any tool; tool-recommendation rate alongside |
| category | tool-recommendation rate | "no tool named" is the finding |
| troubleshooting / docs-shaped | owned-citation share | of confirmed citations |

## 5 · Fill the grader template

[grader-template.md](grader-template.md). Slots come from brand.yaml. If your
disambiguation slot is empty and the fit report warned about a common-word
name, it shouldn't be.

## 6 · Build in the spec's phase order

[BUILD-WITH-AN-AGENT.md](../BUILD-WITH-AN-AGENT.md), with your fit report and
brand.yaml pasted into the first prompt. Skip the cards the fit report marked ✗.

## What doesn't transfer, stated plainly

- **Fact fidelity without a fact sheet.** Sentiment is not a substitute and
  shouldn't be labelled as accuracy.
- **Crawl health and freshness** need bot logs and page-date data for *your*
  site; they don't come from the prompt set.
- **Twelve questions on fifty prompts.** The number of cards is a consequence
  of prompt count and shape mix, not a target.
- **The grading vocabulary.** "Free first-party tools count as named" is right
  for SEO (Search Console) and meaningless for payments. Read every line of the
  grader for your domain.
