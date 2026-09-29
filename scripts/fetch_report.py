#!/usr/bin/env python3
"""Step 0a: pull a Brand Radar report's questions and answers. Everything starts here.

    python3 scripts/fetch_report.py                                   # asks for the report
    python3 scripts/fetch_report.py --report https://app.ahrefs.com/brand-radar/reports/<id>/overview
    python3 scripts/fetch_report.py --report <id> --days 2 --out report/

Needs an Ahrefs API key with Brand Radar access in AHREFS_API_KEY (Ahrefs →
Account settings → API keys). Uses the public v3 API:
GET https://api.ahrefs.com/v3/brand-radar/ai-responses, one call per AI surface
per day. Each call costs API units; one day of a 100-question report on 6
surfaces is 6 calls.

Writes into --out (default report/<report-id>/):

    prompts.csv     every custom question on the report (column: query)
    answers.jsonl   one line per answer: question, model, date, response, sitelinks
    brand.yaml      your brand and competitors; asked for if it doesn't exist yet,
                    because the API doesn't expose a report's brand settings
    fetch.json      what was pulled, from which surfaces, and the count check

Then run propose.py on that folder (it tells you the exact command).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.ahrefs.com/v3/brand-radar/ai-responses"
SURFACES = ["chatgpt", "gemini", "perplexity", "copilot", "google_ai_overviews", "google_ai_mode", "grok", "claude"]
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
FIELDS = "question,response,links,last_updated,country,tags"


def ask(prompt: str, default: str = "") -> str:
    if not sys.stdin.isatty():
        line = sys.stdin.readline()
        return (line.strip() or default)
    v = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    return v or default


def parse_report(s: str) -> str | None:
    m = UUID.search(s or "")
    return m.group(0).lower() if m else None


def call(params: dict, key: str) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "Accept": "application/json"})
    for attempt in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=120))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code == 429 or e.code >= 500:
                time.sleep(3 * (attempt + 1))
                continue
            if e.code in (401, 403):
                sys.exit(f"Ahrefs API refused the key ({e.code}). Check AHREFS_API_KEY has Brand Radar access. {body}")
            sys.exit(f"Ahrefs API error {e.code}: {body}")
        except urllib.error.URLError as e:
            if attempt == 3:
                sys.exit(f"Couldn't reach api.ahrefs.com: {e}")
            time.sleep(3)
    sys.exit("Ahrefs API kept failing; try again later.")


def pull(report: str, surface: str, day: str, key: str) -> list[dict]:
    rows, offset = [], 0
    while True:
        d = call({"report_id": report, "prompts": "custom", "data_source": surface, "date": day,
                  "select": FIELDS, "limit": 1000, "offset": offset}, key)
        if "ai_responses" not in d:
            sys.exit(f"Unexpected API response for {surface} on {day}: {str(d)[:300]}")
        page = d["ai_responses"]
        rows += page
        if len(page) < 1000:
            return rows
        offset += 1000


def dedupe(rows: list[dict]) -> tuple[list[dict], int]:
    """The API can return one question twice for a surface and day (an older
    and newer answer). Keep the most recently updated one."""
    best = {}
    for r in rows:
        k = (r.get("question") or "").strip().lower()
        if k and (k not in best or (r.get("last_updated") or "") > (best[k].get("last_updated") or "")):
            best[k] = r
    return list(best.values()), len(rows) - len(best)


def write_brand(path: Path, args) -> None:
    print("\nThe Ahrefs API doesn't share a report's brand settings, so tell me who's who.")
    print("Use the same brand and competitors as in the Brand Radar report.\n")
    label = args.brand or ask("Your brand's name (as people write it)")
    if not label:
        sys.exit("A brand name is required.")
    variants = args.variants or ask("Other names or spellings for it, comma-separated (optional)")
    domain = args.domain or ask("Your website's domain, e.g. example.com")
    comps = args.competitors or ask("Competitors, comma-separated")
    category = args.category or ask("Your market in a few words, e.g. 'project management software'")
    generic = args.generic_tool or ask("What an unnamed recommendation looks like", "a product in this category")
    split = lambda s: [x.strip() for x in (s or "").split(",") if x.strip()]  # noqa: E731
    y = [f"brand: {label.lower()}", f"label: {label}", f"category: {category}", f"generic_tool: {generic}",
         "variants:"] + [f"  - {v.lower()}" for v in split(variants)] + \
        ["products: []", "competitors:"] + [f"  - {c.lower()}" for c in split(comps)] + \
        ["competitor_variants: []", "owned_domains:"] + [f"  - {d.lower()}" for d in split(domain)] + \
        ["competitor_domains: []", "ugc_domains:", "  - reddit.com", "  - youtube.com", "  - quora.com",
         "  - medium.com", "  - g2.com", "  - trustpilot.com", "disambiguation: []", "win_rate_rule: per_answer",
         "fact_sheet: false", "bot_analytics: false", "tracked_pages: []", ""]
    y.insert(0, "# Written by fetch_report.py. Edit freely: add products, competitor domains and\n"
                "# disambiguation lines (see 08-adapting/brand.yaml for what each field does).")
    path.write_text("\n".join(y), encoding="utf-8")
    print(f"wrote {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", help="Brand Radar report URL or id")
    ap.add_argument("--days", type=int, default=1, help="whole days to pull, ending --end (default 1)")
    ap.add_argument("--end", help="last day to pull, YYYY-MM-DD (default: yesterday, UTC; scans finish late in the day)")
    ap.add_argument("--surfaces", help="comma-separated; default: every surface that has answers")
    ap.add_argument("--out")
    ap.add_argument("--brand"); ap.add_argument("--variants"); ap.add_argument("--domain")
    ap.add_argument("--competitors"); ap.add_argument("--category"); ap.add_argument("--generic-tool")
    a = ap.parse_args()

    raw = a.report or ask("Which Brand Radar report should I measure? Paste its URL or id")
    report = parse_report(raw)
    if not report:
        sys.exit("That doesn't look like a Brand Radar report URL or id. Open the report in Ahrefs and copy "
                 "the address: it contains a long id made of letters, digits and dashes.")
    key = os.environ.get("AHREFS_API_KEY") or ask("Ahrefs API key (or set AHREFS_API_KEY)")
    if not key:
        sys.exit("An Ahrefs API key with Brand Radar access is required.")

    end = dt.date.fromisoformat(a.end) if a.end else dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)
    days = [(end - dt.timedelta(days=i)).isoformat() for i in range(a.days)][::-1]
    out = Path(a.out or f"report/{report}")
    out.mkdir(parents=True, exist_ok=True)

    # Which surfaces does the report track? Probe the last day.
    surfaces = [s.strip() for s in a.surfaces.split(",")] if a.surfaces else SURFACES
    answers, per, dup_total, questions = [], {}, 0, {}
    active = []
    for s in surfaces:
        rows, dups = dedupe(pull(report, s, days[-1], key))
        if rows:
            active.append(s)
            per[(s, days[-1])] = rows
            dup_total += dups
    if not active:
        sys.exit(f"No custom-question answers on {days[-1]} for report {report}. Check the id, that the report "
                 "has custom prompts, and try an earlier --end date.")
    for day in days[:-1]:
        for s in active:
            rows, dups = dedupe(pull(report, s, day, key))
            per[(s, day)] = rows
            dup_total += dups

    for (s, day), rows in per.items():
        for r in rows:
            q = (r.get("question") or "").strip()
            questions.setdefault(q.lower(), {"query": q, "tags": ",".join(map(str, r.get("tags") or []))})
            answers.append({"question": q, "model": s, "date": day, "response": r.get("response") or "",
                            "country": r.get("country"),
                            "sitelinks": [{"url": l.get("url"), "title": l.get("title")}
                                          for l in (r.get("links") or []) if l.get("url")]})

    n_q = len(questions)
    expected = n_q * len(active) * len(days)
    per_surface = {s: sum(len(per.get((s, d), [])) for d in days) for s in active}
    short = {s: n for s, n in per_surface.items() if n < 0.9 * n_q * len(days)}

    import csv
    with open(out / "prompts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["query", "tags"])
        w.writeheader()
        w.writerows(sorted(questions.values(), key=lambda x: x["query"].lower()))
    with open(out / "answers.jsonl", "w", encoding="utf-8") as f:
        for x in answers:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    (out / "fetch.json").write_text(json.dumps({
        "report_id": report, "days": days, "surfaces": active, "questions": n_q, "answers": len(answers),
        "expected": expected, "per_surface": per_surface, "duplicates_dropped": dup_total,
        "cited_flag": False, "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")},
        indent=1), encoding="utf-8")

    print(f"\nReport {report}: {n_q} questions · {len(active)} AI surfaces ({', '.join(active)}) · "
          f"{len(days)} day(s) ending {days[-1]}")
    print(f"Answers: {len(answers)} of {expected} expected (questions × surfaces × days)"
          + (f"; {dup_total} duplicate answers dropped" if dup_total else ""))
    if short:
        print("  ! fewer answers than questions on: " + ", ".join(f"{s} ({n})" for s, n in short.items())
              + ". Scans for that day may be incomplete; try an earlier --end.")
    if len(answers) < 0.9 * expected:
        print("  ! More than 10% of answers are missing. Don't build on this sample; pull an earlier day.")

    bpath = out / "brand.yaml"
    if not bpath.exists():
        write_brand(bpath, a)

    print("\nNext:")
    print(f"  python3 scripts/propose.py --from-report {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
