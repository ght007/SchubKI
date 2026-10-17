"""Step 1 of a UI run: "Is this what you mean?"

Reads the enquiry with the extraction model (the run's own first stage, so the reply is cached and
reused when the user confirms) and returns:
  readings   - the structured requirements that drive the rules, each one can be rejected (-> unknown)
  terms      - glossary translations (e.g. Restfeuchte -> moisture)
  paths      - chosen + detected AFS paths
  warnings   - blocking rules that already fire
  questions  - ONE de-duplicated list: vague words, missing key facts, and the questions of every chosen or
               detected path; answers the text already gives are pre-filled ("from your text")
The customer's text is never rewritten. Nothing here is case-specific.
"""
from __future__ import annotations

from ..schemas import Requirements, TraceItem
from . import coach as coach_mod
from . import extract as extract_mod
from . import glossary
from . import paths as paths_mod
from . import rules as rules_mod

LABELS = {
    "target_variables": "What to measure", "matrix": "Sample", "phase": "Sample form", "optical_behavior": "Optics",
    "aqueous": "Water-based", "fluorescent_target": "Target fluoresces", "heterogeneous": "Heterogeneous",
    "temperature": "Temperature", "fouling_risk": "Fouling risk", "process_context": "Setting",
    "analyzer_remote": "Analyzer far from the probe", "existing_assets": "Equipment they already have",
    "requested_methods": "Methods they ask for", "reference_method": "Reference method available",
    "concentration_level": "Concentration level", "measurement_points": "Measuring points",
    "preferred_paths": "AFS path they ask for",
}
UNKNOWN = (None, "", "unknown", [])
IMPACT_ORDER = {"high": 0, "medium": 1, "low": 2}


def _fmt(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value).replace("_", " ")


def readings(req: Requirements) -> list[dict]:
    out = []
    if req.target_defined == "no":
        out.append({"field": "target_defined", "label": "What to measure", "value": "not defined yet"})
    for name, label in LABELS.items():
        value = getattr(req, name)
        if value in UNKNOWN or (name == "matrix" and value == req.phase):
            continue
        if name == "preferred_paths":
            value = [f"{p} · {paths_mod.PATH_TITLES[p]}" for p in value]
        out.append({"field": name, "label": label, "value": _fmt(value)})
    return out


def questions(req: Requirements, enquiry: str, answers: dict[str, str], shown_paths: list[str]) -> list[dict]:
    qs: list[dict] = []
    covered = set()
    for p in shown_paths:
        for q in paths_mod.PATH_QUESTIONS[p]:
            covered.add(paths_mod.COVERS_FIELD.get(q["id"]))
            pre = paths_mod.prefill(q["id"], req)
            qs.append({"key": paths_mod.answer_key(p, q["label"]), "text": q["text"], "kind": "choice",
                       "options": list(q["options"]), "path": p, "impact": paths_mod.QUESTION_IMPACT.get(q["id"], "medium"),
                       "prefill": pre, "why": f"For Path {p}: {paths_mod.PATH_TITLES[p]}"})
    for f in coach_mod.fields(req, answers):
        if f.status == "unknown" and f.name not in covered:
            qs.append({"key": f.label, "text": f.question, "kind": "text", "impact": f.impact, "prefill": "",
                       "why": f"Missing key fact: {f.label}"})
    seen = set()
    for h in glossary.find(enquiry):
        if h["category"] == "vague" and h["term"] not in seen:
            seen.add(h["term"])
            qs.append({"key": h["ask"], "text": h["ask"], "kind": "text", "impact": "medium", "prefill": "",
                       "why": f'"{h["matched"]}" is too vague to act on. {h["definition"]}'})
    qs.sort(key=lambda q: IMPACT_ORDER[q["impact"]])
    return qs


def run(enquiry: str, answers: dict[str, str] | None = None, preferred_paths: list[str] | None = None) -> dict:
    answers = answers or {}
    trace: list[TraceItem] = []
    req = extract_mod.extract(enquiry, answers, trace)
    hits = rules_mod.evaluate(req, enquiry, answers)
    chosen = sorted(set(preferred_paths or []))
    detected = sorted(set(req.preferred_paths) - set(chosen))
    terms, seen = [], set()
    for h in glossary.find(enquiry):
        if h["category"] != "vague" and h["term"] not in seen and h["matched"].lower() != h["term"].lower():
            seen.add(h["term"])
            terms.append({"matched": h["matched"], "term": h["term"]})
    fields = coach_mod.fields(req, answers)
    known = sum(1 for f in fields if f.status == "stated") + 0.5 * sum(1 for f in fields if f.status == "inferred")
    t = trace[0] if trace else None
    by = "keyword fallback (AI unavailable)" if not t or not t.ok or t.model.startswith("mock") else \
        f"{t.model}{' (cached)' if t.cached else ''}"
    return {
        "summary": req.summary,
        "read_by": by,
        "readings": readings(req),
        "facts": [{"field": f.field, "value": f.value, "status": f.status, "quote": f.quote} for f in req.facts],
        "premises": [p.statement for p in req.premises],
        "terms": terms,
        "paths": {"chosen": chosen, "detected": detected, "titles": paths_mod.PATH_TITLES},
        "warnings": [{"rule_id": h.rule_id, "title": h.title, "text": h.text,
                      "sources": [f"{s.source} p.{s.page}" for s in h.sources]}
                     for h in hits if h.severity == "block" or h.status_hint],
        "questions": questions(req, enquiry, answers, sorted(set(chosen) | set(detected))),
        "completeness": int(round(known)),
        "total": len(fields),
    }
