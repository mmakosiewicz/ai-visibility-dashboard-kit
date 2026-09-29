# The report's input: the measurements object

[report-template.html](report-template.html) is the one renderer every path
uses. Put this JSON in its `<script id="measurements">` block and open the file:
the page (labels, which numbers are worth tracking, main numbers, warnings) is
computed from it by the template itself. `propose.py` writes it for you
(`render_html.py --json` shows it). An assistant working over the Ahrefs MCP
server writes it by hand ([with-mcp.md](with-mcp.md)).

**Supply counts, not conclusions.** No percentages, no verdicts, no "main
number". The template derives all of those, which is what makes every run the
same.

```json
{
  "brand": "Acme",
  "report_id": "<the id from your report's address>",
  "generated": "2026-09-29",
  "classifier": "Claude via the Ahrefs MCP server",
  "surfaces": ["chatgpt", "gemini", "perplexity", "copilot"],
  "days": 1,
  "answers": 400,
  "answers_expected": 400,
  "cited_flag": false,
  "has_fact_sheet": false,
  "competitors": ["Rival One", "Rival Two"],
  "variants": ["Acme App"],
  "owned_domains": ["acme.com"],
  "competitor_domains": ["rivalone.com", "rivaltwo.com"],
  "category": "project management software",
  "groups": [
    {
      "name": "Choosing a tool for a small team",
      "description": "People comparing options before they buy.",
      "questions": [
        {"q": "best project tool for a 5-person team", "type": "list", "note": "", "answers": 4}
      ],
      "metrics": {
        "mention_rate": {"num": 23, "den": 32, "looked_at": 32},
        "citation_split": {"num": 13, "den": 236, "looked_at": 32,
                           "split": [["third-party", 180], ["ugc", 30], ["competitor", 13], ["owned", 13]]}
      }
    }
  ]
}
```

## Fields

| Field | What it is |
|---|---|
| `brand` | display name |
| `report_id` | **required**: the id of the user's Brand Radar report, from its address (`app.ahrefs.com/brand-radar/reports/<id>/…`). The page refuses to render without a real one, and prints it in the footer |
| `demo` | only for a demo the user explicitly asked for: `true` replaces `report_id`, and the page is labelled *made-up data* at the top and in the footer. `from_measurements.py` refuses demo data |
| `surfaces` | the AI surfaces that returned answers; only its length is used |
| `days` | whole days of answers used |
| `answers` / `answers_expected` | answers loaded, and questions × surfaces × days. The page warns when under 90% |
| `cited_flag` | `false` when links don't say whether they were actually cited (true of the public API and MCP). The page warns that source numbers read high |
| `has_fact_sheet` | whether a verified fact list exists; without it, "facts wrong" reads *can't measure yet* |
| `competitors`, `variants`, `owned_domains`, `competitor_domains`, `category` | the brand details the user confirmed. The page doesn't show them; `scripts/from_measurements.py` carries them into `brand.yaml` for the build. Without `competitors`, questions about competitors lose their type there |
| `groups[].questions[]` | every question in the topic: text `q`, `type` (`branded`, `conquest`, `list`, `task`, `category`, `none`), optional `note` if the type was hard to call (shown with ⚠), and `answers`, the number of answers it had |
| `groups[].metrics` | one entry per metric you measured, keyed by id |

## Each metric: which questions, and what num / den / looked_at mean

**Only count answers to questions whose type allows the metric**, per the
`shapes` list for each metric in [metric-menu.json](metric-menu.json). For
example, `win_rate` uses only `branded` and `list` questions. The template
checks the types and says "Based on 7 of 8 questions".

`looked_at` = how many answers you examined for this metric (the answers to
the eligible questions). It's used to project the count to a week. For the two
citation metrics it's the number of answers, not links.

| id | num | den |
|---|---|---|
| `mention_rate` | answers naming the brand **in their text** (a link to its site alone is a citation, not a mention) | all answers examined |
| `position` | **sum** of the brand's rank (1 = first brand named) across answers naming it | answers naming the brand |
| `top_three_rate` | answers where the brand's rank is 1–3 | answers naming the brand |
| `win_rate` | answers whose single overall winner is the brand | answers that name the brand **and** pick one winner overall. "Named first" is not a winner |
| `capture` | answers that recommend the brand as something to use or buy | answers that recommend any specific brand or organization |
| `tool_recommendation_rate` | answers that recommend any specific brand or organization | all answers examined |
| `cohort_sov` | mentions of the brand | mentions of the brand + tracked competitors (one per brand per answer) |
| `negative_rate` | answers negative or mixed about the brand | answers naming the brand |
| `owned_citation_share` | cited websites on the brand's domain | all cited websites, **each website counted once per answer** |
| `citation_split` | same as owned | same denominator; plus `split`: counts per group `owned`, `competitor`, `ugc`, `third-party` |
| `fact_accuracy` | omit unless you have a fact sheet | |

A metric you couldn't measure at all: leave it out. The template shows it as
*can't measure yet*. A metric you measured and got zero for: include it with
`num: 0`. The template treats that differently, and correctly.
