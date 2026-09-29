# Case study 1: SEO tools (the set the spec was written on)

| | |
|---|---|
| Brand / cohort | Ahrefs vs Semrush, Moz, SE Ranking, Profound, Scrunch, Peec |
| Prompts | 194 in 16 tags; registered 29 Jul 2026 |
| Surfaces | ChatGPT, Gemini, Perplexity, Copilot, Google AI Overviews, Google AI Mode |
| Shapes | branded 84 (17 comparisons) · conquest 13 · list 19 · task 39 · category 39 |
| Answers | ~1,200/day; 61 days stored, last 14 graded (15,085 unique answers ≈ $3) |

Why this set can carry all twelve questions: it has branded comparisons (win
rate), branded fact prompts plus a fact sheet (fidelity), adversarial prompts
(narrative), and a large task surface (capture). Most reports won't — see
[the payments case](payments.md) for what to do then.

## Two mistakes made on this board that the spec now guards against

- **Win rate included conquest prompts.** "Is Moz better than Semrush?" was
  counted as a loss. 38.9% → 69.3% once win rate was limited to prompts that
  name the brand. Rule: [02-prompts/shapes.md](../02-prompts/shapes.md).
- **URL normalisation dropped the query string**, so every `youtube.com/watch`
  video became one "page" with 336 answers. Keep identifying params (`v=`),
  drop tracking ones (`utm_*`, `srsltid`, `authuser`). See
  [04-metrics/citation-metrics.md](../04-metrics/citation-metrics.md).

The 16 groups map onto the spec's questions as: head-to-head → Q1; conquest →
Q1 (conquest shape); shortlist, business case → Q2; segment fit, stack pick →
Q3; default tool → Q4; definitions → Q5; feature awareness, fact check, name
lookup, support answers → Q6; brand doubts, category doubts → Q7; category
naming → Q8; **category alive → not in the spec** (needs the "no tool named"
outcome from Q4's capture metric).
