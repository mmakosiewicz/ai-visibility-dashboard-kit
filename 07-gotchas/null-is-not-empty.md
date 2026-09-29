# 2 · `null` is not `[]`

**"We looked and found no brands" and "we have no data for this page" are
different answers. Collapse them and you will confidently assert things that are
false.**

## The three states

When you ask your data source "which brands does this page mention?", there are
three possible answers, not two:

| Response | Means | Correct handling |
|---|---|---|
| `["brand_a", "brand_b"]` | brands found, listed | if you're absent, you're genuinely absent |
| `[]` | it looked, found none | no brands mentioned — a real finding |
| `null` / missing | **no data** — it didn't look, or the page isn't indexed | **unknown** — must not be read as absence |

The third state is the one that gets lost, because most code paths coerce a
missing value to an empty collection and move on. That coercion is where the bug
lives.

## What it cost me

While fixing [citations ≠ mentions](citations-are-not-mentions.md), I added
per-page brand verification and excluded any page whose brand list didn't
include us. A helper in my own code collapsed `null` into `[]` — so "no data"
became "no mention", and pages got excluded for having never been checked.

The page that made it obvious was titled, literally, *"<Brand> pricing and plans
guide"*. It was flagged as not mentioning us. A page with our brand in its title.

That's the useful property of this bug: when it fires, it produces a claim so
obviously wrong that a human spots it. The dangerous cases are the pages where
nobody notices.

## The fix

**Keep the third state all the way through.** Three concrete rules:

1. **Don't coerce at the boundary.** If the API returns `null`, store `null`.
   A JSONB column with a default of `'[]'` quietly destroys this distinction —
   make it nullable.

2. **Read the source directly when the distinction matters.** If a convenience
   helper in your codebase flattens the states, bypass it for verification work.
   Mine did, and that's exactly where the bug was.

3. **Carry `unverified` as a visible status.** A page with no brand data is
   *kept* in the worklist and marked unverified — never silently excluded and
   never silently included. Show the count: "39 confirmed, 11 unverified" is an
   honest row; "50 pages" is not.

## The general form

This isn't really about brand lists. It's the null-vs-empty problem, which
recurs everywhere in this kind of work:

| Field | `null` means | `0` / `[]` means |
|---|---|---|
| brands mentioned | not checked | checked, none found |
| page date | no date discoverable | — (never use 0) |
| position | not mentioned | — (never use 0 or list length) |
| citations | not measured | measured, zero citations |
| sentiment | not mentioned | neutral |

Every one of those pairs has a version where collapsing them produces a wrong
metric. The position one is the most common in this domain — imputing a value
for absence is covered in [position](../04-metrics/position.md).

## The rule

> Unknown is a value. Give it a column, a label on screen, and a count.

If your dashboard cannot say "we don't know" about a row, it will say something
false instead.
