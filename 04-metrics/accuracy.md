# Accuracy metrics

Powers [question 6](../01-questions/06-fact-fidelity.md). The metric is simple;
the populations are not.

## Definition

```
checkable  = claims with verdict in (consistent, contradicted)
wrong      = claims with verdict = contradicted

wrong_claim_rate = wrong / checkable
```

Computed **separately for provoked and unprovoked** claims. Never pooled.

## Claim-based, not answer-based

Rate over *claims*, not answers. One answer about pricing can make a dozen
checkable claims; one comparison answer might make one in passing. An
answer-based rate ("% of answers containing an error") is dominated by answer
length.

Report the answer-level count too — "wrong facts appeared in N of M answers" —
because that's the number that describes reader exposure. Two different
statements, both worth having:

- **claim rate** — how accurate the model is when it states a fact about you
- **answer count** — how many readers encountered a wrong fact

## Why provoked and unprovoked can't be pooled

- **Provoked**: prompts that ask about pricing and plans. A wrong number is
  half-expected; the reader is shopping and may verify.
- **Unprovoked**: a wrong fact volunteered inside a comparison, a category list,
  a how-to. Nobody asked, so the reader has no reason to doubt it.

The populations differ structurally: provoked answers make *several times* more
claims each than unprovoked ones. So a pooled rate mostly tracks the mix of the
two populations in your sample, and it will move when you add a pricing prompt.

Two rates, side by side, each with its own claim count. The unprovoked one is
the more alarming number and the one people haven't seen before.

## Excluding `unverifiable` from the denominator

`unverifiable` means your fact sheet is silent on the point — not that the model
was wrong. Including those in the denominator measures your sheet's coverage,
not the model's accuracy.

Report the `unverifiable` count separately as exactly that: **a fact-sheet
coverage signal.** A rising unverifiable count is a to-do for your review
queue, not a visibility finding.

## Severity, and why the headline should be hard errors

```
hard = a wrong checkable specific — wrong price, wrong plan name, wrong numeric
       limit, a feature claimed that doesn't exist (or denied that does)
soft = wording/framing dispute where the substance is close — e.g. calling
       fair-use limits "unlimited", a loose paraphrase of what a tier includes
```

Soft errors are real but not urgent, and they dominate by count. If your
headline is "contradicted claims", the number is mostly framing quibbles and
people learn to ignore the card. Lead with **hard errors**; keep soft ones one
click down.

Useful pair to display:

- `hard_rate_of_claims` = hard ÷ all checkable claims — the honest error rate
- `hard_share_of_wrong` = hard ÷ contradicted — how serious the errors are

## Error lifecycle, not error list

Because claims carry a stable fingerprint
([data model](../03-data-model/README.md#claim-identity)), the same error is
joinable across days. That turns a list into a lifecycle:

| Status | Meaning | Response |
|---|---|---|
| `new` | first seen in this run | triage |
| `persisting` | seen before, same surfaces | already on the list — is the fix live? |
| `spreading` | now appearing on more surfaces or prompts | escalate |
| `resolved` | previously seen, now absent | verify, then close |

"This error is three weeks old and spreading" is a materially different
statement from "we found 12 errors today", and only the lifecycle version
survives contact with a content team.

## Per-prompt accuracy

Which prompts produce the most wrong facts, ranked. Almost always concentrated —
pricing-shaped prompts dominate — but the outliers are the useful part: a
*comparison* prompt producing wrong pricing claims means a source page in that
comparison's citation set carries the error.

That's the join worth building: **per error, the pages cited in the answers
containing it.** It turns "AI says the wrong price" into a list of suspect pages.

## Suspect vs cause

Two different claims about a page, and conflating them produces bad outreach:

- **Suspect** — the page was cited in an answer that contained the error.
  Cheap, derived from citation data, frequently wrong.
- **Cause** — the page *actually states* the wrong thing. Requires fetching the
  page and checking, with a verbatim quote as evidence.

Verdicts worth storing per (claim, page): `states` / `contradicts` / `silent` /
`unclear`. The `contradicts` case is the important one — the page *refutes* the
claim, so it's evidence in your favour, and I once read a pile of those as the
page being the source of the error. See
[`07-gotchas/page-next-to-a-claim.md`](../07-gotchas/page-next-to-a-claim.md).

## Cost control

Two mechanisms, both necessary at daily cadence:

1. **Answer hash** — an unchanged answer reuses its grading entirely.
2. **Verdict cache** keyed by `(fingerprint, factsheet_version)` — a claim
   already judged against this sheet version is never re-billed, even if it
   appears in a new answer.

The second is what makes a claims-level fact check affordable, because the same
handful of claims recur constantly across surfaces and days.
