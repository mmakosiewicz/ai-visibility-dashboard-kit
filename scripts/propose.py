#!/usr/bin/env python3
"""Propose how to classify YOUR prompts and which metrics to build, checked on sample answers.

    python3 scripts/fetch_report.py                 # 1. which Brand Radar report? pulls it
    python3 scripts/propose.py --from-report report/<id>/   # 2. the proposal

    (or just `python3 scripts/propose.py`: with no inputs it asks for the report first)

Writes three files into --out, all from the same data:

    proposal.html the report: one self-contained page (layout in 09-proposal/report-structure.md)
    proposal.md   the same report as Markdown
    shapes.csv    one row per prompt: group, shape, reason, and a review flag. Edit this.
    plan.json     the build config an agent reads: groups -> prompts -> metrics to build

The loop: run it, read proposal.md, fix shapes.csv by hand, re-run with
--from-shapes proposal/shapes.csv (no model call for classification, just
recomputes the sample), repeat until the plan looks right, then build from plan.json.

Classification uses an LLM (any OpenAI-compatible endpoint: OPENAI_BASE_URL,
OPENAI_API_KEY, --model). Without one, either pass --no-llm (groups from the tag
column, types from the word rules) or write shapes.csv yourself and pass
--from-shapes. That's the path for a chat assistant: it sorts the questions
itself, grades the answers itself, and this script only does the arithmetic and
the page. See 09-proposal/for-chat-assistants.md.

Sample answers: a few days of raw answers exported from Brand Radar, as JSONL,
a JSON list, or CSV with columns question, model (surface), response, sitelinks
(a JSON list of {url, cited}). The script grades them with the grader template
filled from brand.yaml. If the rows already carry the grader's fields
(mentioned, position, brands, tool_recommended, tool_names, verdict_winner,
sentiment), it uses them and grades nothing.

Everything here is a SAMPLE CHECK: it tells you whether a metric will have a
denominator worth reading, not what the metric's value is.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fit_report import QUESTIONS, classify, read_yaml_lite, word_re  # noqa: E402
import plain_language as PL  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MENU = json.loads((ROOT / "09-proposal" / "metric-menu.json").read_text())
SHAPES = list(MENU["shapes"].keys())
BRAND_NUMERATOR = {"mention_rate", "top_three_rate", "win_rate", "capture", "cohort_sov", "owned_citation_share"}
GRADED_FIELDS = {"mentioned", "tool_recommended", "verdict_winner"}


# ---------------------------------------------------------------- inputs

def load_prompts(path: str) -> list[dict]:
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    if not rows:
        sys.exit("prompts.csv is empty")
    cols = {c.lower(): c for c in rows[0]}
    q = next((cols[c] for c in ("query", "prompt", "question", "keyword") if c in cols), None)
    if not q:
        sys.exit("prompts.csv needs a 'query' (or prompt/question) column")
    tag = next((cols[c] for c in ("tags", "tag", "group", "board_group") if c in cols), None)
    out, seen = [], set()
    for r in rows:
        text = (r[q] or "").strip()
        if not text or text.lower() in seen:
            continue
        seen.add(text.lower())
        out.append({"id": f"p{len(out) + 1}", "prompt": text, "tag": (r.get(tag) or "").strip() if tag else ""})
    return out


def load_answers(path: str | None) -> list[dict]:
    if not path:
        return []
    p = Path(path)
    txt = p.read_text(encoding="utf-8")
    if p.suffix == ".csv":
        rows = list(csv.DictReader(txt.splitlines()))
    elif txt.lstrip().startswith("["):
        rows = json.loads(txt)
    else:
        rows = [json.loads(l) for l in txt.splitlines() if l.strip()]
    out = []
    for r in rows:
        sl = r.get("sitelinks") or []
        if isinstance(sl, str):
            try:
                sl = json.loads(sl) if sl.strip() else []
            except json.JSONDecodeError:
                sl = []
        a = {"question": (r.get("question") or r.get("prompt") or r.get("query") or "").strip(),
             "surface": r.get("model") or r.get("surface") or "",
             "date": str(r.get("date") or r.get("snap_date") or ""),
             "response": r.get("response") or "", "sitelinks": sl}
        g = r.get("grade") if isinstance(r.get("grade"), dict) else {k: r[k] for k in r if k in
             ("mentioned", "position", "brands", "tool_recommended", "tool_names", "verdict_winner", "sentiment")}
        if GRADED_FIELDS <= set(g):
            for k in ("brands", "tool_names"):
                if isinstance(g.get(k), str):
                    g[k] = json.loads(g[k]) if g[k].startswith("[") else [x for x in g[k].split(";") if x]
            for k in ("mentioned", "tool_recommended"):
                if isinstance(g.get(k), str):
                    g[k] = g[k].strip().lower() in ("true", "1", "yes")
            a["grade"] = g
        out.append(a)
    return out


def brand_config(path: str, category: str | None) -> dict:
    b = read_yaml_lite(path)
    name = str(b.get("brand", "")).lower()
    terms = [t for t in [name] + [v.lower() for v in b.get("variants", [])]
             + [v.lower() for v in b.get("products", [])] if t]
    comps = [c.lower() for c in b.get("competitors", [])]
    comp_terms = comps + [v.lower() for v in b.get("competitor_variants", [])]
    return {
        "brand": name, "label": b.get("label") or name.title(), "terms": terms,
        "competitors": comps, "comp_terms": comp_terms,
        "category": category or b.get("category") or "",
        "generic_tool": b.get("generic_tool") or "a product in this category",
        "products": b.get("products", []), "disambiguation": b.get("disambiguation", []),
        "owned": b.get("owned_domains", []), "competitor_domains": b.get("competitor_domains", []),
        "ugc": b.get("ugc_domains", []),
        "fact_sheet": b.get("fact_sheet") not in ("", [], None, "false", "no"),
        "bot_analytics": b.get("bot_analytics") not in ("", [], None, "false", "no"),
        "tracked_pages": bool(b.get("tracked_pages")),
        "win_rate_rule": b.get("win_rate_rule") or "per_prompt",
    }


# ------------------------------------------------------------------- llm

def llm(system: str, user: str, model: str, max_tokens: int = 6000) -> dict:
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    headers = {"Content-Type": "application/json"}
    if os.environ.get("OPENAI_API_KEY"):
        headers["Authorization"] = "Bearer " + os.environ["OPENAI_API_KEY"]
    body = json.dumps({"model": model, "temperature": 0, "max_tokens": max_tokens,
                       "response_format": {"type": "json_object"},
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    last = None
    for _ in range(3):
        try:
            req = urllib.request.Request(base + "/chat/completions", data=body, headers=headers)
            r = json.load(urllib.request.urlopen(req, timeout=240))
            t = r["choices"][0]["message"]["content"] or ""
            return json.loads(t[t.find("{"): t.rfind("}") + 1])
        except Exception as e:  # noqa: BLE001 — retried, then raised
            last = e
    raise RuntimeError(f"LLM call failed: {last}")


def propose_groups(prompts, bc, model) -> dict:
    labels = ", ".join(m["label"] for m in MENU["metrics"].values())
    max_groups = max(3, min(16, len(prompts) // 5))
    sys_p = f"""You are helping someone measure how AI assistants answer the prompts they track
for their brand, {bc['label']}, in the market: {bc['category'] or 'infer it from the prompts'}. Tracked competitors: {', '.join(bc['competitors']) or 'none'}.

Read ALL the prompts below and propose groups IN THE USER'S OWN TERMS: the jobs,
worries or buying moments the prompts express, not generic labels like "list prompts".

Rules:
- Aim for groups of 5+ prompts. Fewer, larger groups beat many small ones:
  about one group per 7-10 prompts, never more than {max_groups}.
- Prompts in a group should share what a reader would DO with the answer.
- If some prompts have nothing to do with the market, put them in one group
  called "Outside the market" rather than forcing them elsewhere.
- If a measurement need is visible in the prompts that none of these metrics
  could serve ({labels}), say so in unmet_needs. Don't propose a metric.

Return STRICT JSON: {{"groups":[{{"name":str,"description":str}}],"unmet_needs":[str],"set_notes":str}}"""
    return llm(sys_p, "\n".join(p["prompt"] for p in prompts), model)


def assign(prompts, groups, model) -> dict:
    shape_txt = "\n".join(f"- {k}: {v}" for k, v in MENU["shapes"].items())
    gnames = [g["name"] for g in groups]
    sys_p = f"""Assign each prompt to exactly one group and one shape.

Groups: {json.dumps(groups)}

Shapes (use exactly these words):
{shape_txt}

Rules:
- Shape follows what the prompt NAMES and ASKS, not its topic.
- "Which X...?", "best X", "X with <feature>" (a product finder) -> list.
- "how do I...", "set up...", "fix...", "can I..." -> task.
- definitions, "is X worth it", "X vs Y" between two CONCEPTS, reasoning -> category.
- Use none only when no answer could reasonably name a product in this market.
- reason: max 12 words, why this shape.

Return STRICT JSON: {{"assignments":[{{"id":str,"group":str,"shape":str,"reason":str}}]}}"""
    out = {}
    for i in range(0, len(prompts), 80):
        batch = prompts[i:i + 80]
        r = llm(sys_p, json.dumps([{"id": p["id"], "prompt": p["prompt"]} for p in batch]), model)
        for a in r.get("assignments", []):
            if a.get("id") and a.get("group") in gnames and a.get("shape") in SHAPES:
                out[a["id"]] = a
    return out


def classify_all(prompts, bc, args) -> tuple[list[dict], dict]:
    """Returns rows (id, prompt, group, shape, rule_shape, review, reason) and set-level meta."""
    meta = {"unmet_needs": [], "set_notes": "", "groups": []}
    if args.from_shapes:
        prev = {r["prompt"].strip().lower(): r for r in csv.DictReader(open(args.from_shapes, encoding="utf-8"))}
        prev_plan = Path(args.from_shapes).with_name("plan.json")
        if prev_plan.exists():
            pj = json.loads(prev_plan.read_text())
            meta.update(unmet_needs=pj.get("unmet_needs", []), set_notes=pj.get("set_notes", ""),
                        groups=[{"name": g["name"], "description": g.get("description", "")} for g in pj["groups"]])
        assigned = {}
        for p in prompts:
            r = prev.get(p["prompt"].lower())
            if r:
                sh = (r.get("shape") or "").strip().lower()
                assigned[p["id"]] = {"group": (r.get("group") or "").strip() or "Ungrouped",
                                     "shape": sh if sh in SHAPES else "category",
                                     "reason": r.get("reason", "") or "set by hand"}
        if not meta["groups"]:  # a shapes.csv written by hand or by a chat assistant, no plan.json yet
            desc = {}
            for r in prev.values():
                if (r.get("group_description") or "").strip():
                    desc.setdefault(r["group"].strip(), r["group_description"].strip())
            seen = []
            for a in assigned.values():
                if a["group"] not in seen:
                    seen.append(a["group"])
            meta["groups"] = [{"name": g, "description": desc.get(g, "")} for g in seen]
    elif args.no_llm:
        assigned = {}
        for p in prompts:
            assigned[p["id"]] = {"group": p["tag"] or "Ungrouped", "shape": classify(p["prompt"], bc["terms"], bc["comp_terms"]),
                                 "reason": "word rules (--no-llm)"}
    else:
        g = propose_groups(prompts, bc, args.model)
        meta.update(unmet_needs=g.get("unmet_needs", []), set_notes=g.get("set_notes", ""), groups=g.get("groups", []))
        assigned = assign(prompts, meta["groups"], args.model)

    known = {g["name"] for g in meta["groups"]}
    rows = []
    for p in prompts:
        a = assigned.get(p["id"])
        rule = classify(p["prompt"], bc["terms"], bc["comp_terms"])
        review = []
        if not a:
            a = {"group": p["tag"] or "Ungrouped", "shape": rule, "reason": "not assigned; word rules"}
            review.append("unassigned")
        shape = a["shape"]
        # brand / competitor tokens are facts, not judgments
        names_brand = any(word_re(t).search(p["prompt"].lower()) for t in bc["terms"])
        names_comp = any(word_re(t).search(p["prompt"].lower()) for t in bc["comp_terms"])
        if names_brand:
            shape = "branded"
        elif names_comp:
            shape = "conquest"
        elif shape in ("branded", "conquest"):
            # the model saw a product or organisation name, but not one you track
            shape = rule if rule not in ("branded", "conquest") else "category"
        if shape != a["shape"]:
            review.append(f"model said {a['shape']}; " + ("names a tracked brand" if names_brand or names_comp
                                                         else "names no tracked brand"))
        elif shape != rule and not args.no_llm:
            review.append(f"word rules say {rule}")
        if a["group"] not in known:
            meta["groups"].append({"name": a["group"], "description": ""})
            known.add(a["group"])
        rows.append({"id": p["id"], "prompt": p["prompt"], "group": a["group"], "shape": shape,
                     "rule_shape": rule, "review": "; ".join(review), "reason": a.get("reason", "")})
    return rows, meta


# ----------------------------------------------------------------- grade

def grader_prompt(bc) -> str:
    dis = "\n".join(bc["disambiguation"])
    prods = ", ".join(bc["products"]) or "none listed"
    return f"""You grade one AI-assistant answer about {bc['category'] or 'this market'}. The brand we track is {bc['label']} (including its products: {prods}).
{dis}
Return STRICT JSON only:
{{
 "mentioned": bool,           // {bc['label']} or one of its products is named in the answer's TEXT. A link or citation to {bc['label']}'s website alone is not a mention (that's a citation)
 "position": int|null,        // 1-based order of {bc['label']} among DISTINCT brands as they first appear; null if not mentioned
 "brands": [str],             // distinct brands/companies named, lowercase, in order of first appearance; fold products into the company
 "tool_recommended": bool,    // true ONLY if the answer tells the reader to use/buy a NAMED product. Passing mentions, generic "use {bc['generic_tool']}", or pure explanations are false.
 "tool_names": [str],         // the named products it recommends, lowercase, company-level; [] if tool_recommended is false
 "verdict_winner": str|null,  // the ONE brand the answer overall recommends over the others, lowercase. null is EXPECTED and CORRECT when there is no single winner.
 "sentiment": "positive"|"neutral"|"mixed"|"negative"|null  // toward {bc['label']}; null if not mentioned
}}"""


def grade_sample(answers, bc, model, workers) -> int:
    todo = [a for a in answers if "grade" not in a]
    if not todo:
        return 0
    sys_p = grader_prompt(bc)

    def one(a):
        if not a["response"].strip():
            return {"mentioned": False, "position": None, "brands": [], "tool_recommended": False,
                    "tool_names": [], "verdict_winner": None, "sentiment": None}
        g = llm(sys_p, f"Prompt asked: {a['question']}\n\nAnswer:\n{a['response'][:9000]}", model, 2000)
        # the brand's name in the prose decides "mentioned", both ways; a name that only
        # appears inside a link or citation is a citation, not a mention (same rule as
        # Brand Radar's own mention counts)
        in_text = named_in_text(a["response"], bc["terms"])
        if in_text != bool(g.get("mentioned")):
            g["mentioned"] = in_text
            g["mention_fixed"] = True
            if not in_text:
                g["position"] = None
                g["sentiment"] = None
        return g

    with cf.ThreadPoolExecutor(workers) as ex:
        for a, g in zip(todo, ex.map(lambda x: _safe(one, x), todo)):
            a["grade"] = g
    return len(todo)


LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)|https?://\S+")


def named_in_text(response: str, terms) -> bool:
    """Brand named in the answer's prose: markdown links keep their visible label
    unless it's just a domain; bare URLs are dropped."""
    def keep(m):
        label = m.group(1) or ""
        return "" if (not label or re.fullmatch(r"[\w.-]+\.[a-z]{2,}(/\S*)?", label.strip(), re.I)) else label
    prose = LINK.sub(keep, response or "").lower()
    return any(word_re(t).search(prose) for t in terms)


def _safe(fn, x):
    try:
        return fn(x)
    except Exception as e:  # noqa: BLE001 — a failed grade is recorded, not imputed
        return {"error": str(e)[:200]}


# --------------------------------------------------------------- metrics

def _host(url: str) -> str:
    h = (urlparse(url if "//" in url else "//" + url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def _in(h: str, doms) -> bool:
    return any(h == d or h.endswith("." + d) for d in (x.lower() for x in doms))


def _is_brand(name: str | None, terms) -> bool:
    n = (name or "").lower().strip()
    return any(n == t or n.startswith(t + " ") for t in terms)


def _in_cohort(name: str, terms) -> bool:
    return _is_brand(name, terms)


def compute(metric: str, answers: list[dict], bc) -> tuple[int, int] | None:
    """(numerator, denominator) over graded answers, or None if not computable here."""
    g = [a for a in answers if "grade" in a and "error" not in a["grade"]]
    G = [a["grade"] for a in g]
    men = [x for x in G if x.get("mentioned")]
    if metric == "mention_rate":
        return len(men), len(G)
    if metric == "position":
        pos = [x["position"] for x in men if isinstance(x.get("position"), int)]
        return (sum(pos), len(pos)) if pos else (0, 0)
    if metric == "top_three_rate":
        pos = [x["position"] for x in men if isinstance(x.get("position"), int)]
        return sum(p <= 3 for p in pos), len(pos)
    if metric == "win_rate":
        # decided verdicts in answers that name you: a rival winning an answer
        # you're absent from is not your loss (02-prompts/shapes.md, per-answer rule)
        dec = [x for x in G if x.get("verdict_winner") and x.get("mentioned")]
        return sum(_is_brand(x["verdict_winner"], bc["terms"]) for x in dec), len(dec)
    if metric == "capture":
        tools = [x for x in G if x.get("tool_recommended")]
        return sum(any(_is_brand(t, bc["terms"]) for t in x.get("tool_names") or []) for x in tools), len(tools)
    if metric == "tool_recommendation_rate":
        return sum(bool(x.get("tool_recommended")) for x in G), len(G)
    if metric == "cohort_sov":
        cohort = bc["terms"] + bc["comp_terms"]
        ours = sum(1 for x in G for b in x.get("brands") or [] if _is_brand(b, bc["terms"]))
        allc = sum(1 for x in G for b in x.get("brands") or [] if _in_cohort(b, cohort))
        return ours, allc
    if metric == "negative_rate":
        return sum(x.get("sentiment") in ("negative", "mixed") for x in men), len(men)
    if metric in ("owned_citation_share", "citation_split"):
        # each website counted once per answer: the same unit Brand Radar's cited-domains uses
        hosts = [h for a in answers for h in _answer_hosts(a)]
        return sum(_in(h, bc["owned"]) for h in hosts), len(hosts)
    return None


def _answer_hosts(a) -> set:
    return {_host(s["url"]) for s in a["sitelinks"] if s.get("cited", True) and s.get("url")} - {""}


def split_counts(answers, bc) -> dict:
    c = Counter()
    for a in answers:
        for h in _answer_hosts(a):
            c["owned" if _in(h, bc["owned"]) else "competitor" if _in(h, bc["competitor_domains"])
              else "ugc" if _in(h, bc["ugc"]) else "third-party"] += 1
    return dict(c)


def split_detail(answers, bc) -> str:
    cited = [h for a in answers for h in _answer_hosts(a)]
    if not cited:
        return "no confirmed citations"
    c = Counter()
    for h in cited:
        c["owned" if _in(h, bc["owned"]) else "competitor" if _in(h, bc["competitor_domains"])
          else "ugc" if _in(h, bc["ugc"]) else "third-party"] += 1
    return " · ".join(f"{k} {v * 100 // len(cited)}%" for k, v in c.most_common())


def fmt(metric, num, den) -> str:
    if den == 0 or metric == "citation_split":
        return "—"
    if metric == "position":
        return f"{num / den:.1f}"
    return f"{num * 100 / den:.0f}%"


def verdict(metric, num, den, bc, n_answers, spec, scale, applies=99) -> tuple[str, str]:
    """keep | zero | thin | unavailable, plus a one-line why. `scale` projects the
    sample denominator to one week at full volume."""
    if spec.get("requires") == "fact_sheet" and not bc["fact_sheet"]:
        return "unavailable", "needs an approved fact sheet (brand.yaml fact_sheet)"
    if spec.get("sampled") is False:
        return "keep", "not computed on the sample; needs claim checking against the fact sheet"
    week = den * scale
    if applies < 5 and metric not in ("owned_citation_share", "citation_split"):
        return "thin", f"only {applies} prompt(s) in this group have a shape this metric fits"
    if den == 0:
        base = {"position": "you are never mentioned", "top_three_rate": "you are never mentioned",
                "negative_rate": "you are never mentioned", "win_rate": "no answer that names you picks a winner",
                "capture": "no answer recommends a named product", "cohort_sov": "no cohort brand is named",
                "owned_citation_share": "no confirmed citations", "citation_split": "no confirmed citations"}
        return "zero", "no denominator in the sample: " + base.get(metric, "nothing to count")
    if week < spec.get("min_n", 20):
        return "thin", f"≈{week:.0f}/week at full volume; under the {spec.get('min_n', 20)} this metric needs to be readable"
    if num == 0 and metric in BRAND_NUMERATOR:
        return "floor", (f"0 of {den}: the card would read 0% every day. Right as a baseline if you're "
                         "trying to enter these answers; otherwise drop it")
    return "keep", f"≈{week:.0f}/week in the denominator at full volume"


# ------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--from-report", help="folder written by fetch_report.py (prompts.csv, answers.jsonl, brand.yaml)")
    ap.add_argument("--prompts")
    ap.add_argument("--brand")
    ap.add_argument("--answers", help="sample answers (JSONL / JSON / CSV); optional but it's the point")
    ap.add_argument("--category", help="market in the reader's words; else brand.yaml `category`")
    ap.add_argument("--out", default="proposal")
    ap.add_argument("--model", default=os.environ.get("PROPOSE_MODEL", "gpt-4.1-mini"))
    ap.add_argument("--grade-model", default=None, help="model for grading the sample; defaults to --model")
    ap.add_argument("--surfaces", type=int, default=None, help="AI surfaces per prompt per day; inferred from the sample")
    ap.add_argument("--no-llm", action="store_true", help="tags + word rules only; grade nothing")
    ap.add_argument("--from-shapes", help="reuse an edited shapes.csv instead of classifying again")
    ap.add_argument("--sorted-by", help="who sorted the questions, shown in the footer (default: from the input)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--report-id", help="the Brand Radar report the questions come from (read from fetch.json with --from-report)")
    ap.add_argument("--demo", action="store_true", help="made-up data for a demo the user asked for; the report is labelled as such")
    args = ap.parse_args()
    if not args.from_report and not args.prompts:
        # Everything starts from a Brand Radar report: fetch it first.
        print("No report folder given. Step one is pulling a Brand Radar report.\n")
        import subprocess
        rc = subprocess.call([sys.executable, str(Path(__file__).with_name("fetch_report.py"))])
        if rc:
            return rc
        folders = sorted(Path("report").glob("*/fetch.json"), key=lambda p: p.stat().st_mtime)
        if not folders:
            sys.exit("fetch_report.py didn't write a report folder.")
        args.from_report = str(folders[-1].parent)
    if args.from_report:
        d = Path(args.from_report)
        for f in ("prompts.csv", "answers.jsonl", "brand.yaml"):
            if not (d / f).exists():
                sys.exit(f"{d / f} is missing. Run scripts/fetch_report.py first.")
        args.prompts = args.prompts or str(d / "prompts.csv")
        args.brand = args.brand or str(d / "brand.yaml")
        args.answers = args.answers or str(d / "answers.jsonl")
        if args.out == "proposal":
            args.out = str(d / "proposal")
    if not args.brand:
        sys.exit("--brand is required with --prompts (or use --from-report).")
    report_id = args.report_id
    if args.from_report and (Path(args.from_report) / "fetch.json").exists():
        report_id = report_id or json.loads((Path(args.from_report) / "fetch.json").read_text()).get("report_id")
    if not report_id and not args.demo:
        sys.exit("Which Brand Radar report are these questions from? Every proposal starts from the user's own report:\n"
                 "  run scripts/fetch_report.py (or propose.py with no arguments), or pass --report-id <id from the report's URL>.\n"
                 "Only for a demo the user asked for: --demo (the report is labelled as made-up data).")
    if report_id and (not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", report_id.strip(), re.I)
                      or report_id.strip().lower().startswith("0190a1b2-c3d4")):
        sys.exit(f"{report_id!r} isn't a Brand Radar report id (copy it from app.ahrefs.com/brand-radar/reports/<id>/…).")

    bc = brand_config(args.brand, args.category)
    prompts = load_prompts(args.prompts)
    answers = load_answers(args.answers)
    rows, meta = classify_all(prompts, bc, args)
    graded_now = 0 if args.no_llm else grade_sample(answers, bc, args.grade_model or args.model, args.workers)
    for a in answers:  # one mention rule for every answer, whoever graded it
        g = a.get("grade")
        if g and "error" not in g and a["response"]:
            in_text = named_in_text(a["response"], bc["terms"])
            if in_text != bool(g.get("mentioned")):
                g.update(mentioned=in_text, mention_fixed=True)
                if not in_text:
                    g.update(position=None, sentiment=None)

    by_prompt = defaultdict(list)
    for a in answers:
        by_prompt[a["question"].lower()].append(a)
    for r in rows:
        r["answers"] = len(by_prompt[r["prompt"].lower()])
    fetch_meta = {}
    if args.from_report and (Path(args.from_report) / "fetch.json").exists():
        fetch_meta = json.loads((Path(args.from_report) / "fetch.json").read_text())
    sample_days = len({a["date"] for a in answers if a["date"]}) or 1
    surfaces = args.surfaces or len({a["surface"] for a in answers if a["surface"]}) or 4

    shape_n = Counter(r["shape"] for r in rows)
    groups_out, flat_headline = [], []
    for g in meta["groups"]:
        grows = [r for r in rows if r["group"] == g["name"]]
        if not grows:
            continue
        mix = Counter(r["shape"] for r in grows)
        dom, dom_n = mix.most_common(1)[0]
        metrics = []
        for mid, spec in MENU["metrics"].items():
            elig = [r for r in grows if r["shape"] in spec["shapes"]]
            if not elig:
                continue
            ans = [a for r in elig for a in by_prompt[r["prompt"].lower()]]
            n_graded = sum("grade" in a and "error" not in a["grade"] for a in ans)
            # sample -> one week at full volume for these prompts
            per_week_answers = len(elig) * surfaces * 7
            scale = per_week_answers / max(1, n_graded if mid not in ("owned_citation_share", "citation_split") else len(ans))
            if not ans or (n_graded == 0 and mid not in ("owned_citation_share", "citation_split")):
                num = den = 0
                v, why = ("unavailable", "no graded sample answers for these prompts") if spec.get("sampled") is not False \
                    else verdict(mid, 0, 0, bc, 0, spec, 0)
            else:
                num, den = compute(mid, ans, bc) or (0, 0)
                v, why = verdict(mid, num, den, bc, len(ans), spec, scale, len(elig))
            note = spec.get("notes", {}).get(dom, "")
            metrics.append({"id": mid, "label": spec["label"], "verdict": v, "why": why,
                            "applies_to": len(elig), "of": len(grows),
                            "sample": {"num": num, "den": den, "value": fmt(mid, num, den)},
                            "detail": split_detail(ans, bc) if mid == "citation_split" else "",
                            "split": split_counts(ans, bc) if mid == "citation_split" else None,
                            "looked_at": n_graded if mid not in ("owned_citation_share", "citation_split") else len(ans),
                            "note": note, "doc": spec["doc"]})
        # prefer a headline that moves: a keep with a non-zero sample, then any keep, then a floor
        cands = [m for h in MENU["headline_by_shape"][dom] for m in metrics if m["id"] == h]
        headline = next((m for m in cands if m["verdict"] == "keep" and m["sample"]["num"] > 0), None) \
            or next((m for m in cands if m["verdict"] == "keep"), None) \
            or next((m for m in cands if m["verdict"] == "floor"), None)
        if headline and headline["verdict"] == "keep" and headline["sample"]["num"] == 0:
            flat_headline.append(g["name"])
        groups_out.append({
            "name": g["name"], "description": g.get("description", ""),
            "prompts": [r["id"] for r in grows], "n_prompts": len(grows),
            "shape_mix": dict(mix), "dominant_shape": dom, "mixed": dom_n / len(grows) < 0.6,
            "sample_answers": sum(len(by_prompt[r["prompt"].lower()]) for r in grows),
            "headline": headline["id"] if headline else None, "metrics": metrics,
        })

    n = len(rows)
    none_share = shape_n["none"] / n if n else 0
    scored = n - shape_n["none"]
    if none_share > 0.5:
        set_verdict = "citations-only"
    elif none_share > 0.2 or scored < 15:
        set_verdict = "partial"
    else:
        set_verdict = "full"

    fr_shapes = Counter({k: shape_n[k] for k in ("branded", "conquest", "list", "task", "category")})
    fr_shapes["branded_comparison"] = sum(1 for r in rows if r["shape"] == "branded" and re.search(
        r"\b(vs\.?|versus|or|better than|compared? (to|with)|alternatives?)\b", r["prompt"].lower()))
    have = {"fact_sheet": bc["fact_sheet"], "bot_analytics": bc["bot_analytics"], "tracked_pages": bc["tracked_pages"]}
    questions = [(q, bool(f(fr_shapes, have))) for q, f in QUESTIONS]

    warnings = []
    small = [g["name"] for g in groups_out if g["n_prompts"] < 5]
    if small:
        warnings.append(f"Groups under 5 prompts: {', '.join(small)}. Merge them, or their cards flip on one answer.")
    mixed = [g["name"] for g in groups_out if g["mixed"]]
    if mixed:
        warnings.append(f"Mixed-shape groups: {', '.join(mixed)}. Each metric is computed only on the prompts whose shape allows it (see 'applies to').")
    if flat_headline:
        warnings.append(f"Headline reads 0 on the sample for: {', '.join(flat_headline)}. Nothing on the menu "
                        "for that shape moves here. Either the zero is the finding (say so on the card) or "
                        "pick a different headline by hand in plan.json.")
    rev = sum(bool(r["review"]) for r in rows)
    if rev:
        warnings.append(f"{rev} of {n} prompts flagged for review in shapes.csv (model and word rules disagree, or a brand name overrode the model).")
    if answers and not any("cited" in s for a in answers for s in a["sitelinks"]):
        warnings.append("Sample sitelinks carry no `cited` flag, so every retrieved link is counted as a citation. Citation shares will read high.")
    if not answers:
        warnings.append("No sample answers: verdicts are all 'unavailable'. Export 1–2 days from Brand Radar and re-run with --answers.")
    errs = sum(1 for a in answers if "error" in a.get("grade", {}))
    if errs:
        warnings.append(f"{errs} sample answers failed to grade and are excluded (not counted as absences).")
    if answers:
        nosample = sum(1 for r in rows if not by_prompt[r["prompt"].lower()])
        if nosample:
            warnings.append(f"{nosample} of {n} prompts have no sample answers, so their groups' verdicts rest on fewer prompts. Export a full day.")
    unmatched = len({a['question'].lower() for a in answers} - {r['prompt'].lower() for r in rows})
    if unmatched:
        warnings.append(f"{unmatched} prompts in the sample answers aren't in prompts.csv and were ignored.")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if answers:
        with open(out / "sample-graded.jsonl", "w", encoding="utf-8") as f:
            for a in answers:
                f.write(json.dumps(a, ensure_ascii=False) + "\n")
    with open(out / "shapes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "prompt", "group", "shape", "rule_shape", "review", "reason"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    plan = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "brand": bc["brand"], "label": bc["label"], "category": bc["category"],
        "report_id": report_id, "demo": args.demo or None,
        "classifier": args.sorted_by or ("a reviewed question list" if args.from_shapes
                                         else ("word rules" if args.no_llm else args.model)),
        "prompts": n, "shapes": dict(shape_n), "set_verdict": set_verdict, "set_notes": meta["set_notes"],
        "sample": {"answers": len(answers), "days": sample_days, "surfaces": surfaces, "graded_now": graded_now,
                   "surface_list": sorted({a["surface"] for a in answers if a["surface"]}) or None,
                   "expected": fetch_meta.get("expected"),
                   "cited_flag": (any("cited" in s for a in answers for s in a["sitelinks"]) if answers else None)},
        "fact_sheet": bc["fact_sheet"],
        "groups": groups_out, "unmet_needs": meta["unmet_needs"],
        "questions": {q: ok for q, ok in questions}, "warnings": warnings,
    }
    enrich(plan, rows)
    (out / "plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    (out / "proposal.md").write_text(render_md(plan, rows), encoding="utf-8")
    import render_html  # noqa: E402 — same folder
    (out / "proposal.html").write_text(render_html.render(plan, rows), encoding="utf-8")
    print(f"{n} prompts → {len(groups_out)} groups · shapes {dict(shape_n)} · set: {set_verdict} · "
          f"sample {len(answers)} answers ({graded_now} graded now) · review flags {rev}\n"
          f"wrote {out / 'proposal.html'}, {out / 'proposal.md'}, {out / 'shapes.csv'}, {out / 'plan.json'}")
    return 0


def enrich(plan: dict, rows: list[dict]) -> None:
    """Add plain-language fields to plan.json: what each metric means, its
    calculation with the sample's numbers, a readable status and reason."""
    B = plan["label"]
    for r in rows:
        r["type"] = PL.type_info(r["shape"], B)["name"]
        r["type_note"] = PL.review_note(r, B)
    for g in plan["groups"]:
        for m in g["metrics"]:
            name, what = PL.METRICS.get(m["id"], (m["label"], ""))
            m["plain"] = {
                "name": PL.f(name, B), "what": PL.f(what, B),
                "status": PL.STATUS[m["verdict"]][0], "reason": PL.reason(m, B),
                "calculation": PL.calc(m, B),
            }
    fit_title, fit_text = PL.SET_TEXT[plan["set_verdict"]]
    plan["plain"] = {"fit": fit_title, "fit_text": PL.f(fit_text, B), "notes": PL.warnings(plan, B)}


def render_md(plan, rows) -> str:
    """proposal.md: the same plain-language view as the Console page."""
    B = plan["label"]
    L = [f"# What to track for {B} in AI answers", ""]
    if plan.get("demo"):
        L += ["> **Demo: made-up data.** Nothing here comes from a real Brand Radar report.", ""]
    else:
        L += [f"Source: Ahrefs Brand Radar report `{plan.get('report_id')}`.", ""]
    s = plan["sample"]
    days = "one day" if s["days"] == 1 else f"{s['days']} days"
    L += [f"We read the {plan['prompts']} questions this report tracks, sorted them into {len(plan['groups'])} topics, "
          f"and checked which numbers are worth putting on a dashboard for each one, using {s['answers']} real AI "
          f"answers from {days}.", ""]
    if plan["set_notes"]:
        L += [plan["set_notes"], ""]
    L += [f"**{plan['plain']['fit']}.** {plan['plain']['fit_text']}", ""]
    L += ["> Numbers here come from a small sample. They show whether something is worth tracking, "
          "not what the real figure is. “3 of 12” doesn't mean 25%.", ""]

    L += ["## What kinds of questions are in this report", "", "| Questions | Type | What it means |", "|---|---|---|"]
    for k, v in sorted(plan["shapes"].items(), key=lambda x: -x[1]):
        t = PL.type_info(k, B)
        L.append(f"| {v} | {t['name']} | {t['desc']} ({t['example']}) |")
    L += ["", f"The type decides what can be measured: {B} can only “win” a question that asks for a recommendation.", ""]

    if plan["plain"]["notes"]:
        L += ["## Worth checking", ""] + [f"- {w}" for w in plan["plain"]["notes"]] + [""]

    L += ["## The dashboard this suggests", "", "One card per topic, with the number most worth watching there.", "",
          "| Topic | Questions | Main number | Calculation |", "|---|---|---|---|"]
    for g in plan["groups"]:
        h = next((m for m in g["metrics"] if m["id"] == g["headline"]), None)
        if h:
            c = h["plain"]["calculation"]
            L.append(f"| {g['name']} | {g['n_prompts']} | **{h['sample']['value']}** {h['plain']['name']} | "
                     f"{c['tech']}: {c['worked']} |")
        else:
            L.append(f"| {g['name']} | {g['n_prompts']} | nothing worth tracking | |")
    L.append("")

    by_id = {r["id"]: r for r in rows}
    order = {"keep": 0, "floor": 1, "thin": 2, "zero": 3, "unavailable": 4}
    for g in plan["groups"]:
        L += [f"## {g['name']}", ""]
        if g["description"]:
            L += [g["description"], ""]
        ms = sorted(g["metrics"], key=lambda m: (m["id"] != g["headline"], order[m["verdict"]]))
        track = [m for m in ms if m["verdict"] in ("keep", "floor")]
        skip = [m for m in ms if m["verdict"] not in ("keep", "floor")]
        L += ["### Worth tracking", ""] if track else ["Nothing here is worth tracking yet.", ""]
        for m in track:
            p, c = m["plain"], m["plain"]["calculation"]
            tags = (" · *main number*" if m["id"] == g["headline"] else "") + \
                   (f" · *{p['status'].lower()}*" if m["verdict"] == "floor" else "")
            value = "" if m["id"] == "citation_split" else f"**{m['sample']['value']}** "
            L += [f"{value}**{p['name']}**{tags}  ", f"{p['what']}  ",
                  f"`{c['tech']} = {c['formula']}`  ", f"`= {c['worked']}`  "]
            extra = (f" Based on {m['applies_to']} of {m['of']} questions in this topic; the rest don't fit this measure."
                     if m["applies_to"] != m["of"] else "")
            L += [f"{p['reason']}{extra}", ""]
        if skip:
            L += ["<details><summary>Not worth tracking here</summary>", ""]
            for m in skip:
                p, c = m["plain"], m["plain"]["calculation"]
                calc = f" `{c['formula']}`" + (f" = {c['worked']}" if m["verdict"] != "unavailable" else "")
                L.append(f"- **{p['name']}** ({c['tech']}): {p['status']}. {p['reason']}{calc}")
            L += ["", "</details>", ""]
        L += ["<details><summary>The questions in this topic</summary>", ""]
        for i in g["prompts"]:
            r = by_id[i]
            L.append(f"- *{r['type']}* · {r['prompt']}" + (f" ⚠ {r['type_note']}" if r["type_note"] else ""))
        L += ["", "</details>", ""]

    if plan["unmet_needs"]:
        L += ["## Needs no metric covers", "",
              "The AI saw these in your questions and didn't invent a metric for them:", ""]
        L += [f"- {u}" for u in plan["unmet_needs"]] + [""]

    L += ["## How to read this", "",
          "- **Topics** group questions people would ask for the same reason. An AI model proposed them; a person should check them.",
          f"- **Question types** decide what can be measured. On a general question AI rarely recommends anyone, "
          f"so the useful measure there is whether {B}'s website is used as a source.",
          "- **Calculations** show the metric's standard name, what it divides by what, and the sample's counts. "
          "The part after “÷” says which answers the percentage is out of.",
          "- **Labels:** *Worth tracking* = enough answers each week to see real changes. *Track only as a starting point* = "
          f"{B} doesn't appear yet, so it reads 0%. *Too little data*, *Nothing to measure*, *Can't measure yet* = skip.",
          "", "## Approve or edit", "",
          "1. Fix any question's `group` or `shape` in `shapes.csv`, starting with the ⚠ rows.",
          "2. Re-run with `--from-shapes <dir>/shapes.csv --answers <dir>/sample-graded.jsonl`. Nothing is re-sorted "
          "or re-graded, and the numbers are recomputed in seconds.",
          "3. When the dashboard table above is right, hand `plan.json` to the build agent (BUILD-WITH-AN-AGENT.md, "
          "step 0). Build the numbers marked worth tracking.", "",
          f"*Sorted by {plan['classifier']} · {plan['generated_at'][:10]}.*", ""]
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
