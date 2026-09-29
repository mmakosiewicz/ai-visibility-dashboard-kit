# 6 · Fact fidelity: is what AI says about our features and pricing true?

## The question

"When AI states our price, our limits, what's in which plan — is it right?"

## Why it exists

Of everything on the board, this is the question whose findings have an
unambiguous owner and an unambiguous fix. A wrong price is not a positioning
debate; it's a wrong number on a page someone can go correct. It's also the
finding Sales feels most: a prospect arriving with a wrong number in their head
is a worse starting position than a prospect arriving with none.

## Why it's the hardest card to build

Every other question grades an answer against *itself*. This one grades it
against **ground truth**, which means you need a maintained fact sheet — and the
fact sheet, not the grader, is what determines whether the card is trustworthy.
Budget most of the effort there.

## The prompts

Two populations, and keeping them apart is the core design decision.

**Provoked** — prompts that ask about price and plans directly:

```
ahrefs pricing
what does ahrefs cost
ahrefs monthly plans
ahrefs free plan
compare ahrefs plans
ahrefs feature list
what does ahrefs api cost
```

**Unprovoked** — every *other* question's answers. A wrong fact volunteered
inside a comparison or a how-to, where nobody asked about pricing.

The distinction matters because the reader's posture is different. In a provoked
answer the reader is shopping and half-expects to verify. In an unprovoked one
they're reading a wrong number in passing and have no reason to doubt it. Same
error, very different damage — and my first version could only see the provoked
half.

## The fact sheet

Non-negotiable properties, all learned the hard way:

- **Human-approved, not scraped.** The grader only ever sees facts a person
  approved. Two failure classes proved this: marketing positioning copy graded
  as checkable truth, and two quote-accurate facts that contradicted each other
  (an FAQ vs a pricing table). Quote-anchoring catches neither; a human reading
  a diff catches both.
- **Every fact carries a source quote and URL**, substring-verified against the
  source.
- **Facts are versioned**, and the version is stored on every verdict. Otherwise
  you can't tell a real change from a sheet edit.
- **An authority order.** A parsed plan/price table outranks prose when they
  disagree.
- **Review queue, not auto-apply.** New/changed facts land as `pending` and get
  approved or rejected by a person.

## What gets graded

Per answer, the LLM extracts **claims** and verdicts each one:

```
{"claims": [{"claim": str,
             "verdict": "consistent" | "contradicted" | "unverifiable",
             "severity": "hard" | "soft",
             "fact_ids": [str],
             "note": str}]}
```

The verdict rules carry all the weight. The ones that made the difference:

- **Silence is not contradiction.** If the sheet says nothing on the point, the
  verdict is `unverifiable`, never `contradicted`.
- **Existence vs tier.** "X has feature F" and "F is in plan P" are different
  claims. A sheet entry showing F exists in *any* plan confirms the existence
  claim; it can only contradict a claim that names a specific plan wrongly.
  Never use tier availability as evidence against an unscoped existence claim.
- **Positioning is not checkable.** "Plan X is for freelancers" is paraphrased
  marketing copy, not an error. Exclude audience claims entirely unless they
  assert something countable, like a seat limit.
- **Currency and billing period.** A correct price in another currency, or an
  annual-billing figure, is consistent — not an error.
- **Severity:** `hard` = a wrong checkable specific (price, plan name, numeric
  limit, a feature that doesn't exist). `soft` = wording or framing dispute
  where the substance is close.

Without those rules you get a card full of false positives, people stop
believing it, and the whole thing is dead.

## Claim identity — the part that makes history possible

Each claim needs a **fingerprint** so the same error recognised across days
collapses to one identity: normalised claim text (numbers preserved — `$249`
and `$279` must stay distinct) **plus** the sorted fact ids it was judged
against.

That one field buys you three things:

1. **A verdict cache.** A claim already judged against this sheet version is
   never re-billed to the LLM. This is most of the cost control.
2. **Error lifecycle** — first seen, last seen, still present. Which turns the
   card from "here are today's errors" into "this error is three weeks old and
   spreading".
3. **Per-prompt accuracy** that survives rewording.

## The metric

**Wrong-claim rate = contradicted claims ÷ checkable claims**, computed
**separately for provoked and unprovoked** — never pooled. Provoked answers make
several times more claims each than unprovoked ones, so a pooled rate mostly
tracks the mix of the two.

Also: hard vs soft counts, unverifiable count (a fact-sheet coverage signal,
not an error signal), and the error lifecycle table.

## What the card shows

```
headline:  wrong-claim rate (provoked) · wrong-claim rate (unprovoked) ·
           hard errors · claims checked
table 1:   the wrong claims, hard first — claim · verdict note · where it
           appeared · which fact it contradicts
table 2:   error lifecycle — first seen · last seen · still present · severity
extra:     link to the fact-sheet review queue
drilldown: per error, the pages cited in the answers that contained it
```

That last drilldown is the bridge to a fix: it turns "AI says the wrong price"
into "these pages were cited alongside the wrong price".

## The action

- **Hard error on our own page** → fix the page. Fastest win on the board.
- **Hard error traced to a third-party page** → outreach with the correction.
- **Same error across many surfaces** → the source is probably one widely-cited
  page; find it before writing anything.
- **Lots of `unverifiable`** → your fact sheet is thin, not AI being vague. Feed
  the review queue.

## How it lies

**A page cited next to a wrong claim is a lead, not a verdict.** Often that page
is the one *correcting* the error. Read the claim direction before putting
anyone on an outreach list:
[`07-gotchas/page-next-to-a-claim.md`](../07-gotchas/page-next-to-a-claim.md).

**Wrong-claim rate is sensitive to prompt mix.** Add three pricing prompts and
the provoked rate moves with no change in reality. Keep the prompt set stable,
and when you change it, mark the date on the chart.

**Your own pages contradict each other more than you think.** An FAQ saying one
thing and a pricing table saying another will produce "errors" that are really
your own inconsistency. That's a finding, not a false positive — but it belongs
to your content team, not to AI.
