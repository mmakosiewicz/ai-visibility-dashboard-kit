# 4 · Task recommendations: when AI suggests a tool for a task, does it recommend us?

## The question

"Someone asks *how do I do X* — the job our product does. Does the answer send
them to us, to a competitor, or to no tool at all?"

## Why it exists

This is the largest and most under-measured surface in AI visibility. Nobody
asks "best SEO tools" nearly as often as they ask "how do I find competitor
keywords" — and a how-to answer that names a tool is a product recommendation
delivered at the exact moment of need, without the user ever having considered
buying anything.

It's also the cheapest place to win, because the competition is often *nobody*:
plenty of answers explain a process and never name a tool at all.

## The prompts

Task phrasings for the jobs your product does:

```
how to do keyword research
how to build backlinks
how to find competitor keywords
how to audit a website
how to track rankings
how to fix crawl errors
```

Write them the way a beginner types them. No brand, no "best", no "tool" — the
whole point is to catch the answers where a tool is volunteered rather than
requested. Six to ten prompts covering your main jobs-to-be-done.

## What gets graded

This question needs **two extra fields** beyond the standard set, and they're
the reason it works:

| Field | Meaning |
|---|---|
| `tool_recommended` | does the answer tell the reader to use a **named** product for the task? |
| `tool_names` | the named tools it recommends; `[]` when false |

The grading instruction has to be precise about what counts, or this field is
noise. Mine:

> true only if the answer tells or suggests the reader to use a NAMED product,
> service, platform, app, extension, or software tool for the task; passing
> mentions and generic unnamed tools are false; free/default tools such as
> Search Console count

Two edge cases worth deciding explicitly: a free first-party tool (Search
Console, GA) **is** a named tool — excluding those flatters you; and a passing
mention ("tools like X exist") is **not** a recommendation.

## The metric

**Capture = answers recommending us ÷ answers recommending any named tool.**

The denominator is answers where a recommendation actually happened. Process-only
answers are *not* losses — nobody beat you, the model just explained a workflow.
Counting them against you makes you look defeated in prompts where there was no
contest, and the number then moves whenever models get more or less tool-happy.

Report alongside it:

- **tool-recommendation rate** = answers naming any tool ÷ all answers. This is
  the *opportunity size*, and it's a finding in its own right: the gap between
  it and 100% is how much of this surface is currently uncontested.
- overall mention rate and average position, for continuity with questions 2–3.

## What the card shows

```
headline:  capture · answers recommending a tool · overall mention · avg position
caption:   "N of M answers recommended a named tool; K of those included us.
            Process-only answers are not counted as losses."
table:     per prompt — prompt · answers · recommend a tool · recommend us ·
           capture · avg position
drilldown: which tools get recommended instead, per prompt
```

That caption is load-bearing. Without it, a capture figure gets read as "we
lose the rest of the how-to prompts", which is not what it says — most of the
rest had no tool recommendation at all.

## The action

- **High tool-recommendation rate, low capture** → a genuine competitive loss on
  a high-intent surface. Highest-priority content work on the board.
- **Low tool-recommendation rate** → the opportunity nobody is competing for.
  The play is content that makes naming a tool the natural answer for that task
  — which usually means being the source the answer is built from (question 5).
- **Capture high but position late** → you're the afterthought recommendation.
  Worth watching, not worth a project.

## How it lies

**Process-only answers are the whole trap.** This is the same denominator
mistake as [win rate](01-head-to-head.md), one level up: if your denominator is
all answers rather than all *recommending* answers, you are mostly measuring
model verbosity. I shipped it wrong first and the number was meaningless until
I split the two.

**Grading `tool_recommended` is genuinely hard.** It needs its own instruction
with examples, and it's worth version-stamping the field (`eval_version`) so you
can re-grade historical answers when you tighten the definition. I had to
backfill once already.

**A named tool isn't always a product.** "Use Google Search Console" and "use a
crawler" are different, and only the first counts. If your grader treats generic
category nouns as tool names, capture collapses for no real reason.
