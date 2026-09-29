# 3 · Niches: are we recommended in the sub-niches we care about?

## The question

"We're on the category list — but are we recommended for *keyword research*? For
*local SEO*? For the specific jobs buyers hire us for?"

## Why it exists

The category number hides everything. A healthy overall mention rate routinely
contains one sub-niche where you're strong and another where you're invisible,
and those need opposite responses. This is also where product-market reality
shows up first: the niches where you're absent are usually the ones where your
product genuinely is newer or weaker, and it's better to know that from the data
than from a lost deal.

## The prompts

Grouped into **subgroups** — one per sub-niche, 5–6 prompts each. My six:

```
keyword research      best keyword research tools · keyword research software ·
                      free keyword research tools · find keyword gaps ·
                      keyword tracking tools

web analytics         best web analytics tools · web analytics software ·
                      google analytics alternatives ·
                      website traffic analysis tools · analytics tool pricing

on-page               best on page seo tools · seo content editor ·
                      content optimization software · website audit tools ·
                      on page seo checklist

local SEO             best local seo tools · local seo software ·
                      local citation tools · local rank tracking software ·
                      google business profile tools

bot analytics         ai crawler analytics · bot analytics tools ·
                      track ai crawlers · ai bot traffic monitoring ·
                      identify bot traffic

AI visibility / AEO   best ai visibility tools · ai brand monitoring tools ·
                      aeo tools · geo tools · track brand in chatgpt ·
                      compare ai visibility platforms
```

Pick subgroups by **what you sell**, not by what's easy to prompt. One subgroup
per product area or per job-to-be-done. Note the mix: `keyword research` is a
mature area where we should win, `AI visibility` is a new one where the
incumbents are startups — the point of the split is that those two need
different reading.

Include at least one `free ...` and one `<category> software` phrasing per
subgroup; they surface different brand sets.

## What gets graded

Same fields as [question 2](02-category.md). The extra requirement is
structural: every answer must carry its **subgroup**, because the subgroup — not
the prompt, not the question — is the unit people act on.

## The metric

Per subgroup: **mention rate**, **average position (when mentioned)**, **prompt
count**, and **field share** (our share of all brands named in that subgroup's
answers).

Overall mention rate for the question exists, but treat it as a rollup for the
headline only. Every decision comes from the per-subgroup rows.

One extra column worth building: **platform coverage** — the *worst* per-prompt
count of surfaces that returned an answer. If any prompt in the subgroup loses
one surface, this drops from 7/7 to 6/7 immediately. It's how you catch a
collection gap that would otherwise look like a visibility drop.

## What the card shows

```
headline:  overall mention rate · avg position · answers
table:     one row per subgroup — subgroup · prompts · platform coverage ·
           mention % · position · field share · rank in field
drilldown: per subgroup, the per-prompt table (as question 2)
extra:     share of voice per subgroup, and search demand per prompt
```

The subgroup table is the card. It's the single most-used table on my whole
board, because it's the only view that says "here is the part of the market
where you don't exist".

## The action

- **A subgroup at low mention rate** → a positioning gap, not a content gap.
  Before writing anything, check question 5 to see whose content owns the
  subgroup — in new niches it's usually a startup's comparison page.
- **Strong in the niche, weak in the category** → you're a specialist in the
  models' eyes. Fine, if intended.
- **A niche where you're absent and have no product** → delete the subgroup or
  keep it explicitly as a market-watch row. Don't let it drag a headline number
  that Sales reads as performance.

## How it lies

**`answers` is prompts × surfaces.** A subgroup of 6 prompts across 7 surfaces
reports 42 answers, which looks like a big sample and isn't — it's 6 prompts.
Display prompt count next to answer count, or people will over-trust it. (I
shipped this wrong and it read as missing coverage.)

**Cohort share is meaningless in a young niche.** In `AI visibility` the real
players are startups nobody has in their tracked-competitor list. Use field
share — share of *all* brands named — or you'll report dominance in a niche you
just entered.

**Subgroups have wildly different prompt counts.** Pooling them into one number
means the largest subgroup silently becomes the metric. Never average across
subgroups; report them side by side.
