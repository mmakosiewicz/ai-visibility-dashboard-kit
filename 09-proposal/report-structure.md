# The report: fixed structure

Every proposal renders to the same report, whoever produces it, because every
path fills the same file: [report-template.html](report-template.html). You
supply counts ([measurements.md](measurements.md)); the template computes
labels, main numbers and warnings. This page documents what the template
produces, for review and for porting it into another dashboard. **Don't rebuild
the page from this description; fill the template.**

`{B}` is the brand's display name. Every label and sentence below comes from
[`scripts/plain_language.py`](../scripts/plain_language.py). Use that file's
wording, not a paraphrase.

## Rules that apply everywhere

- **No spec jargon on the page.** No "shape", "verdict", "headline",
  "denominator", metric ids, or file names. Those stay in `plan.json`.
- **Every number has three things next to it:** a plain name ("How often {B} is
  named"), one sentence on what it tells you, and its calculation:
  `Mention rate = answers that name {B} ÷ all answers = 23 ÷ 32 = 72%`.
- **The calculation always shows the real counts.** Never a bare percentage.
- **Numbers are only computed on the questions whose type allows them**
  (table in [`../02-prompts/shapes.md`](../02-prompts/shapes.md)). When that's
  fewer than all questions in a topic, say so: "Based on 7 of 8 questions in
  this topic; the rest don't fit this measure."
- **Sample numbers are a check, not an estimate.** Say it once near the top.

## Sections

### 1 · Title and one-line summary

- Title: **What to track for {B} in AI answers**
- Lead: "We read the {N} questions this report asks AI assistants, sorted them
  into {T} topics, and checked which numbers are worth putting on a dashboard
  for each one, using {A} real AI answers from {one day | D days}."

### 2 · Fit (left card)

One of three headings, with its sentence (`SET_TEXT`):

| Condition | Heading |
|---|---|
| under 20% of questions off-topic | Good fit for a dashboard |
| 20–50% off-topic, or under 15 measurable questions | Partly measurable |
| over 50% off-topic | Only sources can be tracked |

Then, small: "Numbers on this page come from a small sample. They show whether
something is worth tracking, not what the real figure is. “3 of 12” doesn't mean
25%."

### 3 · Question types (right card)

Heading: **What kinds of questions are in this report**. A stacked bar of the
counts, then one row per type present, most common first: `{count} · {name}`
plus its one-line description. Names:

| Type | Name | Description |
|---|---|---|
| branded | About you | Names {B} directly |
| conquest | About a competitor | Names a competitor, not {B} |
| list | Asks for recommendations | Wants names: the best, which one, where to go |
| task | Asks how to do something | Wants steps or help with a job |
| category | General question | Wants information, not a recommendation |
| none | Off-topic | Unrelated to {B}'s market |

Close with: "The type decides what can be measured: {B} can only “win” a
question that asks for a recommendation."

### 4 · Worth checking (only if there's something)

A highlighted box with plain-language warnings (`warnings()` in
plain_language.py). For example: "15 of 66 questions were hard to sort. They're
marked ⚠ in each topic's question list and are worth a quick look." Omit the
box when empty.

### 5 · The dashboard this suggests

Heading plus "One card per topic, showing the number most worth watching
there." One card per topic, in the plan's order:

- topic name
- the main number, large
- its plain name
- the result as a sentence ("23 of 32 answers name {B}"; `sentence()` in plain_language.py)
- `{standard name}: {n} ÷ {d} = {value}`
- footer: `{q} questions · {k} numbers worth tracking`

If a topic has no main number: "Nothing worth tracking here". A main number
that's at zero is shown greyed.

**Choosing the main number:** take the topic's most common question type and
walk its list in `metric-menu.json → headline_by_shape`. Pick the first metric
that's *worth tracking* **and** non-zero in the sample. If none is non-zero, take
the first *worth tracking* one. Failing that, take the first *track only as a
starting point* one.

### 6 · One section per topic

1. **Topic name**, the one-sentence description, and a chip per question type
   with its count ("7 asks for recommendations", "1 about you").
2. **Worth tracking.** Every metric labelled *Worth tracking* or *Track only
   as a starting point*. The main number comes first, then the rest in menu
   order. Each shows:
   - value (large; omitted for the citation split, which has several)
   - plain name, a **main number** tag if it is one, and a *Track only as a
     starting point* tag if it's at zero
   - what it tells you (one sentence)
   - calculation box: `{standard name} = {formula in words}`, then
     `= {n} ÷ {d} = {value}`
   - reason ("About 224 answers a week to count, enough to see real changes.")
     plus the "Based on X of Y questions" note when it applies
3. **Not worth tracking here ({count})**, collapsed. Each metric with plain
   name, standard name in brackets, its label, reason and formula (plus the
   counts, unless it's *Can't measure yet*).
4. **The {n} questions in this topic**, collapsed, "· ⚠ {k} to check" if any
   were hard to sort. Each question with its type chip. Flagged ones get a
   one-line note on why.

### 7 · How to read this page (collapsed)

Four short paragraphs: topics, question types, calculations, and the five
labels:

| Label | Meaning |
|---|---|
| Worth tracking | enough answers each week to see real changes |
| Track only as a starting point | {B} doesn't appear yet, so it reads 0%; useful only if you're trying to get in |
| Too little data | too few questions or answers to be reliable |
| Nothing to measure | the thing it counts never happens in these answers |
| Can't measure yet | needs something not provided, like a list of verified facts |

### 8 · Footer

What generated it, who or what sorted the questions, the date, and the data
source.

## The metrics, in words

Standard name, plain name, and formula (`numerator ÷ denominator`). The
denominator is the part people get wrong. Copy it exactly.

| Standard name | Plain name | Formula |
|---|---|---|
| Mention rate | How often {B} is named | answers that name {B} ÷ all answers |
| Average position | How early {B} is named | sum of {B}'s rank in each answer ÷ answers that name {B} |
| Top-three rate | How often {B} is in the top three | answers with {B} ranked 1–3 ÷ answers that name {B} |
| Win rate | How often {B} is the top pick | answers whose single winner is {B} ÷ answers that name {B} and pick one winner |
| Capture | {B}'s share of recommendations | answers that recommend {B} ÷ answers that recommend any specific brand or organization |
| Recommendation rate | How often anyone gets recommended | answers that recommend a specific brand or organization ÷ all answers |
| Share of voice (vs. tracked competitors) | {B} vs. competitors | mentions of {B} ÷ mentions of {B} + tracked competitors |
| Negative rate | How often AI is critical of {B} | answers negative or mixed about {B} ÷ answers that name {B} |
| Wrong-claim rate | How often AI gets facts about {B} wrong | claims that contradict the fact list ÷ claims that can be checked |
| Owned citation share | How often {B}'s website is a source | cited sources on {B}'s website ÷ all cited sources |
| Citation split | Whose websites AI uses as sources | cited sources in each group ÷ all cited sources |

"Named first" is **not** win rate. An answer that lists five tools without
picking one has no winner, and it's left out of win rate entirely.
