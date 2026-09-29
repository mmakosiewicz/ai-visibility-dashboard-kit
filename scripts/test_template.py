#!/usr/bin/env python3
"""Checks that report-template.html is current and renders correctly.

    python3 scripts/test_template.py

1. The template's embedded wording and rules match plain_language.py and
   metric-menu.json (i.e. build_template.py was run after the last change).
2. With Node installed: a small made-up fixture renders, with the right main
   number, verdict reasons and warnings.
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

# A tiny made-up fixture, built here so no runnable sample data ships with the repo.
FIXTURE = {
    "brand": "TEST-BRAND", "demo": True, "generated": "2000-01-01", "classifier": "test fixture (not real data)",
    "surfaces": ["s1", "s2", "s3", "s4"], "days": 1, "answers": 40, "answers_expected": 40,
    "cited_flag": False, "has_fact_sheet": False,
    "groups": [
        {"name": "Fixture topic A", "description": "made up",
         "questions": [{"q": f"fixture list question {i}", "type": "list", "note": "", "answers": 4} for i in range(6)],
         "metrics": {"mention_rate": {"num": 18, "den": 24, "looked_at": 24},
                     "position": {"num": 36, "den": 18, "looked_at": 24},
                     "win_rate": {"num": 0, "den": 0, "looked_at": 24},
                     "owned_citation_share": {"num": 5, "den": 100, "looked_at": 24,
                                              "split": [["third-party", 80], ["owned", 5], ["ugc", 15]]}}},
        {"name": "Fixture topic B", "description": "made up",
         "questions": [{"q": f"fixture task question {i}", "type": "task", "note": "hard to call" if i == 0 else "", "answers": 4}
                       for i in range(4)],
         "metrics": {"capture": {"num": 3, "den": 8, "looked_at": 16}}},
    ],
}
EXPECT = [">75%<", "Fixture topic A", "Demo: made-up data", "Only 4 questions in this topic suit",
          "doesn&#x27;t say which links were actually cited", "1 of 10 questions were hard to sort"]

if not shutil.which("node"):
    print("skip render checks (node not installed)")
else:
    import tempfile
    sys.path.insert(0, str(ROOT / "scripts"))
    import render_html  # noqa: E402
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
        fh.write(render_html.fill(FIXTURE))
    html = subprocess.run(["node", str(ROOT / "scripts" / "print_report.js"), fh.name], capture_output=True, text=True)
    Path(fh.name).unlink()
    check(html.returncode == 0 and "<h1>" in html.stdout, "fixture renders")
    for e in EXPECT:
        check(e in html.stdout, f"fixture page shows {e!r}")
    check("(Win rate)" in html.stdout, "zero-denominator metric is listed")
    # the page refuses data that names no Brand Radar report
    for bad, why in ((dict(FIXTURE, demo=None), "no report_id"), (dict(FIXTURE, demo=None, report_id="example"), "made-up report_id"),
                     (dict(FIXTURE, demo=None, report_id="0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5b"), "the old placeholder id")):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
            fh.write(render_html.fill(bad))
        out = subprocess.run(["node", str(ROOT / "scripts" / "print_report.js"), fh.name], capture_output=True, text=True).stdout
        Path(fh.name).unlink()
        check("<h1>" not in out and "Brand Radar report" in out, f"refuses measurements with {why}")

print("all passed" if not fails else f"{fails} failed")
sys.exit(1 if fails else 0)
