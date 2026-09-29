# Prompt design

The prompt set is the instrument. Everything downstream — every metric, every
worklist — inherits its bias, so this is the part to get right before you write
any code.

## The short version

- **60–70 prompts**, tagged by question, is a working size.
- **Keyword-shaped, not conversational.** `best seo tools`, not "Hi, could you
  tell me what the best SEO tools are in 2026?"
- **One tag per prompt**, mapping it to exactly one research question.
- **No brand in the prompt** except where the question is explicitly about you
  (comparisons, pricing, reviews).
- **Freeze the set.** Every change breaks comparability; change it deliberately
  and date the change.

## Shape first

What a prompt *names* — your brand, a rival, nobody — decides which metrics its
answers can feed. That rule is in [shapes.md](shapes.md) and it is the one that
lets this spec run on a prompt set that isn't the one it was written for.

## Why keyword-shaped

The instinct is to write natural-sounding questions, because that's how people
talk to chatbots. I'd argue against it for a tracking set:

**Keyword phrasings are reproducible.** "best seo tools" is a stable stimulus.
A conversational prompt has a dozen equally plausible phrasings, and which one
you picked becomes an invisible confound in your own data.

**They isolate the variable you care about.** You're measuring how the *model*
answers a category question over time, not how sensitive it is to your
phrasing. Long prompts add variance you can't separate from real movement.

**They match how the data source indexes.** Brand Radar prompts carry search
volume, which lets you weight prompts by real demand — that only works if the
prompt looks like a query.

**They're comparable to search.** Being able to say "we're absent from the
prompt that has the highest search volume in the category" is a much stronger
statement than the same thing about a sentence you invented.

The trade-off, stated honestly: you are *not* measuring conversational
long-tail behaviour, which is a real and growing share of how people use these
tools. If that matters to you, run it as a **separate** set with its own card —
don't mix the two populations in one metric.

## Set size

| Question | Prompts | Why that many |
|---|---|---|
| 1 · head-to-head | ~10 | one `vs` + one `or` per major competitor |
| 2 · category | 5 | small and stable on purpose — this is your baseline |
| 3 · niches | ~30 | 5–6 per subgroup × 6 subgroups |
| 4 · task recommendations | ~6 | one per core job-to-be-done |
| 6 · fact fidelity | ~7 | price, plans, free tier, limits, feature list |
| 7 · narrative risk | 5 | enough to find the ceiling of negative framing |
| 8 · adjacent categories | ~5 | 2–3 per adjacent category |
| **total** | **~68** | × 7 surfaces ≈ 480 answers/day |

Questions 5, 9, 10 and 11 need no prompts of their own — 5 and 11 are computed
from citations, 9 and 10 from logs and pages.

**Why not more?** Cost scales with prompts × surfaces × days, and so does
grading. 68 prompts across 7 surfaces is roughly 480 answers a day, which is
enough that per-prompt numbers stabilise and small enough to grade daily
without thinking about the bill. Doubling the set buys less than you'd expect:
the variance that matters is between *prompts*, and you've already got coverage.

**Why not fewer?** Below roughly 5 prompts per question, one prompt flipping
moves the headline enough to trigger a false investigation.

## Tagging

Every prompt carries exactly one tag; the tag maps to `(question, subgroup)`.
That mapping lives in **one place** in your code:

```python
TAG_MAP = {
  "4642": ("q1-head-to-head",   "RQ1", None),
  "4644": ("q3-keyword-research","RQ3", "keyword research"),
  "4653": ("q8-social-media",    "RQ8", "social media"),
  ...
}
```

Two hard-won notes:

- **One tag per prompt.** Multi-tagged prompts land in two questions and get
  double-counted in any pooled metric. If a prompt genuinely belongs to two
  questions, it's two prompts.
- **Tags may arrive as ids from one endpoint and as names from another.** Keep a
  reverse map by name as well; assuming ids everywhere cost me a whole surface's
  data once.

Untagged answers should be stored but excluded from question metrics, and the
count surfaced somewhere. Silent exclusion is how you end up with a card that
quietly stopped covering a subgroup.

## Choosing prompts: the three tests

**Would a buyer type this?** Not a marketer, not you. If it contains your
product category *and* your brand *and* a qualifier, nobody typed it.

**Does it have demand?** Where you can attach search volume, do. A prompt with
no demand is a prompt whose answer nobody reads — fine to track, wrong to
prioritise.

**Does the answer imply an action?** If you can't say what you'd do when the
number moves, the prompt is trivia. This test kills about a third of candidate
prompts, which is the point.

## Freezing and changing the set

Treat the prompt set like a survey instrument:

- **Freeze it** once you start trending. Comparability across weeks is most of
  the value.
- **Additions are safer than edits.** A new prompt starts a new series; an edited
  prompt silently breaks an old one.
- **When you change it, date the change** and mark it on the charts. A metric
  step-change with no annotation will be investigated as a real event — once by
  you, and once by whoever inherits the dashboard.
- **Never remove a prompt because it looks bad.** That's how a dashboard becomes
  a reporting layer.

## Surfaces

Pull every AI surface your source supports, and store the surface on every
answer. Expect them to disagree substantially — per-surface mention rate spreads
are wide and real, and "which surface" is a legitimate filter for the whole
board.

Two practical warnings:

- **Be explicit about which surfaces you request.** An omitted model filter can
  silently default to a single surface, and you won't notice until a chart looks
  oddly smooth.
- **Not all surfaces come from one endpoint.** One of mine isn't available via
  the main read API at all and needs a separate raw call. Design the pull layer
  to merge sources into one answer shape, and record when one of them fails
  rather than failing the whole run.
