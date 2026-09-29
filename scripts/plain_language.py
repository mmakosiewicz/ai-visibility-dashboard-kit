"""Plain-language wording for proposals: question types, metric names, formulas
with the sample's numbers, and reasons. Used by propose.py for proposal.md and
the plain-language fields in plan.json. {B} is replaced by the brand label.
"""
from __future__ import annotations

import re

TYPES = {
    "branded":  ("About you", "Names {B} directly", "e.g. “{B} vs …”, “is {B} good?”"),
    "conquest": ("About a competitor", "Names a competitor, not {B}", "e.g. “is [competitor] any good?”"),
    "list":     ("Asks for recommendations", "Wants names: the best, which one, where to go", "e.g. “best … for …”, “which … should I …?”"),
    "task":     ("Asks how to do something", "Wants steps or help with a job", "e.g. “how do I …?”"),
    "category": ("General question", "Wants information, not a recommendation", "e.g. “what is …?”, “is … worth it?”"),
    "none":     ("Off-topic", "Unrelated to {B}'s market", "nothing to measure except sources"),
}

# name, what it tells you  ({B} = brand label)
METRICS = {
    "mention_rate":             ("How often {B} is named", "Out of all answers, how many name {B} in the text (a link to its site alone doesn't count)."),
    "position":                 ("How early {B} is named", "When {B} is mentioned, where it comes in the list of names. 1 = named first."),
    "top_three_rate":           ("How often {B} is in the top three", "When {B} is mentioned, how often it's one of the first three names."),
    "win_rate":                 ("How often {B} is the top pick", "When an answer picks one clear winner, how often that winner is {B}."),
    "capture":                  ("{B}'s share of recommendations", "When an answer recommends someone specific, how often that includes {B}."),
    "tool_recommendation_rate": ("How often anyone gets recommended", "How many answers recommend a specific brand or organization at all. Low means AI just gives information."),
    "cohort_sov":               ("{B} vs. competitors", "Of all mentions of {B} and its tracked competitors, the share that are {B}."),
    "negative_rate":            ("How often AI is critical of {B}", "When {B} is mentioned, how often the answer is negative or mixed about it."),
    "fact_accuracy":            ("How often AI gets facts about {B} wrong", "Checks claims in answers against a list of verified facts."),
    "owned_citation_share":     ("How often {B}'s website is a source", "Of all the websites AI cites as sources (each counted once per answer), the share that are {B}'s own."),
    "citation_split":           ("Whose websites AI uses as sources", "Sources split into {B}'s site, competitors' sites, forums and everyone else."),
}

SENTENCE = {
    "mention_rate":             "{n} of {d} answers name {B}",
    "top_three_rate":           "{n} of {d} answers that name {B} put it in the top three",
    "win_rate":                 "when there's one clear winner, it's {B} {n} of {d} times",
    "capture":                  "{n} of {d} answers that recommend someone include {B}",
    "tool_recommendation_rate": "{n} of {d} answers recommend a specific brand or organization",
    "cohort_sov":               "{B} gets {n} of {d} mentions among itself and competitors",
    "negative_rate":            "{n} of {d} answers that name {B} are negative or mixed",
    "owned_citation_share":     "{n} of {d} cited websites are {B}'s",
}

STATUS = {  # verdict -> (label, css)
    "keep":        ("Worth tracking", "ok"),
    "floor":       ("Track only as a starting point", "warn"),
    "thin":        ("Too little data", "off"),
    "zero":        ("Nothing to measure", "off"),
    "unavailable": ("Can't measure yet", "off"),
}

SET_TEXT = {
    "full": ("Good fit for a dashboard",
             "Most questions can be measured. Each topic below has at least one number worth tracking."),
    "partial": ("Partly measurable",
                "A good share of questions can't be measured beyond which websites AI cites. Build the topics that have a main number and skip the rest."),
    "citations-only": ("Only sources can be tracked",
                       "Most questions are off-topic for {B}. The only useful thing to track is which websites AI cites."),
}


def f(s: str, B: str) -> str:
    return s.replace("{B}", B)


def type_info(k: str, B: str) -> dict:
    name, desc, ex = TYPES.get(k, (k, "", ""))
    return {"key": k, "name": name, "desc": f(desc, B), "example": f(ex, B)}


def _ordinal(x: float) -> str:
    n = max(1, round(x))
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def sentence(m: dict, B: str) -> str:
    s = m["sample"]
    n, d = s["num"], s["den"]
    if d == 0:
        return ""
    if m["id"] == "position":
        return f"when named, {B} is usually the {_ordinal(n / d)} name mentioned (average {n / d:.1f}, from {d} answers)"
    if m["id"] == "citation_split":
        return _split(m.get("detail", ""), B)
    t = SENTENCE.get(m["id"])
    return f(t, B).format(n=n, d=d) if t else f"{n} of {d}"


def _split(detail: str, B: str) -> str:
    names = {"owned": f"{B}'s site", "competitor": "competitors' sites", "ugc": "forums & social",
             "third-party": "everyone else"}
    parts = []
    for chunk in detail.split(" · "):
        bits = chunk.rsplit(" ", 1)
        if len(bits) == 2:
            parts.append(f"{names.get(bits[0], bits[0])} {bits[1]}")
    return ", ".join(parts) if parts else detail


def reason(m: dict, B: str) -> str:
    why, v = m.get("why", ""), m["verdict"]
    if v == "keep":
        w = re.search(r"≈(\d+)/week", why)
        unit = {"cohort_sov": "brand mentions", "owned_citation_share": "cited websites",
                "citation_split": "cited websites"}.get(m["id"], "answers")
        return (f"About {w.group(1)} {unit} a week to count, enough to see real changes." if w
                else "Enough data to see real changes.")
    if v == "floor":
        return (f"{B} never shows up here yet, so this would read 0% every day. "
                "Worth tracking only if you're trying to get in.")
    if v == "thin":
        k = re.search(r"only (\d+) prompt", why)
        if k:
            q = int(k.group(1))
            return f"Only {q} question{'s' if q != 1 else ''} in this topic suit{'s' if q == 1 else ''} this, too few to be reliable."
        return "Too few answers a week to read reliably."
    if v == "zero":
        low = why.lower()
        if "never mentioned" in low:
            return f"{B} is never named in these answers, so there's nothing to measure."
        if "picks a winner" in low:
            return f"No answer that names {B} picks a single winner."
        if "recommends a named" in low:
            return "No answer recommends a specific brand or organization."
        if "cohort" in low:
            return "None of the tracked brands are named."
        if "citation" in low:
            return "These answers cite no sources."
        return "Nothing to count in these answers."
    if "fact sheet" in why:
        return f"Needs a list of verified facts about {B} to check answers against."
    return "No real answers loaded for these questions yet."


def review_note(r: dict, B: str) -> str:
    rv = r.get("review", "")
    if not rv:
        return ""
    if "names a tracked brand" in rv:
        return f"Changed to “{type_info(r['shape'], B)['name']}” because it names a tracked brand."
    if "names no tracked brand" in rv:
        return "The AI thought this named a competitor, but it's not one you track."
    m = re.search(r"word rules say (\w+)", rv)
    if m:
        return f"Hard to call: a simpler automatic check said “{type_info(m.group(1), B)['name']}”."
    if "unassigned" in rv:
        return "The AI skipped this one; sorted automatically."
    return rv


def warnings(plan: dict, B: str) -> list[str]:
    out = []
    for w in plan.get("warnings", []):
        if w.startswith("Mixed-shape"):
            continue  # shown inline as "based on X of Y questions"
        m = re.match(r"(\d+) of (\d+) prompts flagged", w)
        if m:
            out.append(f"{m.group(1)} of {m.group(2)} questions were hard to sort. They're marked ⚠ in each topic's question list and are worth a quick look.")
            continue
        if w.startswith("No sample answers"):
            out.append("No real AI answers have been loaded yet, so nothing could be checked. Every number below reads “can't measure yet”.")
            continue
        if w.startswith("Groups under 5"):
            out.append("Some topics have fewer than 5 questions. Numbers for them jump around a lot; consider merging them.")
            continue
        m = re.match(r"Headline reads 0 on the sample for: (.+?)\. ", w)
        if m:
            out.append(f"The main number reads 0 for: {m.group(1)}. That may be the finding itself, or a sign to pick a different main number.")
            continue
        if "no `cited` flag" in w:
            out.append("The sample doesn't say which links were actually cited, so source numbers will read high.")
            continue
        m = re.match(r"(\d+) of (\d+) prompts have no sample answers", w)
        if m:
            out.append(f"{m.group(1)} of {m.group(2)} questions had no answers in the sample, so some topics rest on fewer questions.")
            continue
        out.append(w)
    return out


# technical metric name (as in the spec), formula in words ({B} = brand label)
FORMULA = {
    "mention_rate":             ("Mention rate", "answers that name {B}", "all answers"),
    "position":                 ("Average position", "sum of {B}'s rank in each answer", "answers that name {B}"),
    "top_three_rate":           ("Top-three rate", "answers with {B} ranked 1–3", "answers that name {B}"),
    "win_rate":                 ("Win rate", "answers whose single winner is {B}", "answers that name {B} and pick one winner"),
    "capture":                  ("Capture", "answers that recommend {B}", "answers that recommend any specific brand or organization"),
    "tool_recommendation_rate": ("Recommendation rate", "answers that recommend a specific brand or organization", "all answers"),
    "cohort_sov":               ("Share of voice (vs. tracked competitors)", "mentions of {B}", "mentions of {B} + tracked competitors"),
    "negative_rate":            ("Negative rate", "answers negative or mixed about {B}", "answers that name {B}"),
    "fact_accuracy":            ("Wrong-claim rate", "claims about {B} that contradict the fact list", "claims that can be checked"),
    "owned_citation_share":     ("Owned citation share", "cited websites that are {B}'s", "all cited websites (each counted once per answer)"),
    "citation_split":           ("Citation split", "cited websites in each group", "all cited websites (each counted once per answer)"),
}


def calc(m: dict, B: str) -> dict:
    """Technical name, the formula in words, and the formula with the sample's numbers."""
    tech, top, bottom = FORMULA.get(m["id"], (m.get("label", m["id"]), "", ""))
    top, bottom = f(top, B), f(bottom, B)
    s = m["sample"]
    n, d = s["num"], s["den"]
    if m["id"] == "citation_split":
        worked = f"{_split(m.get('detail', ''), B)} of {d} cited websites" if d else "no cited websites in the sample"
    elif d == 0:
        worked = f"{n} ÷ 0: nothing to divide by in the sample"
    elif m["id"] == "position":
        worked = f"{n} ÷ {d} = {n / d:.1f}"
    else:
        worked = f"{n} ÷ {d} = {n * 100 / d:.0f}%"
    return {"tech": tech, "formula": f"{top} ÷ {bottom}", "worked": worked}
