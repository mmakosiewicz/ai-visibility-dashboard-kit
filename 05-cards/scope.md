# Scope: global filters

Two global controls, and one rule about which cards are allowed to ignore them.

## The two controls

**Date range.** Presets (today / 7d / 30d / all) plus explicit start and end.
Resolves to a **list of snapshots** — one per day, the last successful run of
that day — which every answer-derived metric then pools. One day and thirty days
take the same code path.

**AI surface.** All surfaces, or exactly one. Recalculates every answer-derived
metric, table and chart.

That's it. Two controls is a deliberate ceiling: every additional global filter
multiplies the number of states you have to make correct, and the third one
nobody uses.

## Scope independence

Some cards **must not** respond to these filters:

| Card | Date range | Surface | Why |
|---|---|---|---|
| answer-derived (1,2,3,4,6,7,8) | yes | yes | that's what they measure |
| citations (5), tracked pages (11) | yes | yes | derived from the same answers |
| crawl health (9) | **no** | **no** | server logs; no surface dimension exists |
| freshness (10) | **no** | **no** | page dates; trailing window of its own |
| any live-stream card | **no** | **no** | today's data would be hidden by a past range |

The important part is **saying so on the card**. Silently ignoring a global
filter is worse than not offering one: the user changes the filter, the number
doesn't move, and they conclude the dashboard is broken. Each independent card
carries its own window control and a line stating it isn't affected by the
selector above.

Implementation detail that bit me: when a filter changes, I clear the deferred
panels and re-fetch. Scope-independent cards must be **excluded from that
clearing**, or they blank out and never come back — they don't read the scope
that changed, so nothing re-triggers them.

## Single-surface views need a sample-size warning

Filtering to one surface cuts the sample to roughly a seventh. Per-prompt rows
then sit at a handful of answers, which is below the point where a rate means
anything.

Two mitigations, both worth doing:

- **A visible warning** on the card when a single surface is selected.
- **Show the delta against the all-surface baseline** — "48% (−7 vs all)" — so
  the filtered number is always read as a comparison rather than a fact.

## Pooling rules

- **One snapshot per day.** Two successful runs on one day would double-weight
  it.
- **Pool answers, not rates.** Sum numerators and denominators across the range,
  then divide. Averaging daily percentages weights a thin day equally with a
  full one.
- **Operational extras come from the final snapshot only** when a range spans
  several — their trailing-window state can't be pooled. Say so in the UI, or
  the two halves of the board look inconsistent.

## Caching scoped results

A scoped result is immutable until a newer snapshot lands, which makes it
trivially cacheable. I keep a small in-process LRU keyed by
`(start, end, surface, newest_completed_snapshot_id)` with a short TTL.

Effect: first view of a scope is a real computation, revisiting it is instant,
and the cache invalidates itself when new data arrives — no manual busting, no
stale-data class of bug. Include the newest snapshot id **in the key** rather
than clearing the cache on refresh; it's the same outcome with none of the race
conditions.

## Progressive loading, and the stale-response trap

Seven heavy queries fired simultaneously on every scope change is both slow and
hard on the database. Two fixes:

- **Render core cards first**, then fill in the expensive panels (sources,
  share of voice, tracked pages, answers) as they resolve. Sequence them into a
  few lanes rather than firing all at once.
- **Sequence-number every load.** If the user changes scope mid-flight, an
  older response must not overwrite the newer selection. Increment a counter on
  each scope change, tag each fetch with it, and discard any response whose tag
  isn't current.

That second one is the bug you'll otherwise ship: change the filter twice
quickly and the board shows the first selection's data under the second
selection's label.
