# Propose before you build

Step 0 of the build, for any prompt set, and the only step that reads **your**
prompts before the spec's defaults touch them.

The fit report ([`scripts/fit_report.py`](../scripts/fit_report.py)) sorts
prompts with word rules written on three prompt sets. That's free, and it's a
guess once your prompts don't sound like SEO tools, payments or standing desks.
This step replaces the guess with a proposal you approve:

1. **An LLM reads all your prompts and groups them in your own terms.** It uses
   the jobs and buying moments the prompts express ("emergency visits",
   "insurance questions"), not our five shapes and not our twelve questions.
2. **Each prompt gets a shape, or `none`.** The five shapes from
   [02-prompts/shapes.md](../02-prompts/shapes.md) are the only allowed labels.
   `none` means no answer could reasonably name a product in your market
   (weather, poems, football). The word rules run alongside as a cross-check,
   and disagreements are flagged, not settled silently.
3. **Metrics come from a fixed menu, in code.** [metric-menu.json](metric-menu.json)
   is the metric-validity table from `shapes.md` as data. The model never picks
   a metric. A metric is proposed for a prompt only if that prompt's shape
   allows it, so the spec's ✗ cells (win rate on rival-vs-rival prompts,
   sentiment on how-to prompts) can't come back.
4. **Every proposed metric is computed on a sample of real answers.** One or
   two days exported from Brand Radar, graded with the grader template filled
   from your brand.yaml.
5. **You get one verdict per metric per group**, with the number it rests on.
6. **You approve or edit**, then build from the approved plan.

## Run it

```
export AHREFS_API_KEY=...        # with Brand Radar access
python3 scripts/propose.py       # asks for the report, pulls it, proposes
```

Step one is always the report. [`fetch_report.py`](../scripts/fetch_report.py)
asks for a Brand Radar report URL or id, finds which AI surfaces it tracks, and
pulls one whole day of answers (yesterday, since today's scans may not be
finished; `--days 2` for two). It checks the count against questions ×
surfaces × days and warns when answers are missing. It also asks for your brand
and competitors, because the API doesn't expose a report's brand settings. It
writes `report/<id>/` with `prompts.csv`, `answers.jsonl`, `brand.yaml` and
`fetch.json`.

`propose.py --from-report report/<id>/` does the rest and writes into
`report/<id>/proposal/`. Run from a terminal, there's no assistant to sort and
grade, so the script calls an OpenAI-compatible model
(`OPENAI_BASE_URL`, `OPENAI_API_KEY`, `--model`). A budget model is enough: on a
50-question report with 350 answers, the whole run took about 6 minutes and a
few cents. `--no-llm` skips the model: groups come from the report's tags and
types from the word rules.

**One limitation of the public API:** it doesn't say which links an answer
actually cited, as opposed to links it only found. Source numbers therefore
count every link and read somewhat high. The report says so.

**Already have files?** `--prompts`, `--brand` and `--answers` still work.
`answers.jsonl` needs `question`, `model`, `response` and `sitelinks` (a list of
`{url, cited}`). If it already carries the grader's fields, nothing is
re-graded.

## Three outputs, one source

| File | For | What's in it |
|---|---|---|
| `proposal.html` | the marketer | **the report**: [report-template.html](report-template.html) filled with this proposal's counts ([measurements.md](measurements.md)). The template computes the labels and main numbers, so every path gives the same page. Layout documented in [report-structure.md](report-structure.md). Same content as proposal.md |
| `proposal.md` | the marketer | written in plain English: the kinds of questions in the set, the suggested dashboard (one main number per topic), then per topic every number worth tracking with what it means, its standard metric name, the formula and the sample's actual calculation ("Mention rate = answers that name you ÷ all answers = 23 ÷ 32 = 72%"), and a collapsed list of numbers not worth tracking and why |
| `shapes.csv` | the marketer, editing | one row per prompt: `group`, `shape`, the word-rule shape, a `review` flag, the model's reason. **This is the file you change.** |
| `plan.json` | the build agent | the same content as data: groups → prompt ids → metrics with verdicts and headline, set verdict, answerable questions, unmet needs. Every metric also carries a `plain` block (name, what it means, status, reason, calculation), so a dashboard can show the same wording |

The edit loop: fix rows in `shapes.csv` (start with the `review` flags), then
re-run with `--from-shapes proposal/shapes.csv --answers proposal/sample-graded.jsonl`.
Nothing is re-classified or re-graded. The sample is recomputed in seconds and
all three files are rewritten. (`sample-graded.jsonl` holds your answers plus
grades, so keep it out of public repos.) Repeat until the board
table is the board you want.

Saving the proposal is the point. A model's grouping varies from run to run;
the approved `shapes.csv` doesn't. Build once from the approved file and keep it
in version control next to brand.yaml.

The wording lives in [`scripts/plain_language.py`](../scripts/plain_language.py):
question-type names, a plain name and explanation per metric, the formula in
words, and the reason text. Edit it there to change what readers see, then run
`python3 scripts/build_template.py` to rebuild the template (and
`scripts/test_template.py` to check it). The spec vocabulary (shapes, verdicts)
stays in `plan.json` for the build agent.

## Reading the verdicts

What the proposal calls each verdict, and what it means:

| Verdict (plan.json) | In the proposal | Meaning | Build it? |
|---|---|---|---|
| ✓ keep | Worth tracking | the denominator projects to enough answers a week at full volume to read | yes |
| ○ at zero | Track only as a starting point | computable, readable base, and your numerator is 0 (never mentioned, never captured) | only if a zero is the baseline you're trying to move, e.g. a new brand or an experiment |
| ~ too thin | Too little data | fewer than 5 prompts in the group have a fitting shape, or the projected weekly base is under the metric's minimum | merge groups or skip |
| ✗ drop | Nothing to measure | nothing to count: no answer names you, so position has no denominator; no answer recommends a product, so capture has none | no |
| – unavailable | Can't measure yet | needs something you haven't got (a fact sheet) or no sample answers for these prompts | no, until you have it |

Sample numbers are **checks, not estimates**. They tell you whether a metric
will have a denominator worth reading. The proposal says so at the top, because
a "3 of 12" gets quoted as a 25% mention rate the moment it's on screen.

**The set verdict** reads the share of `none`:

- **full**: under 20% `none`. Build the board.
- **partial**: 20–50% `none`, or fewer than 15 prompts with a measurable shape.
  Build the groups that have a headline; don't pad the rest.
- **citations-only**: over 50% `none`. Build questions 5, 10 and 12. A thinned-out
  dashboard over prompts where no brand could be named would mislead.

**Unmet needs**: the proposer lists measurement needs it sees in your prompts
that no metric in the menu serves, and doesn't invent one. If a need matters,
design the metric yourself, write its denominator down, add it to
`metric-menu.json` and re-run.

## What the examples show

- [examples/stripe/proposal/](../examples/stripe/proposal/): 50 untagged payment
  prompts. The model proposed 8 groups; one prompt was moved by hand. Capture is
  the headline for 7 of 8 groups. That's the same conclusion the hand-built board
  reached, now with sample numbers: fraud & disputes is the weak group (37% of
  30), as it is on the live board.
- [examples/off-market/proposal/](../examples/off-market/proposal/): a
  deliberately awkward set for a Lisbon dental clinic, with five off-topic
  prompts mixed in. The model split out an "Outside the market" group as `none`,
  grouped the rest into three patient jobs, and corrected two prompts the word
  rules got wrong: "dentist near me open saturday" is a list prompt, not
  category. No sample was supplied, so every metric reads *unavailable*. That's
  the intended state before you export answers.
- On the Versoflip experiment set (53 feature prompts for a brand no AI has
  heard of), the proposer matched the hand labels and marked every
  brand-numerator metric *○ at zero*. That's correct: mention rate at 0% is the
  baseline the experiment exists to move.

## No terminal? Use a chat assistant

[with-mcp.md](with-mcp.md) (Ahrefs MCP server connected, the main path) or
[for-chat-assistants.md](for-chat-assistants.md) (without MCP): the assistant
pulls a whole day of answers, sorts the questions, counts what the answers say
and fills [report-template.html](report-template.html). It never designs the
page or picks the numbers itself.

## Prompts

The two prompts the model gets are in [proposer-prompt.md](proposer-prompt.md).
Paste them into a chat if you'd rather not run the script. The rules the
script applies afterwards are listed there too.
