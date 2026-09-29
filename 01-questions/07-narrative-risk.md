# 7 · Narrative risk: is AI amplifying negative narratives about us?

## The question

"When someone asks whether we're worth it — or googles our bad reviews — what
story does AI tell?"

## Why it exists

Facts can be corrected (question 6). Narratives can't; they can only be
answered. "It's expensive", "the learning curve is steep", "the cheap plan is
too limited" — these aren't errors, they're positions, and knowing which ones AI
has adopted tells Sales what objection is arriving before the call starts.

This is the most useful card for enablement and the least useful for reporting.
Don't put it in a board deck; put it in objection handling.

## The prompts

Deliberately adversarial. You are asking the model to criticise you:

```
ahrefs review
is ahrefs worth it
ahrefs bad reviews
cheaper than ahrefs
ahrefs alternatives
```

Five is enough. Two design notes:

- **`<brand> bad reviews` is the point.** A neutral prompt set will tell you
  sentiment is fine. This set finds the ceiling of how negative the answers get
  when the user is already sceptical — which is the case that matters.
- **`alternatives to <us>`** sits here rather than with category prompts,
  because the asker has already decided to leave. The interesting output isn't
  the sentiment, it's *which* alternative is offered and on what grounds.

## What gets graded

| Field | Meaning |
|---|---|
| `sentiment` | positive / neutral / mixed / negative, toward us |
| `negative_themes` | short phrases naming each criticism stated |
| `negative_quotes` | **verbatim** sentences from the answer carrying the criticism |

The quotes are the deliverable. A theme list tells you "pricing" is a problem;
a verbatim quote tells enablement exactly what sentence a prospect read.

**Verify quotes programmatically.** Models paraphrase when asked to quote. Keep
only quotes that appear verbatim in the answer text (normalised substring
match — unify quote marks, dashes and whitespace first, then drop anything that
doesn't match). Without that check you'll publish a "quote" the model invented,
and one such quote in an enablement doc destroys trust in the whole card.

## The metric

**Negative rate = answers with `negative` or `mixed` sentiment ÷ all answers**
for these prompts.

Counting `mixed` as negative is a judgement call, and I'd defend it: a "mixed"
answer about a paid tool is an answer containing an objection. Whatever you
choose, write it on the card — this is exactly the metric people quote without
its definition.

Also track the **theme frequency table** (which criticism appears how often) and
**sentiment composition over time** (the full positive/neutral/mixed/negative
mix, not just the negative share — composition shifts are more informative than
the single rate).

## What the card shows

```
headline:  negative rate · answers · distinct themes
table 1:   themes by frequency — theme · count · which prompts and surfaces
table 2:   narrative sources — citation split for these answers specifically,
           and the pages cited most in the answers that were negative
drilldown: per theme, the verbatim quotes with prompt + surface
```

The "narrative sources" table is what makes this card actionable rather than
depressing: it separates criticism the models generate from criticism they are
*reading off a specific page*. Rank those pages by appearances in negative
answers, not by total citations.

## The action

- **A theme that's factually wrong** → it's a question 6 problem; move it there
  and fix the source.
- **A theme that's true** → enablement. Objection handling, with the verbatim
  quote as the thing being answered.
- **A UGC page driving a theme** → the hardest category. Sometimes a community
  response is appropriate; often the right move is content that answers the
  objection so well the models prefer it as a source.
- **A competitor page driving a theme** → counter-content.

## How it lies

**You chose adversarial prompts, so the negative rate is high by construction.**
This number is not "how negative is AI about us" — it's "how negative does AI
get when the user is already sceptical". Reported without that framing it looks
like a crisis. Never compare it to a neutral prompt set's sentiment.

**Sentiment is per-answer, not per-mention.** An answer can praise you in one
sentence and criticise you in the next. `mixed` is doing real work; don't
collapse it to a binary.

**Theme extraction drifts.** The model will phrase the same criticism three
ways across a week ("expensive", "pricey", "costs more than competitors"),
splitting one theme into three rows. Normalise to lowercase at minimum, and
review the theme list periodically — the long tail is usually the same handful
of complaints rewritten.

**A criticism is not a finding until it's repeated.** One negative answer on one
surface on one day is noise. Wait for the theme to appear across surfaces before
routing it to enablement.
