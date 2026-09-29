# Running step 0 with the Ahrefs MCP server

For Claude, ChatGPT, Cursor or any assistant connected to the
[Ahrefs MCP server](https://docs.ahrefs.com/docs/mcp/reference/introduction)
(`https://api.ahrefs.com/mcp/mcp`). No terminal or Python needed. The result is
the same report the script produces, because it comes out of the same
template: [report-template.html](report-template.html).

**No API keys needed.** You are the grader: sorting questions and reading
answers is done by you, the model already in the chat. The only connection is
the user's Ahrefs MCP sign-in. (The `OPENAI_API_KEY` in other docs is for the
unattended terminal script, which has no assistant to do this.)

**The split of work:** the MCP server supplies the report's questions,
answers and the counts it can do over all of them. You (the assistant) sort the
questions and read the answers. The template turns your counts into the page.
You never decide what the page looks like, which numbers are worth tracking, or
which one is the main number.

## 1 · Ask for the report

Your first message is a question:

> Which Brand Radar report should I measure? Paste its URL or id. And tell me
> your brand's name and website, and your main competitors.

The id is the long code in the report's address
(`app.ahrefs.com/brand-radar/reports/<id>/…`). Don't use example data, reports
from earlier conversations, or reports you picked yourself. If the
`brand-radar-reports` tool is available, you can list reports to help the user
choose, but let them choose.

Call the `doc` tool for `ai-responses`, `mentions-overview` and `cited-domains`
before first use. The tool list's schemas are simplified.

## 2 · Get the questions and check nothing is missing

Use **yesterday** (today's scans may be unfinished). Every call below uses the
same base: `report_id`, `prompts=custom` (**always**: without it, answers to
Ahrefs' public questions mix in) and `date`.

**Your plan caps rows per call** (Lite 100, Standard 250, Advanced 500,
Enterprise unlimited). Two rules follow, both tested:

- **Never page with `offset`.** On this endpoint it returns the same rows again
  (or an error). Narrow the call with a `where` filter instead.
- **A call that returns exactly the cap was cut off.** Split its question list
  in half and ask again.

1. For each surface (`data_source`: chatgpt, gemini, perplexity, copilot,
   google_ai_overviews, google_ai_mode, claude, grok), call **`ai-responses`**
   with `select=question,last_updated`. A surface that returns nothing isn't
   tracked by this report; drop it.
2. The questions are the distinct `question` values. If a question comes back
   twice for one surface, count it once.
3. **Count check:** answers should equal questions × surfaces. State both
   numbers. Under 90%? Try the day before. **Never** sample the questions, sort
   by volume or stop at the first page.

These calls cost no API units: custom-question data is free (checked from the
units headers on each response).

## 3 · Sort the questions

Follow both prompts in [proposer-prompt.md](proposer-prompt.md):

1. **Topics**, in the user's terms, 5+ questions each, about one per 7–10
   questions.
2. **A type for every question**: `branded` (names the brand), `conquest`
   (names a tracked competitor, not the brand), `list` (asks for
   recommendations: best / which / a product finder), `task` (how to do
   something), `category` (information, definitions, "is it worth it"), `none`
   (off-topic for the market).

A question that contains the brand's name is always `branded`. One that names
a tracked competitor (and not the brand) is always `conquest`. Mark a question
with a short `note` when its type was a close call.

## 4 · Count, topic by topic

Record `num`, `den` and `looked_at` for each metric, as defined in
[measurements.md](measurements.md). Count only over the questions whose type
allows the metric (the `shapes` list per metric in
[metric-menu.json](metric-menu.json)).

Filter to a topic's questions with `where`:
`{"or":[{"field":"question","is":["eq","<question 1>"]}, …]}`, all active
surfaces comma-separated in `data_source`. Keep each call under the row cap:
about 12 questions × 7 surfaces fits in 100 rows. Split bigger lists.

### Counted by the server (all the answers, small results)

| Number | Call |
|---|---|
| answers examined (`looked_at` for these; `den` of mention rate) | `ai-responses`, `select=question,data_source,last_updated`: count the rows, one per question and surface |
| mentions (`mention_rate` num) | the same call with `where` = `{"and":[<questions>, <brand>]}`, where `<brand>` is `{"or":[{"field":"response","is":["iphrase_match","<name>"]}, …]}` over the brand's name, variants and products. Count the rows |
| share of voice (`cohort_sov`) | `num` = the brand's count above. `den` = that plus the same count for each tracked competitor |
| cited websites (`owned_citation_share`, `citation_split`) | `cited-domains`, `select=domain,responses`, same question filter. `responses` = answers citing that site (each website once per answer). `den` = sum of `responses`; `num` = rows on the brand's domain(s); split the rest into competitor, ugc (reddit, youtube, quora, medium, review sites) and third-party |

Don't use `mentions-overview` or `sov-overview` for these. They count
duplicate answers, and share of voice there isn't this metric.

### Read by you (a sample)

A day of answers is far too much text for one chat (about 700,000 characters
for 50 questions on 7 surfaces). So per topic, read **2 questions' answers**
(about 14 answers): pick different question types, recommendation questions
first (`list`, then `branded`, `conquest`, `task`, `category`). Fetch them with
`select=question,data_source,response`. For each answer, apply the grader in
[../08-adapting/grader-template.md](../08-adapting/grader-template.md): the
brand's rank among brands in order of first mention, whether a specific product
or organization is recommended, the single overall winner (null when there
isn't one, which is common and correct) and the tone toward the brand.

**Keep only the tallies, then move to the next topic.** Don't carry the answer
text forward.

| Metric | num | den | looked_at |
|---|---|---|---|
| `position` | sum of ranks | answers naming the brand | answers you read that the metric applies to |
| `top_three_rate` | answers with rank 1–3 | answers naming the brand | 〃 |
| `win_rate` | answers whose winner is the brand | answers naming the brand **and** picking one winner | 〃 |
| `capture` | answers recommending the brand | answers recommending anyone specific | 〃 |
| `tool_recommendation_rate` | answers recommending anyone specific | all read | 〃 |
| `negative_rate` | negative or mixed | answers naming the brand | 〃 |

The template projects `looked_at` to a week, so a small sample is judged
fairly. Tell the user these six rest on a sample: on the Stripe test, the
sample moved three topics' counts of trackable numbers compared with reading
every answer (8 → 5, 8 → 7, 8 → 8 with a different main number). A rerun with
the script path (`propose.py`) reads everything if they need firmer numbers.

## 5 · Give the user the report

The page comes from [report-template.html](report-template.html). It accepts
your measurements object ([measurements.md](measurements.md)) three ways; use
the first your client supports:

1. **As a file.** If you can create files or artifacts (Claude artifacts,
   ChatGPT's code tool): take the template exactly as it is, replace
   `{"_template": true}` inside `<script type="application/json"
   id="measurements">` with your object, and hand over the file.
2. **Pasted.** Give the user the object in one code block and this link:
   <https://mmakosiewicz.github.io/ai-visibility-dashboard-kit/09-proposal/report-template.html>.
   The page shows a box; they paste, and the report appears. Nothing is
   uploaded. It has a button to save the finished report as a file.
3. **Offline.** They download the template from the repo, open it and paste
   in the same way.

Set `cited_flag` to `false`: MCP links don't say which were actually cited.
Include the brand details the user confirmed in step 1 (`competitors`,
`variants`, `owned_domains`, `competitor_domains`, `category`): the build needs
them.
Don't summarise the report into your own layout, restyle it or add sections.

## Checklist before you hand it over

- [ ] The user named the report. Nothing came from example or earlier data
- [ ] `prompts=custom` on every call; only surfaces that returned answers
- [ ] Answers = questions × surfaces (±10%), stated
- [ ] No `offset`; any call that hit the row cap was split and repeated
- [ ] Every question has a type and a topic; topics have 5+ questions
- [ ] Counts only over question types the metric allows
- [ ] Win rate: winner must be picked overall. "Named first" isn't a win
- [ ] Mentions, share of voice and citations counted by the server over every answer
- [ ] The six read metrics say they rest on a sample
- [ ] Measurements contain counts only: no percentages, labels or verdicts
- [ ] The template is unchanged apart from the measurements block

## How this was tested

The steps were run against the public API endpoints the MCP tools wrap (one
tool per endpoint), on a 50-question report tracked on 7 surfaces, with a
100-row cap and no `offset`. That took 79 `ai-responses` calls and 64
`cited-domains` calls, and no API units. The count check came out at 350 of
350. The server counts matched a full script run within a few answers: 3
of 8 topics had identical mention counts, and the rest were off by up to 3.
They weren't run through an actual MCP client. If a step behaves differently
there, please open an issue.
