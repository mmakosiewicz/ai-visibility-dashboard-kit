#!/usr/bin/env python3
"""Turn an approved MCP/chat proposal into the files the build uses.

    python3 scripts/from_measurements.py measurements.json --out report/<name>/

The MCP path (09-proposal/with-mcp.md) ends with a measurements object: the
questions, their topics and types, and the counts. The build needs the approved
sorting as files. This writes, into --out:

  prompts.csv   the report's questions
  shapes.csv    the approved topic and type per question (what the build keeps)
  brand.yaml    a starter with the brand and anything the object records; fill
                in the rest from 08-adapting/brand.yaml before building
  measurements.json  a copy of the input

Then get plan.json without re-sorting anything:

    python3 scripts/propose.py --prompts <out>/prompts.csv --brand <out>/brand.yaml \\
        --from-shapes <out>/shapes.csv --no-llm --out <out>/proposal

No model, no API key. Numbers in that plan.json are placeholders until the
build's own pull fills them; the approved sorting is what carries over.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

TYPES = {"branded", "conquest", "list", "task", "category", "none"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("measurements", help="the measurements JSON (09-proposal/measurements.md), or an HTML report that contains it")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raw = Path(a.measurements).read_text(encoding="utf-8")
    if raw.lstrip().startswith("<"):  # a filled report page: take the embedded object
        import re
        m = re.search(r'<script type="application/json" id="measurements">\s*(.*?)\s*</script>', raw, re.S)
        if not m:
            sys.exit("no measurements block found in that HTML file")
        raw = m.group(1).replace("<\\/", "</")
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    D = json.loads(raw)
    if D.get("_template"):
        sys.exit("that's the empty template, not a proposal")
    problems = []
    for g in D.get("groups", []):
        if not g.get("name"):
            problems.append("a topic has no name")
        for q in g.get("questions", []):
            if q.get("type") not in TYPES:
                problems.append(f"question {q.get('q', '?')[:50]!r} has type {q.get('type')!r}")
    if problems:
        sys.exit("fix these first:\n  " + "\n  ".join(problems))

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    seen = set()
    with open(out / "prompts.csv", "w", newline="", encoding="utf-8") as fp, \
         open(out / "shapes.csv", "w", newline="", encoding="utf-8") as fs:
        wp = csv.writer(fp)
        wp.writerow(["query"])
        ws = csv.writer(fs)
        ws.writerow(["prompt", "group", "shape", "reason", "group_description"])
        for g in D["groups"]:
            for q in g["questions"]:
                k = q["q"].strip().lower()
                if k in seen:
                    continue
                seen.add(k)
                wp.writerow([q["q"].strip()])
                ws.writerow([q["q"].strip(), g["name"], q["type"], q.get("note") or "approved in the MCP proposal",
                             g.get("description", "")])
    by = out / "brand.yaml"
    if by.exists():
        print(f"kept existing {by}")
    else:
        brand = D.get("brand", "")
        lines = ["# Starter written by from_measurements.py. Fill in the rest from",
                 "# 08-adapting/brand.yaml before building: variants, products,",
                 "# competitors, owned_domains, competitor_domains, disambiguation.",
                 f"brand: {brand.lower()}", f"label: {brand}"]
        for key in ("category", "generic_tool"):
            if D.get(key):
                lines.append(f"{key}: {D[key]}")
        for key in ("variants", "products", "competitors", "owned_domains", "competitor_domains"):
            vals = D.get(key) or []
            lines.append(f"{key}:" + ("" if vals else " []"))
            lines += [f"  - {v}" for v in vals]
        lines.append(f"fact_sheet: {'true' if D.get('has_fact_sheet') else 'false'}")
        by.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "measurements.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out}/prompts.csv, shapes.csv, brand.yaml, measurements.json ({len(seen)} questions, {len(D['groups'])} topics)")
    print(f"next: python3 scripts/propose.py --prompts {out}/prompts.csv --brand {out}/brand.yaml "
          f"--from-shapes {out}/shapes.csv --no-llm --out {out}/proposal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
