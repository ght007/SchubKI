"""AFS pathway (S02 p.20): suggested path and fit of the paths the expert or client asked for.

Deterministic, like the method matrix: every verdict comes from a sourced rule's path hint.
  suggested = the path with the most 'supports' hints, unless a rule sets a status
              (insufficient information / outside scope) or the top paths tie -> 'undecided'.
  fit       = premature > conflicts > fits > open (no rule decides it; the lab trial does).
'Proceed anyway' plans are sourced templates, written for requested paths that are
premature or conflicting, so the expert can still see what that route would take.
"""
from __future__ import annotations

from collections import defaultdict

from ..schemas import PathAnalysis, PathFit, PathHint, ProceedPlan, Requirements, RuleHit, SourceRef

PATH_NAMES = {"A": "chemometric model for process automation", "B": "customised multi-spectral system for R&D",
              "C": "customised spectral IoT sensor"}
PATH_TITLES = {"A": "Chemometric model for process automation", "B": "Multi-spectral system for your R&D lab",
               "C": "Low-cost spectral sensor(s)"}

# Extra questions asked when a path is chosen (before the run; all optional).
# An option may carry a sourced effect on that path's verdict; the others are context for the report.
# Answers travel as "Path X - <label>": "<option>[; note]" so they are visible in the run and the export.
PATH_QUESTIONS: dict[str, list[dict]] = {
    "A": [
        {"id": "a_ref", "label": "Reference values",
         "text": "Can you provide samples with independent lab reference values across the normal operating range?",
         "options": {"Yes": None, "Some": None,
                     "No": ("premature", "A chemometric model is built and validated on samples with reference values; "
                                         "without them it cannot be calibrated.", [("S01", 5)])}},
        {"id": "a_analyzer", "label": "Process analyzer",
         "text": "Is a process analyzer already installed or planned at the measuring point?",
         "options": {"Installed": None, "Planned": None, "None yet": None}},
        {"id": "a_use", "label": "Use in the process",
         "text": "What should the measured value do in the process?",
         "options": {"Monitor a trend": None, "Alarm on limits": None, "Closed-loop control": None}},
    ],
    "B": [
        {"id": "b_where", "label": "Where it is used",
         "text": "Where will the system be used?",
         "options": {"Our R&D lab": ("supports", "Path B gives a tailored set of spectrometers for R&D in the customer's own lab.",
                                     [("S02", 20)]),
                     "In production": ("conflicts", "Path B is a lab system for R&D; measuring in production is Path A "
                                                    "(central analyzer) or Path C (sensors).", [("S02", 20)]),
                     "Both": None}},
        {"id": "b_staff", "label": "Staff for spectroscopy",
         "text": "Do you have staff who can run spectrometers and build models?",
         "options": {"Yes": None, "Partly": None, "No": None}},
        {"id": "b_methods", "label": "Methods already in the lab",
         "text": "Which spectroscopy methods do you already have in the lab?",
         "options": {"None": None, "One": None, "Several": None}},
    ],
    "C": [
        {"id": "c_points", "label": "Measuring points",
         "text": "How many measuring points need a sensor?",
         "options": {"1-2": None,
                     "3-10": ("supports", "Sensors at the measuring points give lower installation cost than a central "
                                          "analyzer with long fibers.", [("S02", 18)]),
                     "More than 10": ("supports", "Sensors at the measuring points give lower installation cost than a "
                                                  "central analyzer with long fibers.", [("S02", 18)])}},
        {"id": "c_bands", "label": "Key wavelengths known",
         "text": "Has a lab trial with full-spectrum instruments already shown which wavelengths matter?",
         "options": {"Yes": None,
                     "No": ("premature", "A dedicated LED / multisensor analyzer starts with in-depth laboratory spectrometer "
                                         "studies to choose the optimal spectral ranges.", [("S01", 9)]),
                     "Not sure": ("premature", "A dedicated LED / multisensor analyzer starts with in-depth laboratory "
                                               "spectrometer studies to choose the optimal spectral ranges.", [("S01", 9)])}},
        {"id": "c_vars", "label": "Variables per sensor",
         "text": "How many variables must one sensor measure?",
         "options": {"One": None, "Two or three": None,
                     "Many": ("conflicts", "Several variables at once need full-spectrum information; a few-wavelength sensor "
                                           "is designed for one specific control task.", [("S02", 18)])}},
    ],
}


QUESTION_IMPACT = {"a_ref": "high", "b_where": "high", "c_bands": "high", "c_vars": "medium", "c_points": "medium",
                   "a_analyzer": "medium", "a_use": "low", "b_staff": "low", "b_methods": "low"}
# a path question that covers a general missing fact: ask it once, in its one-click form
COVERS_FIELD = {"a_ref": "reference", "c_points": "points"}


def prefill(qid: str, req: Requirements) -> str:
    """Answer a path question from what the enquiry already says (shown as 'from your text'; the user can change it)."""
    if qid == "a_ref" and req.reference_method == "yes":
        return "Yes"
    if qid == "a_analyzer" and any("analy" in a.lower() for a in req.existing_assets):
        return "Installed"
    if qid == "b_where":
        return {"lab_research": "Our R&D lab", "production": "In production", "pilot": "In production"}.get(req.process_context, "")
    if qid == "c_points":
        import re
        m = re.search(r"\d+", req.measurement_points or "")
        if m:
            n = int(m.group())
            return "1-2" if n <= 2 else "3-10" if n <= 10 else "More than 10"
    if qid == "c_vars" and req.target_defined == "yes" and req.target_variables:
        n = len(req.target_variables)
        return "One" if n == 1 else "Two or three" if n <= 3 else "Many"
    return ""


def answer_key(path: str, label: str) -> str:
    return f"Path {path} - {label}"


def is_path_answer(key: str) -> bool:
    return key.startswith("Path ") and " - " in key


def general_answers(answers: dict[str, str] | None) -> dict[str, str]:
    """Answers without the path questions (those are handled here, not by the keyword heuristics)."""
    return {k: v for k, v in (answers or {}).items() if not is_path_answer(k)}


def questions_public() -> dict:
    """For the UI: full path names and the questions (options without their internal effects)."""
    return {p: {"title": PATH_TITLES[p], "name": PATH_NAMES[p],
                "questions": [{"id": q["id"], "label": q["label"], "text": q["text"], "options": list(q["options"]),
                               "key": answer_key(p, q["label"])} for q in qs],
                "note_key": answer_key(p, "Note")}
            for p, qs in PATH_QUESTIONS.items()}


def answer_hits(answers: dict[str, str] | None) -> list[RuleHit]:
    """Turn path answers with a sourced effect into rule-like hits (shown in the path analysis and rule list)."""
    out = []
    for p, qs in PATH_QUESTIONS.items():
        for q in qs:
            value = (answers or {}).get(answer_key(p, q["label"]), "")
            choice = value.split(";")[0].strip()
            effect = q["options"].get(choice)
            if not effect:
                continue
            kind, reason, srcs = effect
            out.append(RuleHit(rule_id=f"ANSWER_{q['id'].upper()}", title=f"Answer: {q['label']} = {choice}",
                               severity="info", text=reason,
                               paths=[PathHint(path=p, effect=kind, reason=reason)],
                               sources=[SourceRef(source=s, page=pg) for s, pg in srcs]))
    return out

PLANS = {
    "A": ([
        "Collect representative samples across the client-agreed range, each with an independent reference value.",
        "Record full spectra with the short-listed method(s) and build a calibration model; validate it on held-out batches or runs.",
        "Agree how the model is maintained (recalibration triggers, matrix changes) before it is used for process control.",
    ], [SourceRef(source="S01", page=5), SourceRef(source="S02", page=20)]),
    "B": ([
        "Specify the lab kit from the methods short-listed in this assessment: spectrometers, fiber probes, software.",
        "Run the method comparison on the customer's own samples in their lab.",
        "Use the results as the basis for a later process solution (Path A or C).",
    ], [SourceRef(source="S02", page=20), SourceRef(source="S01", page=4)]),
    "C": ([
        "Run a lab trial with full-spectrum instruments on representative samples.",
        "Select the most informative wavelengths and check that a few-band model reaches the client-agreed error on independent samples.",
        "Build and test a prototype LED / filter sensor against the reference method before any volume order.",
    ], [SourceRef(source="S01", page=9), SourceRef(source="S03", page=14), SourceRef(source="S02", page=18)]),
}


def analyse(hits: list[RuleHit], req: Requirements, expert_paths: list[str],
            answers: dict[str, str] | None = None) -> PathAnalysis:
    # answers to the path questions count like rule hits, and come first: they are the customer's own facts
    hits = answer_hits(answers) + list(hits)
    support: dict[str, list[RuleHit]] = defaultdict(list)
    against: dict[str, list[tuple[str, RuleHit, str]]] = defaultdict(list)   # path -> (effect, rule, reason)
    reasons: dict[tuple[str, str], str] = {}
    for h in hits:
        for ph in h.paths:
            reasons[(h.rule_id, ph.path)] = ph.reason
            if ph.effect == "supports":
                support[ph.path].append(h)
            else:
                against[ph.path].append((ph.effect, h, ph.reason))

    # suggested path
    out = PathAnalysis()
    blocked_status = any(h.status_hint for h in hits)
    ranked = sorted(((len(v), p) for p, v in support.items() if not against.get(p)), reverse=True)
    if not blocked_status and ranked and (len(ranked) == 1 or ranked[0][0] > ranked[1][0]):
        best = ranked[0][1]
        out.suggested = best
        out.reasons = [reasons[(h.rule_id, best)] for h in support[best]]
        out.sources = [s for h in support[best] for s in h.sources][:4]
    else:
        out.reasons = ["The rule findings do not single out one path; the lab trial decides."
                       if not blocked_status else "Too early: the target or the scope must be settled first."]

    # requested paths (expert in the UI and/or detected in the enquiry)
    by: dict[str, str] = {}
    for p in expert_paths:
        by[p] = "expert"
    for p in req.preferred_paths:
        by[p] = "both" if p in by else "enquiry"
    for path in sorted(by):
        neg = against.get(path, [])
        prem = [x for x in neg if x[0] == "premature"]
        conf = [x for x in neg if x[0] == "conflicts"]
        if prem:
            _, h, why = prem[0]
            fit = PathFit(path=path, requested_by=by[path], verdict="premature", reason=why, sources=h.sources[:2])
        elif conf:
            _, h, why = conf[0]
            fit = PathFit(path=path, requested_by=by[path], verdict="conflicts", reason=why, sources=h.sources[:2])
        elif support.get(path):
            h = support[path][0]
            fit = PathFit(path=path, requested_by=by[path], verdict="fits", reason=reasons[(h.rule_id, path)],
                          sources=h.sources[:2])
        else:
            fit = PathFit(path=path, requested_by=by[path], verdict="open",
                          reason="No finding speaks for or against this path yet; the lab trial decides.",
                          sources=[SourceRef(source="S02", page=20)])
        out.requested.append(fit)
        if fit.verdict in ("premature", "conflicts"):
            steps, srcs = PLANS[path]
            out.proceed_anyway.append(ProceedPlan(
                path=path, caveat=f"Path {path} ({PATH_NAMES[path]}) is "
                                  f"{'premature' if fit.verdict == 'premature' else 'a poor fit'} here: {fit.reason}",
                steps=steps, sources=srcs))
    return out


def prompt_block(analysis: PathAnalysis) -> str:
    """Compact text for the report prompt."""
    lines = [f"Suggested path: {analysis.suggested} ({'; '.join(analysis.reasons)})"]
    for f in analysis.requested:
        lines.append(f"Requested Path {f.path} (by {f.requested_by}): {f.verdict} - {f.reason}")
    return "\n".join(lines)