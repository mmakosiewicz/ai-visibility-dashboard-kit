# 4 · A page next to a wrong claim is a lead, not a verdict

**When you find a page cited in an answer that contained a wrong fact about you,
that page is frequently the one *correcting* the error — not the source of it.**

## Suspect vs cause

Two different claims, and conflating them puts blameless pages on outreach
lists:

| | Claim | Cost | Reliability |
|---|---|---|---|
| **Suspect** | this page was cited in an answer containing the error | free, from citation data | frequently wrong |
| **Cause** | this page actually states the wrong thing | needs a fetch and a check | reliable, with evidence |

Promoting a suspect to a cause requires reading the page and recording *which
direction* it states the claim:

```
states       — the page asserts the wrong thing      → genuine cause
contradicts  — the page asserts the correct thing    → evidence IN YOUR FAVOUR
silent       — the page doesn't address it            → coincidental citation
unclear      — ambiguous                              → human review
```

The `contradicts` case is the trap. Those pages appear in exactly the same
citation data as the causes, and they're the ones you should be *thanking*.

## What it cost me

I concluded in a draft that one of our own blog posts was the biggest single
source of wrong facts about us, on the strength of a high row count in the
suspect table. Two separate errors:

**A high row count read as "source of errors".** Of the rows on that page, most
carried the verdict `contradicts` — the page was *refuting* the AI's claim. The
table was showing me a page that was doing its job, and I read the volume as
guilt.

**URL matching by path, not host.** I matched sources with
`LIKE '%blog/brand-pricing%'`, which also caught four other companies' pages at
the same path on their own domains. Those got pooled into what looked like our
page's row, inflating exactly the number I then over-read.

The genuine residue after fixing both was small, real, and different in kind:
our own page listed one tier's price two ways in two places, and an "additional
users" line got paraphrased by models into something misleading. A useful
finding — just not the one I'd published.

## The fix

**Match on host, not path.** Always.

```sql
-- wrong: pools every domain with this path
WHERE url LIKE '%blog/brand-pricing%'

-- right
WHERE host(url) = 'ourdomain.com' AND path(url) = '/blog/brand-pricing'
```

Normalise consistently (strip scheme, `www.`, query, fragment, trailing slash)
and compare host and path separately.

**Read the verdict direction before acting.** A suspect list is a queue for
verification, never a list of culprits. Show the verdict on every row.

**Enumerate every occurrence before concluding.** When a figure looks wrong,
find *all* its occurrences in the source — not the first plausible one. My
wrong conclusion came from reading one matching row and stopping.

**Keep "the page is wrong" and "the verdict is wrong" separate.** When a finding
looks false, there are two independent possibilities: the page genuinely says
something wrong, or your ground truth is wrong. Never resolve a confusing alert
by editing the ground truth to silence it — that corrupts good data to fix a
symptom.

## The rule

> Citation proximity is a hypothesis. A verbatim quote from the page is a
> finding.

Store the quote. It's what makes an outreach email possible and what stops you
sending the wrong one.
