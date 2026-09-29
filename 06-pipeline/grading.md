# Grading answers with an LLM

Two passes. The first runs on every answer; the second only where you have
ground truth to check against.

The instructions below are the shape of what works — the value is in the
*rules*, which are all scar tissue from a wrong number.

The prompt below is filled for one brand. The slotted version, with the
brand-specific passages marked and two filled examples, is
[08-adapting/grader-template.md](../08-adapting/grader-template.md). Read that
before copying this one.

## Pass 1 · Extraction (every answer)

Input: the prompt and the answer text (truncate long answers — ~9k chars was
plenty). Output: strict JSON, no prose.

```json
{
  "mentioned": true,
  "position": 2,
  "total_brands": 7,
  "brands": ["semrush", "ahrefs", "moz"],
  "tool_recommended": true,
  "tool_names": ["ahrefs", "semrush"],
  "sentiment": "neutral",
  "verdict_winner": null,
  "negative_themes": ["price"],
  "negative_quotes": ["..."]
}
```

Field definitions that must be in the instruction, not assumed:

| Field | Instruction |
|---|---|
| `position` | 1-based order of our brand among **distinct brands as they first appear**; `null` if not mentioned |
| `brands` | in order of first appearance — this is what makes position auditable |
| `tool_recommended` | true only if the answer tells the reader to use a **named** product for the task; passing mentions and generic unnamed tools are false; free/default first-party tools count |
| `verdict_winner` | the tool the answer **overall** recommends, lowercase; **`null` when it names none** — and say explicitly that null is expected and correct |
| `sentiment` | toward us specifically; `null` if not mentioned |
| `negative_quotes` | **verbatim** fragments, max ~25 words, max 4 |

### Four rules that came from bugs

**Say that `null` is expected.** Left implicit, the model picks a winner to be
helpful, your "decided" population inflates with fabricated verdicts, and win
rate becomes meaningless.

**Verify quotes in code, not in the prompt.** Models paraphrase when asked to
quote. Keep only quotes that appear verbatim under normalisation:

```python
def normalise(t):
    t = t.lower().replace("\u2019","'").replace("\u201c",'"').replace("\u201d",'"')
    t = t.replace("\u2014","-").replace("\u2013","-")
    return re.sub(r"\s+", " ", t)

ev["negative_quotes"] = [q for q in ev.get("negative_quotes", [])
                         if normalise(q) in normalise(response)][:4]
```

**Use JSON mode and retry with backoff.** Transient empty completions were
silently degrading gradings — they don't announce themselves, they just skew a
number slightly.

**Budget completion tokens generously.** A long list answer plus reasoning
tokens overran my first limit and returned empty completions. Looked like a
model failure; was a truncation.

## Pass 2 · Fact check (question 6 only)

Input: the approved fact sheet **plus** one answer. Output: extracted claims,
each with a verdict.

```json
{"claims": [{"claim": "...",
             "verdict": "consistent | contradicted | unverifiable",
             "severity": "hard | soft",
             "fact_ids": ["..."],
             "note": "one sentence"}]}
```

### The verdict rules, and why each exists

**Silence is not contradiction.** If the sheet says nothing on the point, the
verdict is `unverifiable` — never `contradicted`. Without this rule the card
fills with false positives and people stop believing it.

**Existence vs tier.** "X has feature F" and "F is in plan P" are different
claims. A sheet entry showing F exists in *any* plan **confirms** the existence
claim; it can only contradict a claim that names a specific plan wrongly. Never
use tier availability as evidence against an unscoped existence claim, and never
assume the answer meant the entry-level plan when it named no plan.

**Positioning is not checkable.** "Plan X is for freelancers", "best for
agencies", "most popular" — that's paraphrased marketing copy, not a fact.
Exclude audience claims entirely unless they assert something countable, like a
seat limit.

**Currency and billing period.** A correct price quoted in another currency, or
an annual-billing figure, is `consistent`. Not an error.

**Authority order.** A parsed plan/price table outranks prose facts when they
disagree — because your own FAQ and your own pricing table *will* disagree.

**Severity.** `hard` = a wrong checkable specific (price, plan name, numeric
limit, a feature that doesn't exist or is denied). `soft` = wording or framing
where the substance is close ("unlimited" for fair-use limits). Use `soft` for
anything a reasonable reader would call imprecise rather than false.

**Vague or other-brand claims: don't include them at all.** Not `unverifiable` —
absent. Otherwise your denominator fills with noise.

### Claim fingerprinting

```
fingerprint = normalise(claim_text) + sorted(fact_ids)
```

Normalisation lowercases, unifies punctuation, collapses whitespace — and
**preserves numbers**, because `$249` and `$279` must stay distinct claims.
Including the fact ids means the same sentence judged against a different fact
is a different claim, so a fact-sheet correction doesn't make old verdicts look
current.

This buys the verdict cache, the error lifecycle, and per-prompt accuracy that
survives rewording.

## Model choice

| Pass | What it needs |
|---|---|
| extraction | fast, cheap, reliable JSON — runs on every answer, every day |
| fact check | stronger reasoning — it's applying scoping rules, not extracting fields |

Use the cheap model for pass 1 and a stronger one for pass 2. Pass 1 is
high-volume and mechanical; pass 2 is low-volume and genuinely interpretive,
and cheaping out there produces exactly the false-positive class the verdict
rules exist to prevent.

## Validate the output shape

Parse into a typed model (Pydantic or equivalent) at the boundary. Normalise
known harmless variants — models return `"yes"` for booleans, or an extra key —
and drop unknown fields rather than storing them. A grading pass that silently
half-worked is much worse than one that failed.

## Cost control recap

1. **Answer hash** — unchanged answer, reuse grading. Biggest lever by far.
2. **Verdict cache** on `(fingerprint, factsheet_version)` — a claim already
   judged is never re-billed even in a new answer.
3. **Only fact-check where it pays.** Running the full claims pass on every
   answer in every question is mostly waste; I had ~54 LLM calls per run
   feeding nothing on screen before I noticed and turned that path off.
4. **Bounded concurrency.** Protects the provider and your rate limit.
