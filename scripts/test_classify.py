"""Regression cases for fit_report.classify. Run: python3 scripts/test_classify.py"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fit_report import classify

B, C = ["acme"], ["rival"]
CASES = [
    # product finders with no list marker (the Versoflip miss)
    ("standing desks with reversible tops", "list"),
    ("desk controllers that lock voice commands", "list"),
    ("standing desks that weigh what is on them", "list"),
    # "Which ...?" questions
    ("Which standing desks accept voice commands?", "list"),
    ("Which standing desks support user profiles?", "list"),
    ("What is a reversible desk top, and which standing desks have one?", "list"),
    # superlative / tool-stack questions
    ("What is the most used SEO tool?", "list"),
    ("I run a 3-person agency — what tools should my stack include?", "list"),
    # concept-vs-concept is category, not list
    ("What is AEO vs SEO?", "category"),
    ("load sensing versus overload protection on a standing desk", "category"),
    # "top" as a noun is not "top 10"
    ("how much does a standing desk top weigh", "category"),
    # definitions / decisions / reasoning stay category
    ("what does duty cycle mean on a standing desk", "category"),
    ("is clap control on a desk a gimmick", "category"),
    ("why do smart desks use 2.4 GHz wifi instead of 5 GHz", "category"),
    ("Pros and cons of dynamic currency conversion", "category"),
    # tasks
    ("how to do keyword research", "task"),
    ("Why are webhooks retrying repeatedly?", "task"),
    ("Can I do SEO with AI?", "task"),
    # brand / competitor precedence
    ("acme vs rival", "branded"),
    ("best rival alternatives", "conquest"),
]

bad = [(q, want, classify(q, B, C)) for q, want in CASES if classify(q, B, C) != want]
for q, want, got in bad:
    print(f"FAIL  want {want:8} got {got:8} | {q}")
print(f"{len(CASES) - len(bad)}/{len(CASES)} passed")
sys.exit(1 if bad else 0)
