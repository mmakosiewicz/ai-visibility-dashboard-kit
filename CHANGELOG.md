# Changelog

## 2026-09-29 — no sample data

Agents sometimes used the shipped examples to skip the Brand Radar report. So:

- **`examples/` removed.** No question lists, brand files or plans ship any
  more. The two write-ups live on as reading-only
  [`10-case-studies/`](10-case-studies/), with the step 0 findings summarised.
- **Every report must name its Brand Radar report.** The report page refuses
  measurements without a real report id (`report_id`) and prints it in the
  footer; `propose.py` needs `--from-report`, `--report-id` or a fetch;
  `from_measurements.py` refuses input without one.
- **Demo data only when asked**: `--demo` / `"demo": true` labels the page
  "made-up data" at the top and in the footer, and can't become build files.
- `test_template.py` renders a tiny labelled fixture built inside the test,
  and checks both refusals.

## 2026-09-29 — renamed: AI visibility dashboard kit

Published under a new name, `ai-visibility-dashboard-kit`. Same content as the
last version of the measurement spec; links and the report footer point here.

## 2026-09-29 — agent rules and the MCP-to-build bridge

- **`AGENTS.md`**: rules that coding agents pick up automatically. Four checks
  before any dashboard code (the user named the report; it was read and passed
  the count check; brand details confirmed; proposal approved), never invent
  project data, synthetic data only on request and labelled, and a
  self-contained `preview.html` for anything viewed in a chat.
- **`scripts/from_measurements.py`**: turns an approved MCP proposal (the report
  page or its measurements block) into `prompts.csv`, `shapes.csv` and a
  starter `brand.yaml`. `propose.py --from-shapes --no-llm` then writes
  `plan.json` without re-sorting anything and with no key. Tested on the Stripe
  proposal: all 50 questions kept their topic and type.
- The measurements object can now carry the confirmed brand details
  (`competitors`, `variants`, domains, `category`), so questions about
  competitors keep their type in the build.
- README and BUILD-WITH-AN-AGENT.md point to AGENTS.md instead of repeating it;
  the build review checklist gains the no-invented-data and preview checks.

## 2026-09-29 — works through the Ahrefs MCP server

- MCP guide rewritten for chat limits: no `offset` paging (it repeats rows),
  split calls that hit the plan's row cap, server counts for answers, mentions,
  share of voice and citations over every answer, and a 2-question sample per
  topic for the six metrics that need reading. The report page also takes pasted
  measurements (hosted on GitHub Pages) and can save itself as a file.
- Docs now say plainly that the MCP and chat paths need no API keys: the
  assistant in the chat is the grader. The model key is only for the
  unattended terminal script.

- **`09-proposal/with-mcp.md`**: the main path for Claude, ChatGPT and other
  assistants connected to the Ahrefs MCP server. The assistant asks for the
  report, pulls a whole day with `ai-responses` (`prompts=custom`), checks the
  count, sorts and reads the answers, and fills the template. The MCP calls
  were checked through the equivalent public API endpoints, not through an MCP
  client.
- **`09-proposal/report-template.html`**: the report page is now one
  self-contained template that computes labels, main numbers and warnings from
  counts. `render_html.py` fills it, so the script and every assistant give the
  same page. Input format: `09-proposal/measurements.md`. Rebuild with
  `scripts/build_template.py`; check with `scripts/test_template.py`.
- **One mention rule everywhere**: a brand is mentioned when its name is in
  the answer's text. A link to its site alone is a citation. On a 50-question
  test report this matched Brand Radar's own mention matching answer for
  answer.
- **Citations count each website once per answer**, matching Brand Radar's
  cited-domains numbers.
- Fixed: `brand.yaml` lines like `products: []` were read as the terms `[` and
  `]`. That affected every report written by `fetch_report.py`.
- `--sorted-by` sets the footer credit when re-running from a reviewed
  `shapes.csv`.

## 2026-09-29 — it starts by asking for your Brand Radar report

- **`scripts/fetch_report.py`**: asks for a report URL or id and pulls it
  through the public Ahrefs API (`/v3/brand-radar/ai-responses`,
  `prompts=custom`). It finds the surfaces the report tracks, pulls one whole
  day of answers (yesterday by default), drops duplicate answers and checks the
  count against questions × surfaces × days. It asks for brand and competitors
  once and writes `report/<id>/`.
- **`propose.py` with no arguments** runs the fetch first; `--from-report`
  takes the folder. File inputs still work.
- `for-chat-assistants.md`: the assistant's first message asks which report to
  measure; no example or earlier data. Documents the exact API call.
- README "Start here" rewritten around the report.
- Known limit: the public API doesn't return the `cited` flag, so source
  numbers count every link.

## 2026-09-29 — same report, whoever runs it

A chat assistant given this repo built its own dashboard from 100
volume-sorted answers, used "named first" as win rate, and skipped the
question types. Three changes so every run produces the same report:

- **`proposal.html`**: `propose.py` now renders the report as one
  self-contained page (`scripts/render_html.py`), with the same structure as the
  reference Console view.
- **`09-proposal/report-structure.md`**: the report's sections, order, labels
  and metric formulas, for anyone reproducing it without the script.
- **`09-proposal/for-chat-assistants.md`**: the assistant sorts and grades,
  then runs `propose.py --from-shapes` with pre-graded answers (no API key).
  It starts with a data check: whole days, count = questions × surfaces ×
  days, scoped to brand and competitors, never a volume-sorted slice.
- `--from-shapes` now accepts a hand-written `shapes.csv` with no `plan.json`
  (optional `group_description` column).

## 2026-09-29 — plain-English proposals

- `proposal.md` rewritten for someone seeing it for the first time: no
  "shapes", "verdicts" or metric ids. Question types have plain names ("Asks
  for recommendations", "General question"); each metric has a plain name
  ("How often you're the top pick"), one sentence on what it tells you, its
  standard name, the formula in words and the sample's actual calculation
  (`Win rate = … ÷ … = 9 ÷ 13 = 69%`). Numbers not worth tracking sit in a
  collapsed list with the reason.
- `plan.json` metrics carry the same wording in a `plain` block, so a
  dashboard can reuse it.
- New `scripts/plain_language.py` holds all reader-facing wording.
- README opens with what the repo does, in plain English, and a worked
  example; `fit_report.py` is now the free fallback, `propose.py` the main path.

## 2026-09-28 — step 0: propose before you build

The word-rule classifier is a guess on any prompt set unlike the three it was
written on. New step that reads the user's prompts first:

- **`scripts/propose.py`** — an LLM groups prompts in the user's terms and assigns
  each a shape or `none`. Brand/competitor tokens override the model; the word
  rules cross-check it and disagreements are flagged. Metrics come from
  `09-proposal/metric-menu.json` (the shapes.md validity table as data), never
  from the model. Each eligible metric is computed on 1–2 days of sample answers
  and gets a verdict: keep / at zero / too thin / drop / unavailable.
- **Three outputs from one run**: `proposal.md` (readable), `shapes.csv`
  (editable; re-run with `--from-shapes`), `plan.json` (build config).
- **Set verdict**: full / partial / citations-only, from the share of `none`.
- **`09-proposal/`**: README, metric menu, the two proposer prompts.
- Worked outputs: `examples/stripe/proposal/`, and a new
  `examples/off-market/` (Lisbon dental clinic with off-topic prompts mixed in).
- `brand.yaml` gains `category` and `generic_tool` (the grader already needed
  both). `BUILD-WITH-AN-AGENT.md` now starts at phase 0 and passes `plan.json`
  to the agent instead of the fit report.
- First real run (a 66-prompt health-charity report) fixed three things: the
  model may no longer label a prompt branded/conquest unless it names a
  *tracked* brand (it tagged a drug name as a competitor); a group's headline
  prefers a metric that moves on the sample over one that reads 0 every day,
  and warns when none does; graded sample answers are saved to
  `sample-graded.jsonl` so the edit loop re-runs in seconds instead of
  re-grading.
- Win rate in the sample counts only decided verdicts **in answers that name
  you**. A rival winning an answer you're absent from isn't your loss.

## 2026-09-28 — prompt-shape classifier fix

Running `fit_report.py` on a third prompt set (53 feature-led product
prompts) labelled 33 as **category**. Two causes: the list regex matched
`which is|which one` but not a bare "Which standing desks…?", and product
finders with no marker word ("standing desks with a child lock") fell through.

- `which` alone, `top-rated`/`top picks`, `most used/popular/accurate`,
  `what tools` are now list markers. `top` alone is not (a desk *top*).
- New product-finder rule: a non-question noun phrase + `with/that/featuring…`
  → **list**.
- `vs`/`versus` removed from list markers: product comparisons are already
  branded/conquest, so the remainder is concept-vs-concept → **category**.
- `can I/you …` is a task marker; the `how/why/where …?` fallback now
  requires the question mark.
- Result: the third set goes from 29/53 to 51/53 agreeing with hand labels.
  Ahrefs example: 11 prompts moved (mostly category → list on "most accurate",
  "what tools"); Stripe example: unchanged.
- `scripts/test_classify.py`: 20 regression cases.

## 2026-09-28 — fork: dashboard spec → measurement spec

Prompted by running the original spec on a second report (payments, 50
untagged prompts, none naming the brand) and finding that most defaults were
consequences of the first prompt set, not principles.

- **`02-prompts/shapes.md`** — five prompt shapes and the metric-validity
  matrix. The rule that decides which metrics a prompt set may feed.
- **`08-adapting/`** — the procedure for a report that isn't the author's:
  `brand.yaml` (every brand-specific fact in one file), the grader prompt as a
  template with slots, fit-report-driven question selection, headline-per-shape.
- **`scripts/fit_report.py`** — offline: prompt shapes, answerable questions,
  entity-collision warnings, grading cost. Reads a CSV and brand.yaml.
- **`examples/`** — both prompt lists published; two READMEs recording what
  changed between the SEO-tools build and the payments build and why.
- Win rate eligibility rule added to `04-metrics/win-rate.md`; URL-normalisation
  rule added to `04-metrics/citation-metrics.md`; prompt-shape column and three
  checklist items added to `BUILD-WITH-AN-AGENT.md`; prerequisites column in
  `01-questions/README.md`.
- README reframed: the method transfers, the dashboard is its output.
