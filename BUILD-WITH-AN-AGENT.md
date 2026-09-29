# Build it with a coding agent

Realistically, nobody is going to port someone else's 9,000-line dashboard. But
handing this spec to a coding agent and getting your own is a couple of
afternoons — which is what the spec is shaped for.

## Before you start

Have these ready. The agent can't decide them for you, and getting them wrong is
what makes the rebuild wasted work:

| Decision | Notes |
|---|---|
| Your brand and its name variants | sub-brands, product lines, common misspellings |
| Your tracked competitor set | 5–8; drives cohort share of voice |
| Your sub-niches | one per product area or job-to-be-done |
| Your adjacent categories | areas you've entered, not areas you sell into |
| Brand Radar report with custom prompts | tagged per research question |
| API/connector access to it | and a token that works from your environment |
| Your approved proposal | from Claude/ChatGPT with the Ahrefs MCP server ([`09-proposal/with-mcp.md`](09-proposal/with-mcp.md), then `scripts/from_measurements.py`) or `python3 scripts/propose.py`, reviewed until the board table is right. Its `plan.json` is the build config. The fit report is the free, word-rule version of the same check |
| A filled `brand.yaml` | [`08-adapting/brand.yaml`](08-adapting/brand.yaml) (a commented template); the [case studies](10-case-studies/) describe what changes between brands |
| Which questions you're starting with | the ✓ rows of the fit report; if in doubt, [`01-questions/README.md`](01-questions/README.md#if-you-only-build-five) |

## Phase order

**0 · Propose.** [`09-proposal/`](09-proposal/). It starts by asking which
Brand Radar report to measure and pulling a whole day of its answers
(`scripts/fetch_report.py`). Then it sorts the questions, picks metrics from the
menu, checks them on those answers, and waits for your approval. Skip
it only if your prompts look like one of the case studies and the fit report
agrees with your own reading.

**Working in a chat assistant (ChatGPT, Claude) rather than a terminal?** With
the Ahrefs MCP server, follow [`09-proposal/with-mcp.md`](09-proposal/with-mcp.md);
without it, [`09-proposal/for-chat-assistants.md`](09-proposal/for-chat-assistants.md).
You sort the questions and count what the answers say. The report comes out of
[`09-proposal/report-template.html`](09-proposal/report-template.html), which
turns your counts into the fixed layout. Don't design your own dashboard at this
stage.

**Before phase 1**, the four checks in [`AGENTS.md`](AGENTS.md) must hold:
the user named the report, it was read and passed the count check, the brand
details are confirmed, and the proposal is approved. If step 0 ran through MCP,
`scripts/from_measurements.py` turns its result into the build files (see
AGENTS.md). Never fill gaps with example or made-up data. Synthetic data is
only for a demo the user asked for, and it's labelled.

Then build in this order. Each phase is independently useful, and stopping after any
of them leaves you something that works.

**1 · Storage + pull.** Schema from
[`03-data-model/schema.sql`](03-data-model/schema.sql), then a daily pull that
writes one snapshot of answers with their cited sources. No grading, no UI. The
deliverable is a table filling up every day — which already answers questions
you can't answer today, by hand, with SQL.

**2 · Grading.** Pass 1 from [`06-pipeline/grading.md`](06-pipeline/grading.md),
plus the answer-hash skip. Now you have mention rate, position, brands,
sentiment and winners.

**3 · Three cards.** Category, head-to-head, tasks. Four-layer anatomy from
[`05-cards/README.md`](05-cards/README.md). Resist building all twelve — three
cards used daily beats twelve that nobody opens.

**4 · Citations.** Question 5 and the citation metrics. No LLM needed, and it's
what turns "we're absent" into "here's whose content to get into".

**5 · Worklist.** [`05-cards/worklists.md`](05-cards/worklists.md). The point at
which the thing becomes a tool rather than a report.

**6 · The rest, on demand.** Add a question when someone asks something you
can't answer. That's the only good reason to add one. Question 12 (citation
attention) goes last — it pools citation history across every group, so it needs
weeks of data before it says anything.

**7 · Board chrome.** The KPI history strip, the always-populated status line and
the per-card Actions deep links — [`05-cards/board-chrome.md`](05-cards/board-chrome.md).
Cosmetic-sounding, and it's what makes the thing get opened daily.

## The prompt

Paste this, with the bracketed parts filled in:

---

I want to build an AI-visibility dashboard for my brand, following the spec in
this repo. Read `README.md` first, then `08-adapting/README.md`,
`02-prompts/shapes.md`, `01-questions/README.md`, `03-data-model/README.md` and
`05-cards/README.md` before writing any code.

My approved `plan.json` (from `scripts/propose.py`, edited by me) and brand.yaml
are pasted below. Read `09-proposal/README.md` first. The plan is the build
config: use its groups and prompt ids exactly, build only metrics with verdict
`keep` (and `floor` where I've said a zero is the baseline), use each group's
`headline` as the card's headline, and store each prompt's shape from
`shapes.csv` on the answer row. Do not re-classify prompts or add metrics that
aren't in the plan. If you think one is missing, tell me. Fill the grading
prompt from `08-adapting/grader-template.md` using my brand.yaml — do not copy
the Ahrefs-filled version.

[plan.json]
[brand.yaml]

Context:
- Brand: `[BRAND]`, name variants `[VARIANTS]`
- Tracked competitors: `[COMPETITORS]`
- Sub-niches: `[NICHES]`
- Data source: Ahrefs Brand Radar report `[REPORT_ID]`, custom prompts,
  `[tagged per research question | untagged — group per the mapping below]`
- Stack: `[e.g. Python + Flask + Postgres]`

Build phase 1 only: the schema from `03-data-model/schema.sql` (adapted to my
stack) and a daily pull that stores one snapshot of answers with their cited
sources. Do not build grading or UI yet.

Requirements I care about, all from the spec:
- store full answer text and cited sources, never only computed scores
- one snapshot per run; date ranges pool snapshots and never mutate rows
- `answer_hash = sha1(question|surface|response)` so unchanged answers can skip
  grading later
- a failed pull for one AI surface records the error on the snapshot and
  continues with the others
- keep `null` distinct from `[]` on any brand/mention field — read
  `07-gotchas/null-is-not-empty.md` and tell me where that applies in the schema
- store each prompt's shape (branded / conquest / list / task / category) on the
  answer row, so every metric can filter to the shapes it's valid for
- normalise cited URLs without dropping identifying query parameters (`?v=`)

When you're done, show me the row count per surface for one day and one sample
answer row, then stop.

---

Then, phase by phase:

> Phase 2: add the extraction pass from `06-pipeline/grading.md`, with the
> answer-hash skip and quote verification in code. Version-stamp any graded
> field whose definition might tighten.

> Phase 3: build the category, head-to-head and task cards using the four-layer
> anatomy in `05-cards/README.md`. Every ratio gets its denominator in the
> caption. Read `04-metrics/win-rate.md` and `04-metrics/capture.md` first —
> the denominators are the whole point.

## Make the agent read the gotchas

The single highest-value instruction you can give it:

> Before implementing any ranking, worklist or alert over cited pages, read
> `07-gotchas/` and tell me which traps apply to what you're about to build.

Those four traps are the parts an agent will otherwise reinvent — they're all
locally reasonable decisions that produce wrong numbers. Ranking pages by
citation count is exactly what a competent agent does by default.

## Review checklist

Whatever built it, check these before trusting a number:

- [ ] Does every number come from the user's own report? No example, earlier or
      made-up data (demo data only if asked for, and labelled)?
- [ ] If it's meant to be viewed in a chat, is there a self-contained
      `preview.html` that works on its own ([`AGENTS.md`](AGENTS.md))?
- [ ] Does every ratio show its denominator on screen?
- [ ] Is position computed **only** over answers where you're mentioned?
- [ ] Is win rate over **decided** comparisons only — and only on prompts where you're in the comparison?
- [ ] Does every card's headline metric match its prompts' shape (`02-prompts/shapes.md`)?
- [ ] Is cohort brand matching exact-token (no "squarespace" inside "square")?
- [ ] Are "rivals named instead of us" taken from recommended tools, not every brand the answer mentions?
- [ ] Is capture over **recommending** answers only?
- [ ] Are provoked and unprovoked accuracy reported **separately**?
- [ ] Is `null` kept distinct from `[]` on brand/mention fields?
- [ ] Do URL matches compare **host**, not path substrings?
- [ ] Is there a per-prompt view for every aggregate?
- [ ] Do operational cards say they ignore the global filters?
- [ ] Does every card end in something someone can do?
- [ ] Can you still recompute history if the grading prompt changes?
- [ ] Does any "citations" ranking say whether it means confirmed citations or
      source appearances?
- [ ] Does the KPI strip use a per-metric good/bad direction (up is bad for
      error rates)?

Any unchecked box is a number that will be wrong in a way nobody notices.
