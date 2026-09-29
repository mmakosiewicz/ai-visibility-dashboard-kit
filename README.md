# AI visibility dashboard kit

A free guide and toolkit that looks at the questions you track in AI
assistants, tells you which numbers are worth putting on a dashboard, and then
helps a coding agent build that dashboard for you. It works from
[Ahrefs Brand Radar](https://ahrefs.com/brand-radar) data.

## What it does

Most AI visibility dashboards show the same numbers for every question, whether
or not they make sense. This starts from your own list of tracked questions.

You give it a Brand Radar report. It pulls the questions you track and a day
of the answers AI assistants gave, and asks you for your brand and competitors.

It then does four things:

1. **Groups your questions into topics** in your own terms ("choosing a
   treatment", "finding a specialist"), not a generic template.
2. **Works out what kind of question each one is.** Some ask for a
   recommendation, some ask how to do something, some just want information.
   That decides what you can measure. Your brand can only "win" a question that
   asks for a recommendation. On a general information question AI rarely
   recommends anyone, so the useful number there is how often your website is
   cited as a source.
3. **Tests every metric on real answers.** Each one is labelled *worth
   tracking*, *too little data* or *nothing to measure*, with the calculation
   shown: "mention rate = answers that name you ÷ all answers = 23 ÷ 32".
4. **Hands the approved plan to a coding agent**, with the rest of this guide:
   how to store and grade answers, how each metric is calculated, and the
   mistakes that make AI visibility numbers wrong.

The numbers in the proposal come from a small sample. They show whether a
metric is worth tracking, not what its real value is.

**Example.** On a 66-question report for a cancer charity, the proposal took
about three minutes and a few cents. Only one topic turned out to be a real
contest between organizations: there the charity was named in 72% of answers.
The other 47 questions were medical information questions where AI recommends
no one, so the number worth watching was how often the charity's website was
used as a source (3–7%).

## Start here

Everything starts from a Brand Radar report with custom questions: yours,
named by you. Agents working in this repo follow [`AGENTS.md`](AGENTS.md),
which forbids building from guessed or example data.

**Using Claude, ChatGPT or another assistant connected to the
[Ahrefs MCP server](https://docs.ahrefs.com/docs/mcp/reference/introduction)?**
This is the main path. Give it this repo and tell it: *"Follow
09-proposal/with-mcp.md."* It asks which report to measure, pulls a whole day
of answers through MCP, sorts the questions, counts, and gives you the report,
either as a file or as a block you paste into the
[report page](https://mmakosiewicz.github.io/ai-visibility-dashboard-kit/09-proposal/report-template.html).
It has the same layout, labels and rules as the script path below, because
both fill the same template
([`09-proposal/report-template.html`](09-proposal/report-template.html)).
**No API keys:** Claude or ChatGPT does the sorting and grading itself, and the
Ahrefs connection is the MCP sign-in you already did.

**In a terminal** (unattended runs, or scheduling it), with an Ahrefs API key
with Brand Radar access:

```
export AHREFS_API_KEY=...        # Ahrefs → Account settings → API keys
python3 scripts/propose.py
```

It asks which report to measure (paste its URL or id) and pulls one whole day of
answers from every AI surface the report tracks. It checks that none are
missing, then asks for your brand and competitors. After that it sorts the
questions, grades the answers and writes the report into
`report/<id>/proposal/`:

- `proposal.html`: the report, one page in a [fixed layout](09-proposal/report-structure.md)
- `proposal.md`: the same in Markdown
- `shapes.csv`: edit this to re-sort questions
- `plan.json`: what the coding agent builds from

Here there's no chat assistant to do the sorting and grading, so the script
calls a model itself and needs its key (`OPENAI_BASE_URL`, `OPENAI_API_KEY`,
`--model`). Only this path needs one. The two steps can also run separately: `scripts/fetch_report.py`
pulls the report, and `scripts/propose.py --from-report report/<id>/` writes the
proposal.

**A chat assistant without the Ahrefs MCP server** can follow
[`09-proposal/for-chat-assistants.md`](09-proposal/for-chat-assistants.md)
instead. What the proposal found on real reports is in
[`10-case-studies/`](10-case-studies/).

## Where it comes from

I built the original dashboard for our Sales team. It tracks twelve questions
across seven AI surfaces, grades every answer, and turns the result into
worklists someone can act on. This repo is everything except my data: the
questions, the question types, the schema, the metric definitions, the card
layout, the pipeline, and the four traps that made my numbers wrong before I
caught them. What carries over to your brand is the method, not the cards: the
two [case studies](10-case-studies/) produced 16 cards on one report and 7 on another.

## Why a spec instead of code

The dashboard is ~9,000 lines welded to one Brand Radar report id, one Web
Analytics project, an internal fact sheet and an internal app framework. Handing
you that repo would give you a thing that doesn't run. Handing you the spec
gives you the part that took the longest to get right — deciding *what to
measure* and *how not to fool yourself* — in a form you can implement in
whatever stack you already use, or hand to a coding agent.

## What you need before you start

| Requirement | Why |
|---|---|
| Ahrefs Brand Radar report with **custom prompts** | the answer corpus every metric is computed from |
| API or connector access to that report | daily automated pulls; the UI alone won't do |
| Somewhere to store answers | Postgres in my build; any relational store works |
| An LLM with JSON output | grading answers into structured fields |
| *(optional)* Ahrefs Web Analytics | bot/crawl health — question 9 |
| *(optional)* A maintained fact sheet | fact fidelity — question 6 |

The first four are the real floor. Without answer-level storage and an LLM
grading pass you have a rank tracker, not an AI-visibility dashboard.

## Without an API key

With the Ahrefs MCP server you don't need any key: the assistant is the grader
(see above). If you already have the questions and answers as files, skip the fetch:
`python3 scripts/propose.py --prompts questions.csv --brand brand.yaml --answers answers.jsonl`.
For a free, instant check with no AI model at all, `scripts/fit_report.py` sorts
questions with fixed word rules. It works well on question sets like the
case studies and guesses on anything else. Then follow [`08-adapting/`](08-adapting/).

## Read in this order

| | |
|---|---|
| [`01-questions/`](01-questions/) | The twelve questions, one file each — the metric, the card, the action, and how each one lies. **Start here.** |
| [`02-prompts/`](02-prompts/) | Prompt design: taxonomy, **prompt shapes → valid metrics**, how many per question, tagging, and why prompts are keyword-shaped |
| [`03-data-model/`](03-data-model/) | The schema, as DDL. The most transferable thing in this repo |
| [`04-metrics/`](04-metrics/) | Every metric, its formula, and — the part that matters — its denominator |
| [`05-cards/`](05-cards/) | Card anatomy: headline → worklist → drilldown → action; plus the board chrome that isn't a card |
| [`06-pipeline/`](06-pipeline/) | Daily pull, grading passes, caching, refresh cadence, the 30-second wall |
| [`07-gotchas/`](07-gotchas/) | Four ways these numbers will mislead you (plus sample size). Read before you trust a chart |
| [`08-adapting/`](08-adapting/) | Fit report, `brand.yaml`, the grader as a template, headline-per-shape. **The procedure for a report that isn't mine** |
| [`09-proposal/`](09-proposal/) | Step 0: an LLM reads your prompts, proposes groups, shapes and metrics from a fixed menu, and checks each on sample answers. Readable proposal + editable shapes.csv + plan.json |
| [`10-case-studies/`](10-case-studies/) | What happened on real reports: [SEO tools](10-case-studies/seo-tools.md) (194 prompts, 16 cards) and [payments](10-case-studies/payments.md) (50 prompts, 7 cards), same spec, different dashboards, and why. Reading only: no data to run |
| [`BUILD-WITH-AN-AGENT.md`](BUILD-WITH-AN-AGENT.md) | Hand this spec to a coding agent and get your own dashboard |

## The one-paragraph version

Pick 60–70 prompts that represent how buyers actually ask about your category.
Tag each prompt with the question it answers, and know each prompt's shape —
what it names decides which metrics its answers can feed. Pull every AI answer daily across
every surface you can get, and store the answer text plus its cited sources —
never just a score. Grade each answer once with an LLM into structured fields
(mentioned, position, brands named, sentiment, winner, criticisms). Compute
metrics per prompt, never only in aggregate. Then build cards that end in a
worklist, because a dashboard that doesn't tell someone what to fix is a
reporting obligation, not a tool.

## Scope and honesty notes

- **No sample data.** There are no question lists, answers or plans to run: every
  build starts from your own Brand Radar report, and the scripts and report page
  refuse input that doesn't name one. The handful of numbers in the case studies
  are one week of one report, there to show the shape of the output.
- **Ahrefs-specific by design.** Brand Radar is the data source, named
  throughout. Most of the spec (schema, metrics, card anatomy, gotchas) is
  source-agnostic and portable; questions 9 and 11 lean on Ahrefs specifically.
- **Twelve questions is my answer on my prompt set, not the answer.** The
  payments case supports seven. [`scripts/fit_report.py`](scripts/fit_report.py)
  tells you how many yours supports; [`01-questions/README.md`](01-questions/README.md)
  says which to build first.
- **Written from a running system.** Every metric definition, grading prompt and
  schema decision here is what the live dashboard does, including the parts that
  were wrong first. Where a decision has a date attached, that's when it changed
  and why.
