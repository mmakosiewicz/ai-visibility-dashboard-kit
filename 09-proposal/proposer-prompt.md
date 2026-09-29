# The proposer prompt

`scripts/propose.py` sends these two prompts to any OpenAI-compatible model.
They're here so you can read what the model is told, and paste them into a chat
yourself if you'd rather not run the script. The script appends the shape
definitions from [metric-menu.json](metric-menu.json) and the prompts, with their
ids, as JSON.

The model never picks metrics. It groups prompts and proposes a shape per
prompt; the metrics come from the menu in code, so it can't invent one or bring
back a combination the spec rules out.

## Pass 1: groups

```
You are helping someone measure how AI assistants answer the prompts they track
for their brand, {label}, in the market: {category}. Tracked competitors:
{competitors}.

Read ALL the prompts below and propose groups IN THE USER'S OWN TERMS — the jobs,
worries or buying moments the prompts express (e.g. "emergency visits",
"insurance questions", "price shopping"), not generic labels like "list prompts".

Rules:
- Aim for groups of 5+ prompts. Fewer, larger groups beat many small ones:
  about one group per 7–10 prompts, never more than {max_groups}.
- A group may mix wording, but prompts in a group should share what a reader
  would DO with the answer.
- If some prompts have nothing to do with the market, put them in one group
  called "Outside the market" rather than forcing them elsewhere.
- If a measurement need is visible in the prompts that none of these metrics
  could serve — {metric_labels} — say so in unmet_needs. Don't propose a metric.

Return STRICT JSON: {"groups":[{"name":str,"description":str (one sentence)}],
"unmet_needs":[str], "set_notes": str (2 sentences max: what this prompt set is
mostly about, and anything unusual about it)}
```

## Pass 2: assignment (batches of 80)

```
Assign each prompt to exactly one group and one shape.

Groups: {groups}

Shapes (use exactly these words):
{shape definitions}

Rules:
- Shape follows what the prompt NAMES and ASKS, not its topic.
- "Which X…?", "best X", "X with <feature>" (a product finder) → list.
- "how do I…", "set up…", "fix…", "can I…" → task.
- definitions, "is X worth it", "X vs Y" between two CONCEPTS, reasoning → category.
- Use none only when no answer could reasonably name a product in this market.
- reason: max 12 words, why this shape.

Return STRICT JSON: {"assignments":[{"id":str,"group":str,"shape":str,"reason":str}]}
```

## What code does after the model answers

- **Brand and competitor tokens win.** If the prompt contains your brand or a
  tracked competitor (from brand.yaml), the shape is `branded` / `conquest`
  regardless of the model. That's a fact, not a judgment.
- **The word rules run as a cross-check.** Where the model and
  `fit_report.classify` disagree, the model's label is kept and the row is
  flagged `review` in shapes.csv. On the three example sets that was 10–20% of
  prompts; read those rows first.
- **Any prompt the model skipped** gets the word-rule label and a `review` flag.
