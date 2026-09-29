#!/usr/bin/env python3
"""Fit report: what will this spec give you on YOUR prompt set, before you build.

    python3 scripts/fit_report.py --prompts prompts.csv --brand brand.yaml
    python3 scripts/fit_report.py --prompts prompts.csv --brand brand.yaml --json out.json

prompts.csv  one prompt per row; columns: query[,tags]  (Brand Radar's custom
             prompt export has these). tags may be empty or ";"-separated.
brand.yaml   see 08-adapting/brand.yaml — only brand/variants/products/competitors
             are read here. Parsed with a tiny reader, no PyYAML needed.

Output: prompt count and tag coverage, prompt shapes (02-prompts/shapes.md),
which of the 12 questions the set can answer, entity-collision warnings, and a
grading-cost estimate. Nothing here calls an API.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter

# "vs"/"versus" are deliberately NOT list markers: with no brand or competitor
# named, "AEO vs SEO" or "load sensing versus overload protection" compares two
# concepts, which is a category prompt. Product-vs-product prompts are caught
# earlier as branded/conquest.
LIST_MARKERS = re.compile(r"\b(best|top \d+|top[- ]rated|top picks|alternatives?|compare|comparison|which|recommend\w*|options?|most (used|popular|accurate|reliable|recommended)|what tools|tools (do|should|used))\b", re.I)
# Product-finder prompts: a bare noun phrase qualified by a feature, e.g.
# "standing desks with reversible tops", "desk controllers that lock voice
# commands", "payment processor for subscriptions". They ask for options without
# a list marker. Only applied when the prompt does not open like a question.
QUESTION_OPENERS = re.compile(r"^(what|how|why|when|where|who|is|are|do|does|did|can|could|should|would|will|pros|cons|explain|define|tell)\b", re.I)
FINDER = re.compile(r"^[a-z0-9][\w\s\-/&]{1,60}?\s(with|without|that|featuring|supporting)\s\S", re.I)
TASK_MARKERS = re.compile(r"\b(how (do|to|can) |set ?up|implement|integrate|fix|why (is|are|does|do) my|can (you|i) |steps? (to|for)|enable|configure|migrate|calculate|process|add|create|handle|export|recover|verify|tokeni[sz]e|store|accept|optimi[sz]e|onboard|support|mitigate|dispute|securely)\b", re.I)

# Brand names that are also ordinary words. If yours is here (or should be),
# the grader needs a disambiguation line and the pipeline can't trust keyword
# matching for mentions.
COMMON_WORDS = {"square", "stripe", "monday", "notion", "slack", "zoom", "loom", "linear",
                "front", "arc", "bolt", "brave", "wave", "sage", "mint", "bench", "wise",
                "chime", "current", "plaid", "ramp", "brex", "clear", "hive", "drift",
                "intercom", "moz", "later", "buffer", "hootsuite", "canvas", "figma"}

QUESTIONS = [
    ("1 head-to-head", lambda s, w: s["branded_comparison"] >= 3),
    ("2 category list", lambda s, w: s["list"] >= 3),
    ("3 sub-niches", lambda s, w: s["list"] + s["task"] >= 8),
    ("4 task recommendations", lambda s, w: s["task"] >= 5),
    ("5 source influence", lambda s, w: True),
    ("6 fact fidelity", lambda s, w: s["branded"] >= 5 and w.get("fact_sheet")),
    ("7 narrative risk", lambda s, w: s["branded"] >= 5),
    ("8 adjacent categories", lambda s, w: False),  # needs your own labelling
    ("9 crawl health", lambda s, w: bool(w.get("bot_analytics"))),
    ("10 citation freshness", lambda s, w: True),
    ("11 tracked pages", lambda s, w: bool(w.get("tracked_pages"))),
    ("12 citation attention", lambda s, w: True),
]


def read_yaml_lite(path: str) -> dict:
    """Reads the flat/one-level-list subset used by brand.yaml. Not a YAML parser."""
    out, key = {}, None
    for raw in open(path, encoding="utf-8"):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if not val:
                out[key] = []
            elif val.startswith("[") and val.endswith("]"):  # inline list: [] or [a, b]
                out[key] = [v.strip().strip('"\'') for v in val[1:-1].split(",") if v.strip()]
            else:
                out[key] = val.strip('"\'')
        elif line.strip().startswith("- ") and key is not None:
            item = line.strip()[2:].strip().strip('"\'')
            if isinstance(out[key], list):
                out[key].append(item.split(":")[0].strip() if key == "competitors" else item)
    return out


def word_re(term: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])")


def classify(prompt: str, brand_terms: list[str], comp_terms: list[str]) -> str:
    p = prompt.lower().strip()
    if any(word_re(t).search(p) for t in brand_terms):
        return "branded"
    if any(word_re(t).search(p) for t in comp_terms):
        return "conquest"
    if LIST_MARKERS.search(p):
        return "list"
    if TASK_MARKERS.search(p) or p.startswith(("how to", "how do", "how can", "what should")) \
            or p.endswith("?") and p.startswith(("how", "why", "where")):
        return "task"
    if not QUESTION_OPENERS.match(p) and FINDER.match(p):
        return "list"
    return "category"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--brand", required=True)
    ap.add_argument("--surfaces", type=int, default=6, help="AI surfaces scanned per prompt per day")
    ap.add_argument("--days", type=int, default=30, help="history to grade at first build")
    ap.add_argument("--cost-per-answer", type=float, default=0.0003,
                    help="USD per graded answer; ~0.0003 with a budget model, ~0.002 mid-tier")
    ap.add_argument("--json")
    a = ap.parse_args()

    brand = read_yaml_lite(a.brand)
    bname = str(brand.get("brand", "")).lower()
    brand_terms = [bname] + [v.lower() for v in brand.get("variants", [])] + [v.lower() for v in brand.get("products", [])]
    comp_terms = [c.lower() for c in brand.get("competitors", [])] + [v.lower() for v in brand.get("competitor_variants", [])]
    brand_terms = [t for t in brand_terms if t]

    rows = list(csv.DictReader(open(a.prompts, encoding="utf-8")))
    qcol = next((c for c in rows[0].keys() if c.lower() in ("query", "prompt", "question", "keyword")), None) if rows else None
    if not qcol:
        print("prompts.csv needs a 'query' (or prompt/question) column", file=sys.stderr)
        return 1
    tcol = next((c for c in rows[0].keys() if c.lower() in ("tags", "tag", "group")), None)

    shapes, tagged, per_prompt = Counter(), 0, []
    for r in rows:
        q = (r[qcol] or "").strip()
        if not q:
            continue
        sh = classify(q, brand_terms, comp_terms)
        comp = sh == "branded" and bool(re.search(r"\b(vs\.?|versus|or|better than|compared? (to|with)|alternatives?)\b", q.lower()))
        tags = (r.get(tcol) or "").strip() if tcol else ""
        tagged += bool(tags)
        shapes[sh] += 1
        if comp:
            shapes["branded_comparison"] += 1
        per_prompt.append({"prompt": q, "shape": sh, "comparison": comp, "tags": tags})
    n = len(per_prompt)

    warnings = []
    for t in [bname] + [c for c in comp_terms]:
        if t in COMMON_WORDS:
            warnings.append(f'"{t}" is also an ordinary word or a substring of other brands — add a disambiguation line to the grader and do not trust keyword matching for mentions.')
    if shapes["branded"] == 0:
        warnings.append("No prompt names your brand: win rate needs the per-answer rule (02-prompts/shapes.md) and fact fidelity is not available.")
    if tcol and tagged < n:
        warnings.append(f"{n - tagged} of {n} prompts have no tag: group them in your build config, or tag them in the source first.")
    if n and n < 30:
        warnings.append(f"Only {n} prompts: expect noisy daily rates; pool 7+ days before reading a change as a change.")
    for sh in ("branded", "conquest", "list", "task", "category"):
        if 0 < shapes[sh] < 5:
            warnings.append(f"Only {shapes[sh]} {sh} prompt(s): any card built on them flips on a single answer.")

    have = {"fact_sheet": brand.get("fact_sheet") not in ("", [], None, "false", "no"),
            "bot_analytics": brand.get("bot_analytics") not in ("", [], None, "false", "no"),
            "tracked_pages": bool(brand.get("tracked_pages"))}
    answerable = [(q, bool(f(shapes, have))) for q, f in QUESTIONS]

    answers_day = n * a.surfaces
    cost_first = answers_day * a.days * a.cost_per_answer
    cost_day = answers_day * a.cost_per_answer

    print(f"Prompts: {n}   tagged: {tagged}/{n}   brand: {bname}   competitors: {', '.join(brand.get('competitors', [])) or '—'}")
    print("\nShapes (02-prompts/shapes.md):")
    for sh in ("branded", "conquest", "list", "task", "category"):
        print(f"  {sh:10} {shapes[sh]:4}" + (f"   (of which comparisons: {shapes['branded_comparison']})" if sh == "branded" else ""))
    print("\nQuestions this set can answer:")
    for q, ok in answerable:
        print(f"  {'✓' if ok else '✗'} {q}")
    print(f"\nHeadline metric suggestion: "
          + ("win rate (branded comparisons)" if shapes["branded_comparison"] >= 5
             else "capture (task prompts)" if shapes["task"] >= shapes["list"]
             else "mention rate + position (list prompts)"))
    print(f"\nVolume: {answers_day} answers/day over {a.surfaces} surfaces. "
          f"First build grading {a.days} days ≈ ${cost_first:.2f}; then ≈ ${cost_day:.2f}/day. "
          f"Fact checking (if used) costs 10–30× more per answer — scope it to branded prompts.")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ! {w}")
    if a.json:
        json.dump({"n": n, "tagged": tagged, "shapes": dict(shapes), "answerable": dict(answerable),
                   "warnings": warnings, "cost_first_build_usd": round(cost_first, 2),
                   "cost_per_day_usd": round(cost_day, 2), "prompts": per_prompt},
                  open(a.json, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
