# The grading prompt as a template

[`06-pipeline/grading.md`](../06-pipeline/grading.md) shows the extraction pass
as a finished prompt. Three passages in it are about *one* brand, and a reader
keeps them by accident. This is the same prompt with the brand-specific parts as
slots, followed by the two filled versions that run today.

## Template

```
You grade one AI-assistant answer about {category}. The brand we track is
{label} (including its products: {products}).
{disambiguation}
Return STRICT JSON only:
{
 "mentioned": bool,           // {label} or one of its products is named anywhere in the answer
 "position": int|null,        // 1-based order of {label} among DISTINCT brands as they first appear; null if not mentioned
 "brands": [str],             // distinct brands/companies named, lowercase, in order of first appearance;
                              // fold a company's products into the company ({fold_rules});
                              // keep separately owned brands separate ({keep_separate})
 "tool_recommended": bool,    // true ONLY if the answer tells the reader to use a NAMED product for the task.
                              // Passing mentions, generic "use a {generic_tool}", or pure process explanations are false.
                              // {free_tools_note}
 "tool_names": [str],         // the named products it recommends, lowercase, company-level; [] if tool_recommended is false
 "verdict_winner": str|null,  // the ONE brand the answer overall recommends over the others, lowercase.
                              // null is EXPECTED and CORRECT when the answer names no single winner. Never pick one to be helpful.
 "sentiment": "positive"|"neutral"|"mixed"|"negative"|null,  // toward {label} specifically; null if not mentioned
 "negative_themes": [str],    // short labels for criticisms of {label} (e.g. {theme_examples}); [] if none
 "negative_quotes": [str]     // VERBATIM fragments criticising {label}, copied exactly, max 25 words each, max 4; [] if none
}
```

| Slot | What goes in | Why it exists |
|---|---|---|
| `{category}` | the market, in the reader's words | anchors "brand" to the right domain |
| `{label}`, `{products}` | from brand.yaml | a product mention IS a brand mention; without the list you under-count |
| `{disambiguation}` | brand.yaml `disambiguation`, one line each; empty is fine | names that are also words (Square, Monday, Notion, Slack) |
| `{fold_rules}` | brand.yaml `fold_rules` | position and share of voice count companies, not SKUs |
| `{keep_separate}` | brand.yaml `keep_separate` | a rival's acquisition can be its own competitor (Braintree) |
| `{generic_tool}` | "an SEO tool", "a payment gateway" | defines what a NON-named recommendation looks like |
| `{free_tools_note}` | e.g. "Free first-party tools (Google Search Console, GA) count as named." | otherwise the model drops them and capture flatters you |
| `{theme_examples}` | two plausible criticisms | steers labels to a stable vocabulary |

## In code, not in the prompt

Whatever the template says, enforce these after the call:

- **Quotes verified verbatim** under normalisation (lowercase, straight quotes,
  collapsed whitespace, markdown stripped). Drop paraphrases.
- **Mention override**: if the literal brand token appears in the answer text
  (word-boundary regex) and the model said `mentioned: false`, set it true and
  flag `mention_fixed`. Both example boards needed this on <1% of answers.
- **Brand list lowercased and stripped**; `verdict_winner` lowercased.
- **Cohort matching is exact-token.** "squarespace" must not match "square";
  "se ranking" and "seranking" are the same brand. Match `b == v or
  b.startswith(v + " ")`, not `v in b`.

## Filled: SEO tools (Ahrefs)

```
You grade one AI-assistant answer about SEO / marketing / AI-visibility tools. The brand we track is Ahrefs (including its products: Site Explorer, Keywords Explorer, Site Audit, Rank Tracker, Brand Radar, Ahrefs Webmaster Tools, AI Content Helper).
[no disambiguation lines]
… fold a company's products into the company ("keywords explorer" -> "ahrefs", "google search console" -> "google search console") …
… generic "use an SEO tool" … Free first-party tools (Google Search Console, GA) count as named. …
… criticisms of Ahrefs (e.g. "price", "learning curve") …
```

## Filled: payments (Stripe)

```
You grade one AI-assistant answer about online payments. The brand we track is Stripe (including its products: Stripe Payments, Checkout, Elements, Billing, Connect, Radar, Terminal, Tax, Link, Atlas, Sigma, Identity, Treasury, Stripe docs).
"Square" means Square Inc. / Block's payments product (Square Online, Square Reader, Square Terminal), never the shape or "square footage". "Squarespace" is a different company.
… fold a company's products into the company ("stripe billing" -> "stripe", "square online" -> "square"); keep separately owned brands separate ("braintree", "venmo", "adyen") …
… generic "use a payment gateway" … [no free-tools note]
… criticisms of Stripe (e.g. "fees", "account holds") …
```

What differs between the two is exactly the slot contents. The Ahrefs version
has an empty disambiguation slot and a free-tools note; the Stripe version has
two disambiguation lines and a keep-separate list. Read your own brand.yaml and
ask which slots are empty for you — that's the review.
