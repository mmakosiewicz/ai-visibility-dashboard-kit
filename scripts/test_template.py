#!/usr/bin/env python3
"""Checks that report-template.html is current and renders the worked examples.

    python3 scripts/test_template.py

1. The template's embedded wording and rules match plain_language.py and
   metric-menu.json (i.e. build_template.py was run after the last change).
2. With Node installed: each example's proposal renders, and the page's main
   numbers match plan.json (the Python and the template agree on verdicts).
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import plain_language as PL  # noqa: E402

fails = 0


def check(ok, msg):
    global fails
    print(("ok   " if ok else "FAIL ") + msg)
    fails += not ok


t = (ROOT / "09-proposal" / "report-template.html").read_text(encoding="utf-8")
wording = json.loads(re.search(r"const WORDING = (.*?);\n", t).group(1))
menu = json.loads(re.search(r"const MENU = (.*?);\n", t).group(1))
src = json.loads((ROOT / "09-proposal" / "metric-menu.json").read_text(encoding="utf-8"))
check(menu["metrics"] == src["metrics"] and menu["headline_by_shape"] == src["headline_by_shape"],
      "template rules match metric-menu.json")
check(all(wording[k] == json.loads(json.dumps(getattr(PL, k))) for k in wording), "template wording matches plain_language.py")
check(t.count('{"_template": true}') == 1, "template has one empty measurements slot")

if not shutil.which("node"):
    print("skip render checks (node not installed)")
else:
    for ex in sorted((ROOT / "examples").glob("*/proposal/plan.json")):
        html = subprocess.run(["node", str(ROOT / "scripts" / "print_report.js"), str(ex.parent / "proposal.html")],
                              capture_output=True, text=True)
        check(html.returncode == 0 and "<h1>" in html.stdout, f"{ex.parent.parent.name}: renders")
        plan = json.loads(ex.read_text(encoding="utf-8"))
        for g in plan["groups"]:
            h = next((m for m in g["metrics"] if m["id"] == g.get("headline")), None)
            v = h and h["sample"].get("value")
            if v:
                check(f">{v}<" in html.stdout, f'{ex.parent.parent.name}: "{g["name"][:40]}" main number {v}')
            n_keep = sum(m["verdict"] == "keep" for m in g["metrics"])
            check(f"{n_keep} numbers worth tracking" in html.stdout or f"{n_keep} number worth tracking" in html.stdout
                  or (n_keep == 0 and "0 numbers" in html.stdout),
                  f'{ex.parent.parent.name}: "{g["name"][:40]}" keeps {n_keep}')

print("all passed" if not fails else f"{fails} failed")
sys.exit(1 if fails else 0)
