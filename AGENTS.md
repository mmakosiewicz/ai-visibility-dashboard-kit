# Agent instructions

This repository is a measurement spec for building an AI-visibility dashboard
from **one specific Ahrefs Brand Radar report**. It is not a dashboard template,
and its examples are not data you can use.

## Which job are you doing?

- **Proposing what to measure (step 0).** In Claude, ChatGPT or another chat
  with the Ahrefs MCP server: follow
  [`09-proposal/with-mcp.md`](09-proposal/with-mcp.md). You are the grader; no
  API keys are needed. In a terminal: `python3 scripts/propose.py`
  ([`09-proposal/README.md`](09-proposal/README.md)).
- **Building the dashboard.** Only after step 0 is approved. Follow
  [`BUILD-WITH-AN-AGENT.md`](BUILD-WITH-AN-AGENT.md).

## Before writing any dashboard code

All four must be true. If one isn't, stop and say exactly what's missing.

1. **The user named the report**: its URL or id. If they haven't, ask. Your
   first message is that question.
2. **It was read from the report itself**, through the Ahrefs MCP server, the
   API or an export the user supplied, and the count check passed: answers ≈
   questions × AI surfaces for a whole day.
3. **The user confirmed** the brand, its name variants, its domain and the
   tracked competitors.
4. **The user approved the proposal**: the question topics and types, and which
   numbers to track. The build reads it as `plan.json`. If step 0 ran through
   MCP, turn its result into build files first. That needs no model and no
   key:

   ```
   python3 scripts/from_measurements.py <report.html or measurements.json> --out report/<name>/
   python3 scripts/propose.py --prompts report/<name>/prompts.csv --brand report/<name>/brand.yaml \
       --from-shapes report/<name>/shapes.csv --no-llm --out report/<name>/proposal
   ```

   Fill in the rest of `report/<name>/brand.yaml` before building.

The order is always **report → answers → proposal → approved plan → build**.
Never go from reading the spec straight to designing a dashboard.

## Never invent project data

Don't make up, guess or carry over from another project:

- report ids, questions, competitors or tracked AI surfaces
- answer text, citations or metric values
- topics, question types or `plan.json` contents

The examples show the method. They are never fallback data, and neither is
anything from an earlier conversation. **Synthetic data only when the user asks
for a demo or mockup**, and then labelled as such on the page and in what you
hand over.

## While building

- Treat `plan.json` as the build config: build only what it marks as worth
  tracking.
- Store every answer with its cited sources, not just computed scores.
- Read [`07-gotchas/`](07-gotchas/) before writing rankings, worklists, alerts,
  citation metrics or brand matching.
- The rest (which question types a metric applies to, showing what each
  percentage is out of, drill-downs to the questions) is in the spec. Follow it
  rather than restating it.

## Handing over something to view

If you deliver a page or dashboard to look at in a chat (Claude artifact,
ChatGPT canvas), also deliver a **self-contained `preview.html`**: all CSS and
JavaScript inline, no sibling files, no local server, demo data labelled. Chat
viewers can't load other files, so a multi-file project shows as a blank page.
Check the preview on its own before saying it works. The step 0 report is
already self-contained
([`09-proposal/report-template.html`](09-proposal/report-template.html)).
