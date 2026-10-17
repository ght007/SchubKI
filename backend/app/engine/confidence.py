"""Computed confidence level + breakdown + caps.

Confidence is never asked from the LLM. It is the minimum of observable signals,
then capped by rules (e.g. target undefined -> insufficient) and lowered by weak
verification or council disagreement. Every signal is shown in the UI.
"""
from __future__ import annotations

from ..schemas import (Coach, Confidence, Council, MethodConfidence, MethodScore, PremiseVerdict, Report, Requirements,
                       RuleHit, Signal, Verification)

LEVELS = ["insufficient", "low", "medium", "high"]
APPLICATION_RULES = {"R_DAIRY", "R_PHARMA_BLEND", "R_WATER_IN_HYDROCARBON", "R_HOT_MELT_API", "R_MOISTURE",
                     "R_BIOPROCESS", "R_HETEROGENEOUS", "R_GLUCOSE_NOT_FLUORESCENT_TARGET"}


def _lv(i: int) -> str:
    return LEVELS[max(0, min(3, i))]


def _ix(level: str) -> int:
    return LEVELS.index(level)


def compute(req: Requirements, hits: list[RuleHit], matrix: list[MethodScore], premises: list[PremiseVerdict],
            ver: Verification | None, coach: Coach, council: Council | None, report: Report | None) -> Confidence:
    signals: list[Signal] = []

    ratio = coach.completeness / max(1, coach.total)
    info = 3 if ratio >= 0.6 else 2 if ratio >= 0.35 else 1 if ratio >= 0.15 else 0
    if req.target_defined == "no":
        info = 0
    signals.append(Signal(name="Information", level=_lv(info), value=round(ratio, 2),
                          detail=f"{coach.completeness}/{coach.total} decision-relevant facts known; target defined: {req.target_defined}"))

    app_hits = [h.rule_id for h in hits if h.rule_id in APPLICATION_RULES]
    leads = [m for m in matrix if m.verdict == "lead"]
    ev = 3 if app_hits and leads else 2 if leads else 1 if any(m.verdict == "candidate" for m in matrix) else 0
    signals.append(Signal(name="Evidence", level=_lv(ev), value=ev / 3,
                          detail=("Direct application in AFS sources: " + ", ".join(app_hits)) if app_hits else
                          "Only general method knowledge applies; no direct application example in the sources"))

    scope = 3
    detail = "Requested use matches the scope of the cited evidence"
    if any(h.rule_id == "R_CLINICAL_SCOPE" for h in hits):
        scope, detail = 0, "Requested use (clinical/in vivo) exceeds the in-vitro / lab scope of the evidence"
    elif req.process_context in ("production",):
        scope, detail = 2, "Sources show lab or application examples; production performance is unconfirmed"
    signals.append(Signal(name="Scope fit", level=_lv(scope), value=scope / 3, detail=detail))

    contra = [p for p in premises if p.verdict == "contradicted"]
    unver = [p for p in premises if p.verdict == "unverifiable"]
    prem = 1 if contra else 2 if unver else 3
    signals.append(Signal(name="Client premises", level=_lv(prem), value=prem / 3,
                          detail=f"{len(contra)} contradicted, {len(unver)} unverifiable, "
                                 f"{len(premises) - len(contra) - len(unver)} supported"))

    if ver and ver.n_sourced:
        vr = ver.n_verified / ver.n_sourced
        vlev = 3 if vr >= 0.9 else 2 if vr >= 0.7 else 1
        signals.append(Signal(name="Verification", level=_lv(vlev), value=round(vr, 2),
                              detail=f"{ver.n_verified}/{ver.n_sourced} sourced claims verified; "
                                     f"{ver.n_unsupported_numbers} unsupported numbers"))
    if council and council.drafts:
        ag = council.agreement
        alev = 3 if ag >= 0.99 else 2 if ag >= 0.6 else 1
        signals.append(Signal(name="Model agreement", level=_lv(alev), value=round(ag, 2),
                              detail=council.agreement_detail + (f" ({council.families} model families)" if council.families else "")))

    overall = min(info, ev, scope)
    caps = []
    for h in hits:
        if h.cap_confidence and _ix(h.cap_confidence) < overall:
            overall = _ix(h.cap_confidence)
            caps.append(f"{h.rule_id}: capped at {h.cap_confidence}")
        elif h.cap_confidence:
            caps.append(f"{h.rule_id}: cap {h.cap_confidence}")
    if any(s.name == "Verification" and s.level in ("low", "insufficient") for s in signals) and overall > 0:
        overall -= 1
        caps.append("Weak verification: lowered one level")
    if any(s.name == "Model agreement" and s.level == "low" for s in signals) and overall > 0:
        overall -= 1
        caps.append("Council disagreement: lowered one level")
    if report and report.decision_status == "insufficient_information":
        overall = 0
    elif report and report.decision_status == "outside_supported_scope":
        overall = min(overall, 0)

    per_method = []
    for m in matrix:
        lvl = overall if m.verdict == "lead" else overall - 1 if m.verdict == "candidate" else 0
        per_method.append(MethodConfidence(method_id=m.method_id, level=_lv(lvl),
                                           detail=f"{m.verdict}, screening score {m.score}"))
    raise_with = [f.question for f in coach.fields if f.status == "unknown" and f.impact == "high" and f.question][:3]
    return Confidence(level=_lv(overall), signals=signals, caps=caps, per_method=per_method, raise_with=raise_with)
