# Position and top-three rate

## Definition

```
position = 1-based rank of our brand among all distinct brands named in the
           answer, by order of FIRST appearance. null when not mentioned.

avg_position   = mean(position) over answers WHERE mentioned = true
top_three_rate = answers with position <= 3 / answers WHERE mentioned = true
```

Both are **conditional on being mentioned**. That's the whole file.

## Why conditional

Absence is not a bad position; it's a different outcome. If you score an
unmentioned answer as last place — or as list length, or as zero — you've
blended two independent things into one number:

- how often you appear (presence)
- how early you appear when you do (prominence)

They move independently and they imply different work. A mention rate rising
while position slips means you're getting into more lists but being inserted
later — new entrants ahead of you, probably a source problem. A blended metric
shows that as "roughly flat" and you learn nothing.

So: two metrics, side by side, and write the condition into the on-screen label
("avg position — when mentioned"). Not the tooltip. The label.

## Why first appearance, not "best" appearance

A brand can be named in a list, then again in a summary. Ranking by first
appearance is:

- **stable** — doesn't change when an answer adds a closing recap
- **cheap to extract** — the model is just reading the order it saw brands
- **closest to what a reader experiences** — people read top-down and stop

The alternative (rank by the most favourable mention) rewards verbose answers
and is hard to define consistently. Not worth it.

## Report total_brands next to it

Position 4 of 5 and position 4 of 20 are completely different results, and list
length drifts over time — models get more or less expansive. Without
`total_brands` on the card, a stable average position can hide the fact that
lists doubled in length and your relative standing improved.

This is also why **top-three rate is often the better headline than average
position**: "top three" is a fixed, meaningful bar regardless of list length,
and it maps to how shortlists actually work. Average position is smoother for
trend lines; top-three rate is more honest for reporting.

## Top-three rate needs its condition stated twice

It's conditional on mention, and that makes it easy to misread as a presence
metric. In my data, top-three-rate-when-mentioned varies enormously by question
— strong in the core category, much weaker in expansion areas — while overall
mention rate looks comparatively flat across both. Same brand, same day, two
very different stories, and only the conditional version tells you which.

Label it `top-three rate (of answers mentioning us)` and put the mention count
next to it.

## Averaging positions: a caveat

The mean of a rank is not a great statistic — ranks aren't interval-scaled, and
the difference between 1 and 2 matters more than between 8 and 9. I use the mean
anyway, because it's legible and the trend is what people read. If you want
better:

- **median position** is more robust to a single 15th-place outlier
- **top-three rate** avoids the problem entirely

I'd keep the mean for the trend line and top-three rate for the headline.

## Per-surface positions differ

Some surfaces produce short lists (3–5 brands), others long ones (10+). A
pooled average position across surfaces is therefore partly a measure of the
surface mix in your sample. It's fine as a trend when the mix is stable, but if
one surface fails to return answers for a day, this metric moves for that reason
alone — which is why the per-prompt platform-coverage column in
[question 3](../01-questions/03-niches.md) exists.
