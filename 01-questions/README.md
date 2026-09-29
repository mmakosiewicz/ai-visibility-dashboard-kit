# The twelve questions

A dashboard organised around *metrics* ("mention rate", "share of voice") tells
you how you're doing. A dashboard organised around *questions* tells you what to
do next. The twelve below are the ones my Sales team actually asks, which is why
they're the unit of the dashboard — one card per question, each ending in a
worklist. Eleven are load-bearing; the twelfth is explicitly experimental.

Every file uses the same eight headings, so a reader (or an agent) can diff them:

```
The question          what a salesperson would ask, in their words
Why it exists         the decision it informs — if none, delete the card
The prompts           what you ask the AI, and how many
What gets graded      the fields the grading pass must produce
The metric            formula + denominator
What the card shows   headline metrics, the table under it, the drilldowns
The action            who does what when the number moves
How it lies           the failure mode specific to this question
```

## The set

| # | Question | Kind | Needs | Prompt shape ([shapes.md](../02-prompts/shapes.md)) |
|---|---|---|---|---|
| [1](01-head-to-head.md) | When AI compares us to a competitor, do we win? | answer-graded | prompts + LLM | branded comparisons |
| [2](02-category.md) | Are we on the "best in category" list — and where? | answer-graded | prompts + LLM | list |
| [3](03-niches.md) | Are we recommended in the sub-niches we care about? | answer-graded | prompts + LLM | list or task, per niche |
| [4](04-task-recommendations.md) | When AI suggests a tool for a task, does it recommend us? | answer-graded | prompts + LLM | task |
| [5](05-source-influence.md) | Whose content does AI cite? | citation-derived | prompts | any |
| [6](06-fact-fidelity.md) | Is what AI says about our features and pricing true? | answer-graded | prompts + LLM + fact sheet | branded **+ fact sheet** |
| [7](07-narrative-risk.md) | Is AI amplifying negative narratives about us? | answer-graded | prompts + LLM | branded adversarial |
| [8](08-adjacent-categories.md) | In categories we're expanding into, do we show up at all? | answer-graded | prompts + LLM | list/task in the adjacent category |
| [9](09-crawl-health.md) | Can AI bots even reach our content? | operational | bot analytics | none — bot analytics |
| [10](10-citation-freshness.md) | How stale are the pages AI cites? | operational | crawl + page dates | none — page dates |
| [11](11-tracked-pages.md) | For pages we care about: how often cited, and do we get named? | citation-derived | tracked pages | none — a page list |
| [12](12-citation-attention.md) | Across everything, which pages keep coming up? *(experimental)* | citation-derived | prompts | any, weeks of history |

## Three kinds of question, and why the split matters

**Answer-graded (1, 2, 3, 4, 6, 7, 8)** — an LLM reads each answer and fills in
structured fields. These are the questions about *what AI says*. They share one
grading pass, one storage shape, one date/platform filter.

**Citation-derived (5, 11, 12)** — computed from the cited-source lists attached
to answers, with no LLM. Cheap, and they answer a different question: *whose
content is feeding the answers*. The three are scoped differently and that's the
point: 5 splits citations by class **within a prompt group**, 11 tracks **pages
you chose in advance**, 12 ranks **every page across every group** to find the
ones you should have chosen.

**Operational (9, 10)** — not about answers at all. Can bots reach you; is the
content they cite current. These are the gates: a brilliant page nobody can
crawl scores zero everywhere else, and no amount of prompt-level work fixes it.

Most AI-visibility dashboards I've seen only build the first group. The
operational pair is where the cheapest wins usually are, and it's the group
people skip because it isn't about AI at all.

## Or: build what your prompts can answer

Before choosing five, run [`scripts/fit_report.py`](../scripts/fit_report.py)
on your prompt list. It marks each question answerable or not from the shape
counts. The payments case ([10-case-studies](../10-case-studies/payments.md)) came out
with 1, 6, 7, 8 and 9 unanswerable — and a perfectly useful seven-card board.

## If you only build five

Start here and the dashboard is still coherent:

**2 (category)** — your baseline presence number. **1 (head-to-head)** — the
one Sales asks about daily. **4 (task recommendations)** — the largest prompt
surface, and the one where absence is cheapest to fix. **6 (fact fidelity)** —
the only question whose findings have a definite owner and a definite fix.
**9 (crawl health)** — cheapest possible win, and it gates everything else.

Add 5 and 7 once the first five are stable; they're interpretive and reward
having history. Leave 3, 8, 10 and 11 until someone asks a question you can't
answer — that's the signal you need them. **Build 12 last**, if at all: it's the
discovery layer over 5 and 11, and it's only meaningful once you have weeks of
citation history to pool.

## Ordering on screen

Not by number. The live board renders 1 → 12 because the numbers were assigned
in build order, and that's a mistake I kept. If I rebuilt the layout I'd group:

1. **Am I there?** — 2, 3, 8
2. **Do I win when I'm there?** — 1, 4
3. **Is what's said about me right?** — 6, 7
4. **Why?** — 5, 11, 12
5. **Is anything structurally broken?** — 9, 10

Groups 1–2 are for reporting, 3–4 are where the work comes from, and 5 is
checked first when a number drops for no visible reason.
