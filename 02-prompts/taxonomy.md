# Prompt taxonomy

Six intent buckets. The bucket determines which research question a prompt
belongs to, what you can conclude from its answers, and how urgently you act.

| Bucket | Shape | Question | Buyer's state |
|---|---|---|---|
| **Comparison** | `<us> vs <them>`, `<us> or <them>` | 1 | actively evaluating, shortlist of two |
| **Category list** | `best <category> tools`, `top <category> software` | 2 | building a shortlist |
| **Niche list** | `best <sub-niche> tools`, `<sub-niche> software` | 3, 8 | has a specific job, no shortlist yet |
| **Task / how-to** | `how to <job>` | 4 | not shopping at all — tool recommendation is incidental |
| **Brand-specific** | `<us> pricing`, `<us> free plan`, `<us> api cost` | 6 | already interested, verifying details |
| **Adversarial** | `<us> review`, `is <us> worth it`, `<us> bad reviews`, `cheaper than <us>` | 7 | sceptical, looking for reasons not to |

## Why these six

They're separated by **what the answer can tell you**, not by wording.

A category list and a niche list look nearly identical as strings but produce
different brand populations — the niche one surfaces specialists who never
appear in the category list. A task prompt and a category prompt both mention
tools, but only the task prompt can tell you about the *uncontested* surface
where no tool gets named. Comparison and adversarial prompts both mention your
brand, but one measures who wins and the other measures what's held against you.

Mixing any two of these in one metric produces a number that moves for reasons
you can't attribute.

## Intent temperature, and why it drives priority

Roughly, from coldest to hottest:

```
task/how-to  →  niche list  →  category list  →  comparison  →  brand-specific
     ↑                                                              ↑
  biggest surface,                                        smallest surface,
  lowest intent                                            highest intent
                          adversarial ── sits outside the ladder:
                          high intent, negative direction
```

That shape explains the standing prioritisation:

- **Brand-specific errors first.** Smallest volume, highest intent, and a
  definite fix. Someone comparing plans and reading a wrong price is the most
  expensive error you can have.
- **Comparisons second.** Directly attached to live deals.
- **Category and niche next.** Shortlist formation — slower, structural.
- **Task prompts last by urgency, first by volume.** Biggest long-term
  opportunity, least immediate pain. Where uncontested wins live.
- **Adversarial: not a priority queue at all.** It feeds enablement, not the
  content backlog.

## Phrasing variants worth having

Within a bucket, some variants are different prompts, not synonyms:

| Variant pair | Why both |
|---|---|
| `<us> vs <them>` / `<us> or <them>` | `or` pulls a recommendation, `vs` pulls a feature table |
| `best X tools` / `X software` | different brand populations; `software` skews to established vendors |
| `best X tools` / `free X tools` | free-tier lists are a separate population |
| `alternatives to <competitor>` | a list prompt, but the highest-intent one: they've decided to leave |
| `<job> checklist` / `how to <job>` | checklists name tools less often — good for measuring uncontested surface |

## What this taxonomy leaves out

Stated plainly, because these are real gaps:

- **Conversational long-tail.** Multi-turn and sentence-shaped prompts behave
  differently. A separate set with its own card, if you want it.
- **Geography.** Every prompt here is one market. Scores are not comparable
  across countries — different answer populations, different competitors — so
  either run per-market sets separately or say the metric is single-market.
  Pooling markets is the quiet way to make a number meaningless.
- **Language.** Same argument as geography, more so.
- **Buyer role.** "best seo tools for agencies" vs "for beginners" produce
  different brand sets. Worth a subgroup if you sell to distinct segments.
- **Non-English.** Untested here; don't assume the grading prompts transfer.
