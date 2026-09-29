# Running step 0 in a chat assistant

**Connected to the Ahrefs MCP server? Use [with-mcp.md](with-mcp.md) instead.**
That's the main path for chat assistants. This page covers assistants without
MCP that can run Python or work from exported files.

For ChatGPT, Claude or any assistant working in a chat instead of a terminal.
The goal is the **same report** a script run produces
([report-structure.md](report-structure.md)), built from the whole data set
rather than a convenient slice of it.

The split of work: **you (the assistant) do the judgment**: sorting questions
and grading answers. **The script or the template does the arithmetic and the
page.** Most chat
assistants can run Python on uploaded files (ChatGPT's data analysis, Claude's
analysis tool). If yours can, use path A. If it can't, use path B.

## First: ask for the Brand Radar report

**Your first message to the user is a question, not a report.** Ask:

> Which Brand Radar report should I measure? Paste the report's URL or id.
> Also tell me your brand's name, website and main competitors, if they aren't
> already in the report.

Don't use example data, a report from an earlier conversation, or a report you
found yourself. Don't start until the user has named one. If you have no way to
read the report (no Ahrefs API access or connector), ask the user to export it:
the report's custom questions, and one day of answers from every AI surface it
tracks.

## Then: get the whole data set

The common failure is building a report from one page of results. Before
sorting or counting anything:

1. **Pull every answer for one whole day** (yesterday; today's scans may not
   be finished). With the Ahrefs API that's
   `GET https://api.ahrefs.com/v3/brand-radar/ai-responses` with
   `report_id=<id>`, `prompts=custom`, `date=YYYY-MM-DD`,
   `select=question,response,links,last_updated`, `limit=1000`, once per
   `data_source` (chatgpt, gemini, perplexity, copilot, google_ai_overviews,
   google_ai_mode, grok, claude). Surfaces that return nothing aren't tracked
   on the report; drop them. If Python is available, `scripts/fetch_report.py`
   does all of this.
2. **The question list is the distinct questions in those answers.** If a
   question appears twice for one surface, keep the most recently updated
   answer. Expected count =
   questions × AI surfaces × days. Say the number you got and the number
   expected. **Stop if they don't match.**
3. **Only the report's own questions.** Always pass `prompts=custom` with the
   report id. Without it, the API mixes in answers to Ahrefs' public question
   set.
4. **Never sort by search volume to pick a sample.** High-volume questions are
   the broad "best X" ones where every brand is named, so they inflate every
   rate. Use whole days instead.

## Path A: you can run Python

1. Upload or clone this repository.
2. If you can reach the Ahrefs API, run `python3 scripts/fetch_report.py --report <url-or-id>`
   with `AHREFS_API_KEY` set. It writes `report/<id>/` with `prompts.csv`,
   `answers.jsonl` and `brand.yaml`, and prints the count check. Otherwise
   write those three files yourself: `brand.yaml` from
   [`../08-adapting/brand.yaml`](../08-adapting/brand.yaml), `prompts.csv` with a
   `query` column, `answers.jsonl` with one line per answer (`question`,
   `model`, `date`, `response`, `sitelinks` as a list of `{url}`).
4. **Sort the questions yourself.** Follow both prompts in
   [proposer-prompt.md](proposer-prompt.md). Write `shapes.csv` with the columns
   `prompt, group, shape, reason, group_description`. `shape` must be one of
   `branded, conquest, list, task, category, none`. Name groups in the user's
   terms, 5+ questions each.
5. **Grade every answer yourself** with the grader in
   [`../08-adapting/grader-template.md`](../08-adapting/grader-template.md),
   filled from brand.yaml. Add the fields to each line of `answers.jsonl`:
   `mentioned, position, brands, tool_recommended, tool_names,
   verdict_winner, sentiment`. `verdict_winner` is null unless the answer
   picks one winner overall. That's expected and correct.
6. Run:

   ```
   python3 scripts/propose.py --from-report report/<id>/ --from-shapes shapes.csv
   ```

   No API key needed: with `--from-shapes` and pre-graded answers, the script
   calls no model.
7. Give the user `report/<id>/proposal/proposal.html`: that's the report. `proposal.md` is
   the same in Markdown; `plan.json` is what gets built from.

## Path B: you can't run code

Sort and read the answers as in path A, count as in
[with-mcp.md](with-mcp.md) step 4, write the measurements object
([measurements.md](measurements.md)) and put it into
[report-template.html](report-template.html). The template computes the rest,
so don't build the page by hand.

## Checklist before you show the report

- [ ] The user named the Brand Radar report; nothing came from example or earlier data
- [ ] Answer count matches questions × surfaces × days
- [ ] Only the report's own questions (`prompts=custom`) and surfaces it tracks
- [ ] Every question has a type and a topic; topics have 5+ questions
- [ ] No metric shown for a question type that doesn't allow it
- [ ] Win rate counts only answers that name the brand **and** pick one
      winner. "Named first" is not a win
- [ ] Mentions: the brand's name in the answer's text, not only in a link
- [ ] The page is report-template.html (or propose.py's proposal.html), unchanged apart from the data
