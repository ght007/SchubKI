"""Pre-check before a run: instant, free (no LLM).

Shows the expert what the enquiry already contains and what is vague or missing, so the
enquiry can be sharpened before Groq tokens are spent. The customer's words are never
changed: anything the expert adds becomes a separate, labelled answer.
"""
from __future__ import annotations

from ..schemas import Requirements
from . import coach as coach_mod
from . import extract as extract_mod
from . import glossary
from . import rules as rules_mod


def run(enquiry: str, answers: dict[str, str] | None = None) -> dict:
    answers = answers or {}
    hits = glossary.find(enquiry)
    terms, seen = [], set()
    for h in hits:
        if h["category"] == "vague" or h["term"] in seen:
            continue
        seen.add(h["term"])
        terms.append({k: h[k] for k in ("term", "matched", "category", "definition", "source")})

    vague, seen_v = [], set()
    for h in hits:
        if h["category"] == "vague" and h["term"] not in seen_v:
            seen_v.add(h["term"])
            vague.append({"term": h["term"], "matched": h["matched"], "ask": h["ask"], "why": h["definition"]})

    req: Requirements = extract_mod.heuristic(enquiry, answers)
    fired = rules_mod.evaluate(req, enquiry, answers)
    warnings = [{"rule_id": f.rule_id, "severity": f.severity, "title": f.title, "text": f.text,
                 "sources": [f"{s.source} p.{s.page}" for s in f.sources]}
                for f in fired if f.severity == "block" or f.status_hint]
    fields = coach_mod.fields(req, answers)
    missing = [{"name": f.name, "label": f.label, "impact": f.impact, "question": f.question}
               for f in fields if f.status == "unknown"]
    order = {"high": 0, "medium": 1, "low": 2}
    missing.sort(key=lambda m: order[m["impact"]])
    known = sum(1 for f in fields if f.status == "stated") + 0.5 * sum(1 for f in fields if f.status == "inferred")
    return {
        "terms": terms,
        "vague": vague,
        "warnings": warnings,
        "missing": missing,
        "completeness": int(round(known)),
        "total": len(fields),
        "words": len(enquiry.split()),
        "paths_detected": list(req.preferred_paths),   # paths the customer seems to ask for (keywords)
        "note": "Keyword pre-check (no AI). The full assessment reads the enquiry with the language model.",
    }