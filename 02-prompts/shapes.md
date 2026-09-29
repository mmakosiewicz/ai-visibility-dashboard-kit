# Prompt shapes: which metrics a prompt can honestly feed

The taxonomy in [taxonomy.md](taxonomy.md) sorts prompts by *buyer intent*. This
file sorts them by something more mechanical: **what the prompt names**. That
single property decides which metrics are valid for the answers it produces, and
it is the rule that lets this spec run on a prompt set that isn't the one it was
written for.

## The five shapes

| Shape | The prompt names… | Example | What an answer can tell you |
|---|---|---|---|
| **branded** | your brand | `ahrefs pricing`, `is ahrefs worth it`, `ahrefs vs semrush` | whether the answer is right, fair, and picks you |
| **conquest** | a rival, not you | `is moz a good seo tool`, `paypal alternatives` | whether you get pulled into a rival's conversation |
| **list** | nobody; asks for options | `best seo tools`, `best payment gateway for saas` | whether you're on the list, and how high |
| **task** | nobody; asks how to do a job | `how to do keyword research`, `implement webhooks for payment events` | whether a tool gets named at all, and whether it's you |
| **category** | the category itself, no product | `is seo dead`, `does link building still work` | whether the category is treated as alive; brand mentions are incidental |

Classification is nearly mechanical, in this order:

1. the prompt contains the brand or a brand variant → **branded**
2. else a tracked competitor → **conquest**
3. else a list marker (`best`, `top 10`, `top-rated`, `alternatives`, `compare`,
   `which`, `recommend`, `most used/popular/accurate`, `what tools`) → **list**
4. else a task marker (`how to`, `set up`, `implement`, `fix`, `why is my`,
   `can I …`), or a `how/why/where …?` question → **task**
5. else a **product finder**, a bare noun phrase qualified by a feature and not
   phrased as a question (`standing desks with a child lock`, `desk controllers
   that lock voice commands`) → **list**
6. else **category**

Two rules that look wrong but aren't:

- **`vs` / `versus` is not a list marker.** A comparison that names a product is
  already caught at step 1 or 2. What's left compares two *concepts* ("AEO vs
  SEO", "load sensing versus overload protection"), which is a category prompt.
- **`top` alone is not a list marker.** "How much does a standing desk top
  weigh" is a spec lookup. Only `top` + a number, `top-rated`, or `top picks`
  counts.

[`scripts/fit_report.py`](../scripts/fit_report.py) does this for you and prints
the counts; [`scripts/test_classify.py`](../scripts/test_classify.py) holds the
regression cases. On a third, hand-labelled set (53 prompts: product finders,
"best …", "Which …?" headings, definitions, decisions, specs) it now agrees on
51. The first version put 33 of those 53 in **category**, because it missed
bare product finders and every "Which …?" heading. It still misses questions
phrased as tasks but meaning something else ("what should I look for when
buying…" reads as task, not category). Check the per-prompt JSON before you
trust a card built on a small shape.

## Which metrics each shape feeds

| Metric | branded | conquest | list | task | category |
|---|---|---|---|---|---|
| Mention rate | ✓ (expect ~100%; a miss is a bug) | ✓ **primary** | ✓ | ✓ | ✓ (expect ~0) |
| Position / top-three | — (you're the subject) | ✓ | ✓ **primary** | ✓ | — |
| **Win rate** | ✓ **primary** on comparisons | ✗ | ✓ only when the answer puts you in the verdict | ✗ | ✗ |
| Capture | — | ✓ | ✓ | ✓ **primary** | ✓ |
| Tool-recommendation rate | — | — | — | ✓ ("no tool named" is a real outcome) | ✓ **primary** |
| Cohort share of voice | — | ✓ | ✓ | ✓ | — |
| Sentiment / negative rate | ✓ **primary** on adversarial | ✓ | ✓ | — | — |
| Fact accuracy | ✓ **primary** (needs a fact sheet) | ✗ | ✗ | ✗ | ✗ |
| Citation split / top pages | ✓ | ✓ | ✓ | ✓ | ✓ |

The ✗ cells are where a number would be *computable* and *wrong*:

- **Win rate on a conquest prompt.** "Is Moz better than Semrush?" — Semrush
  wins, and that is the expected result, not a loss for you. Counting it makes
  win rate move with how many rival-vs-rival prompts you happen to track. The
  Ahrefs board reported 38.9% until this was excluded; the honest figure was
  69.3%.
- **Win rate on a task prompt.** Task answers rarely pick a winner, and when
  they do, it's a tool for one step. Treat that as capture, not a verdict.
- **Fact accuracy anywhere but branded.** If the prompt didn't ask about you,
  claims about you are incidental and the denominator is meaningless.
- **Sentiment on task/category prompts.** You're barely mentioned; "neutral"
  dominates and tells you nothing.

### Win rate across shapes: the per-answer rule

Win rate needs *the brand to be in the comparison*. Two ways to enforce it:

1. **Per prompt** — count only branded prompts. Simple; right for a set like the
   Ahrefs one where every comparison names the brand.
2. **Per answer** — count any answer whose verdict names you *or* whose prompt
   names you, and exclude prompts that pit two rivals against each other. Right
   for a set with no branded prompts at all (the Stripe example: 0 of 50
   prompts name Stripe, yet 149 of 2,100 answers pick a winner, and 124 of
   those pick Stripe).

Pick one, write it in the caption, and don't mix them across cards.

## Which questions a shape can answer

| Spec question | Needs shape(s) | If you have none… |
|---|---|---|
| 1 head-to-head | branded comparisons | skip the card; don't fake it from list prompts |
| 2 category list | list (category-wide) | skip |
| 3 sub-niches | list (niche-specific) or task per job | skip or merge into 4 |
| 4 task recommendations | task | skip |
| 5 source influence | any | always available |
| 6 fact fidelity | branded + **a fact sheet** | skip; sentiment is not a substitute |
| 7 narrative risk | branded adversarial | conquest gives a weak proxy |
| 8 adjacent categories | list/task in the adjacent category | skip |
| 9 crawl health | none (bot analytics) | skip if no bot data |
| 10 citation freshness | none (page dates) | always available, slower |
| 11 tracked pages | none (a page list) | skip |
| 12 citation attention | any, weeks of history | wait |

**Rule of thumb: a card needs at least 5 prompts of the right shape**, or its
worklist is a list of one-offs and its rate flips on a single answer.

## The two case studies

| | SEO tools ([case study](../10-case-studies/seo-tools.md)) | Payments ([case study](../10-case-studies/payments.md)) |
|---|---|---|
| Prompts | 194 | 50 |
| branded | 84 (17 comparisons) | **0** |
| conquest | 13 | 2 |
| list | 12 | 5 |
| task | 37 | 40 |
| category | 48 | 3 |
| Headline metric | win rate (on branded) | capture (on task) |
| Cards | 16 groups → 6 sections | 7 groups → 4 sections |
| Fact fidelity | possible (fact sheet exists) | dropped |
| Entity risk | none | "square" ≠ Squarespace ≠ square footage |

Same pipeline, same schema, same grader template. What differed is entirely
described by the shape counts and the brand config. That is the claim this
file makes: **read the shapes first, then decide what the dashboard is**.
