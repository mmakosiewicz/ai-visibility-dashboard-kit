#!/usr/bin/env python3
"""Fill the report template with a proposal's numbers.

    python3 scripts/render_html.py proposal/            # plan.json + shapes.csv -> proposal.html
    python3 scripts/render_html.py proposal/ --out x.html
    python3 scripts/render_html.py proposal/ --json m.json   # also write the measurements object

propose.py calls this automatically. The page itself is 09-proposal/report-template.html:
the one renderer every path uses. This script only converts plan.json into the
template's input (09-proposal/measurements.md) and inserts it.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plain_language as PL  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "09-proposal" / "report-template.html"
PLACEHOLDER = '{"_template": true}'


def measurements(plan: dict, rows: list[dict]) -> dict:
    """plan.json + shapes.csv -> the template's input."""
    B = plan["label"]
    by_id = {r["id"]: r for r in rows}
    groups = []
    for g in plan["groups"]:
        qs = []
        for i in g["prompts"]:
            r = by_id.get(i)
            if not r:
                continue
            qs.append({"q": r["prompt"], "type": r["shape"], "note": r.get("type_note") or PL.review_note(r, B),
                       "answers": r.get("answers", 1)})
        ms = {}
        for m in g["metrics"]:
            if m["verdict"] == "unavailable" and m.get("why", "").startswith("needs an approved fact sheet"):
                continue
            looked = m.get("looked_at")
            if looked is None:  # plans written before looked_at existed: recover it from the verdict text
                import re as _re
                w = _re.search(r"≈(\d+)/week", m.get("why", ""))
                if w and m["sample"]["den"]:
                    looked = round(m["applies_to"] * plan["sample"]["surfaces"] * 7 * m["sample"]["den"] / int(w.group(1)))
                else:
                    looked = 0 if m["verdict"] == "unavailable" else max(1, m["sample"]["den"])
            x = {"num": m["sample"]["num"], "den": m["sample"]["den"], "looked_at": looked}
            if m["id"] == "citation_split":
                split = m.get("split") or {}
                x["split"] = sorted(split.items(), key=lambda kv: -kv[1])
            ms[m["id"]] = x
        groups.append({"name": g["name"], "description": g.get("description", ""), "questions": qs, "metrics": ms})
    s = plan["sample"]
    return {
        "brand": B, "generated": plan["generated_at"][:10], "classifier": plan["classifier"],
        "surfaces": s.get("surface_list") or ["?"] * s.get("surfaces", 4), "days": s["days"],
        "answers": s["answers"], "answers_expected": s.get("expected"),
        "cited_flag": s.get("cited_flag", False if any("cited` flag" in w for w in plan.get("warnings", [])) else None),
        "has_fact_sheet": bool(plan.get("fact_sheet")), "groups": groups,
    }


def fill(m: dict) -> str:
    t = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in t:
        sys.exit(f"{TEMPLATE} has no measurements placeholder; rebuild it with scripts/build_template.py")
    return t.replace(PLACEHOLDER, json.dumps(m, ensure_ascii=False, indent=1).replace("</", "<\\/"), 1)


def render(plan: dict, rows: list[dict]) -> str:
    return fill(measurements(plan, rows))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir", help="folder with plan.json and shapes.csv")
    ap.add_argument("--out")
    ap.add_argument("--json", help="also write the measurements object here")
    a = ap.parse_args()
    d = Path(a.dir)
    plan = json.loads((d / "plan.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(open(d / "shapes.csv", encoding="utf-8")))
    m = measurements(plan, rows)
    if a.json:
        Path(a.json).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    out = Path(a.out) if a.out else d / "proposal.html"
    out.write_text(fill(m), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
