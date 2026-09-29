# 1 · Citations are not mentions

**The pages AI cites when answering about your category are largely not the
pages that talk about you.**

This is the most expensive wrong assumption in AI-visibility work, because it's
invisible: citation counts are easy to get, they look like influence, and
ranking by them produces a plausible-looking list.

## How it shows up

You build a list of "the pages AI cites most about our category" and use it for:

- **outreach targets** — most of which have no hook for you, because you aren't
  in them
- **"did someone remove us" monitoring** — which can never fire on a page you
  were never in
- **a sense of your share of the conversation** — inflated, because you're
  counting pages that don't mention you

In my data, a large share of AI-cited pages in our space are only ever cited in
answers where our brand is absent. In one adjacent category it was essentially
all of them — thousands of citations, zero mentions, because we have no product
there. Citation volume was a perfect signal of *the category's* importance and
no signal at all about us.

## Why it happens

A citation is the model saying "this page was relevant to the question". A
mention is the page saying "this brand exists". Those are different claims, and
nothing in citation data connects them.

The pages that rank as most-cited in any category are its biggest generic
resources — roundups, guides, review sites. Whether *you* appear in them is a
completely separate fact.

## The fix

**Verify mentions per page before ranking anything.**

Your data source almost certainly exposes this: Brand Radar's cited-pages view
returns a `mentioned_brands` list per page, which is the authoritative "does
this page mention us" signal. Use it — don't infer mentions from citation
counts, and don't infer them from the page's title either.

Then rank:

```
1. verified-mentioning pages, by distinct answers citing them   ← your worklist
2. pages with no data, flagged unverified                       ← check manually
3. pages verified as not mentioning you                         ← excluded, kept
   (they're still useful context: that's the category's supply chain)
```

Don't delete category 3. It tells you who owns the conversation you're absent
from, which is a finding of its own — it's just not an outreach list.

## The caught-in-the-act version

A page sat near the top of my brand-drop watch list on citation volume alone.
It never mentions us. A "they removed us" alert on that page could not possibly
fire — and it took someone reading the list carefully to notice, because the row
looked exactly like the rows above and below it.

After verifying mentions per page against the source's own brand data, a
significant fraction of the top pages came off the list entirely. The remaining
list is shorter and every row is actionable.

## The rule

> Citation count ranks the category. Verified mentions rank your work.

And when you verify, respect the three-state answer — see
[`null` is not `[]`](null-is-not-empty.md), which is the bug I introduced *while
fixing this one*.
