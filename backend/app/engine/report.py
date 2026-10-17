"""Stage 6: single-model report draft.

`draft()` asks one model for a Report. `rule_report()` builds a complete, sourced
report from the deterministic stages alone; it is used when the LLM is unavailable
and is honest about being a rule-only draft.
"""
from __future__ import annotations

from ..config import settings
from ..llm.client import complete_json
from ..schemas import (Citation, Evidence, FeasibilityPlan, MethodCoverage, MethodScore, Pathway, PremiseVerdict,
                       Question, Recommendation, Report, Requirements, RuleHit, Statement, TraceItem)
from .context import citations_for_rule, claims_by_page, fmt_evidence, fmt_matrix, fmt_requirements, fmt_rules

GEOMETRY = {"NIR": "NIR (diffuse reflection or transmission/transflection, chosen by sample optics)",
            "MIR": "MIR ATR (chalcogenide or polycrystalline IR fiber)",
            "RAMAN": "Raman (fiber probe; excitation wavelength to be selected)",
            "UVVIS": "UV/Vis (transmission, transflection or UV-ATR by optical density)",
            "FLUO": "Fluorescence (fluorimetric probe)"}
PROFILE_PAGES = {"NIR": ("S01", 10), "MIR": ("S01", 10), "RAMAN": ("S01", 11), "UVVIS": ("S01", 5), "FLUO": ("S01", 5)}


def build_user_prompt(enquiry: str, answers: dict, req: Requirements, hits: list[RuleHit], matrix: list[MethodScore],
                      coverage: list[MethodCoverage], premises: list[PremiseVerdict], evidence: list[Evidence]) -> str:
    prem = "\n".join(f"- {p.premise_id}: \"{p.statement}\" -> {p.verdict}: {p.explanation}" for p in premises) or "- none"
    ans = "\n".join(f"- {k}: {v}" for k, v in answers.items()) or "- none"
    hints = sorted({h.status_hint for h in hits if h.status_hint})
    return (f"ENQUIRY:\n{enquiry}\n\nCLIENT ANSWERS ADDED LATER:\n{ans}\n\n"
            f"REQUIREMENTS:\n{fmt_requirements(req)}\n\nPREMISE VERDICTS:\n{prem}\n\n"
            f"RULE FINDINGS:\n{fmt_rules(hits)}\nSTATUS HINTS: {hints or 'none'}\n\n"
            f"METHOD SCREENING:\n{fmt_matrix(matrix, coverage)}\n\nEVIDENCE PACK:\n{fmt_evidence(evidence)}")


def draft(model: str, stage: str, user_prompt: str, trace: list[TraceItem], fallback=None) -> Report | None:
    system = (settings.prompts_dir / "report.md").read_text(encoding="utf-8")
    return complete_json(stage, model, system, user_prompt, Report, trace, fallback=fallback,
                         max_tokens=3500, temperature=0.2)


# ------------------------------------------------------------------ rule-only report
def _claim_cite(source: str, page: int) -> list[Citation]:
    c = claims_by_page().get((source, page), [])
    return [Citation(source=c[0]["source"], page=c[0]["page"], quote=c[0]["quote"])] if c else []


def rule_report(enquiry: str, req: Requirements, hits: list[RuleHit], matrix: list[MethodScore],
                coverage: list[MethodCoverage], premises: list[PremiseVerdict]) -> Report:
    hints = [h.status_hint for h in hits if h.status_hint]
    status = "outside_supported_scope" if "outside_supported_scope" in hints else \
        "insufficient_information" if "insufficient_information" in hints else "provisional_assessment"
    blocks = [h for h in hits if h.severity == "block"]
    contradicted = [p for p in premises if p.verdict == "contradicted"]

    if blocks:
        headline = blocks[0].text
    elif contradicted:
        headline = f"The premise \"{contradicted[0].statement}\" is not supported: {contradicted[0].explanation}"
    else:
        leads = [m.name for m in matrix if m.verdict == "lead"]
        headline = (f"Provisional: {', '.join(leads)} worth testing first, to be confirmed in a multi-method lab trial."
                    if leads else "Several methods are possible; a multi-method comparison should decide.")
    headline += " (Rule-based draft: the language model was unavailable.)"

    recs: list[Recommendation] = []
    for m in matrix:
        if m.verdict in ("lead", "candidate") and status != "outside_supported_scope":
            rationale = []
            for c in m.contributions[:3]:
                h = next((x for x in hits if x.rule_id == c.rule_id), None)
                if h:
                    rationale.append(Statement(text=f"{h.title}.", kind="sourced", citations=citations_for_rule(h, 1)))
            src = PROFILE_PAGES[m.method_id]
            rationale.append(Statement(text=f"General method basis for {m.name}.", kind="sourced",
                                       citations=_claim_cite(*src)))
            recs.append(Recommendation(method=GEOMETRY[m.method_id], method_ids=[m.method_id],
                                       role="primary" if m.verdict == "lead" else "comparison",
                                       rationale=rationale, conditions="To be confirmed on representative samples."))
        elif m.verdict == "not_supported" or (m.requested_by_client and m.score < 0):
            h = next((x for x in hits if m.method_id in x.scores and x.scores[m.method_id] < 0), None)
            recs.append(Recommendation(method=GEOMETRY[m.method_id], method_ids=[m.method_id], role="not_recommended",
                                       rationale=[Statement(text=h.text if h else "Not supported by the screening.",
                                                            kind="sourced" if h else "proposal",
                                                            citations=citations_for_rule(h, 1) if h else [])]))

    questions = [Question(question=h.question.text, why=h.question.why or "Changes the method or setup.",
                          impact=h.question.impact) for h in hits if h.question]
    questions += [Question(question=f"{u.item}?", why=u.why_it_matters, impact=u.impact) for u in req.unknowns]
    order = {"high": 0, "medium": 1, "low": 2}
    seen, uniq = set(), []
    for q in sorted(questions, key=lambda q: order[q.impact]):
        if q.question.lower() not in seen:
            seen.add(q.question.lower())
            uniq.append(q)

    risks = [Statement(text=h.text, kind="sourced", citations=citations_for_rule(h, 1))
             for h in hits if h.severity in ("block", "warn") and h.text]
    cov_notes = [c.asset_check for c in coverage if c.asset_check]
    concept = [Statement(text=n, kind="sourced", citations=_claim_cite("S02", 6)) for n in cov_notes]
    concept.append(Statement(text="Probe geometry follows the sample optics: transmission/transflection for clear liquids, "
                                  "diffuse reflection for powders and opaque media, ATR for strongly absorbing or "
                                  "high optical density media.", kind="sourced", citations=_claim_cite("S01", 16)))
    ranges = []
    for m in matrix:
        if m.verdict in ("lead", "candidate"):
            ranges.append(Statement(text=f"{m.name}: nominal method range only; the usable range depends on the "
                                         f"selected instrument, fiber and probe.", kind="proposal"))
    plan_steps = [p for h in hits for p in h.plan]
    plan = FeasibilityPlan(
        samples=["Representative samples covering the client-agreed range and the physical variation of the process."],
        reference=["Independent reference values from the client's laboratory method for every sample."],
        comparison=["Compare the shortlisted methods and probe geometries on the same samples; single-method models "
                    "first, combinations only afterwards."],
        decision_basis=["Client-agreed error and bias on independent samples or runs."],
        steps=plan_steps[:6] or ["Run a multi-method lab trial on representative samples.",
                                 "Build and validate models on held-out material."])
    return Report(decision_status=status, headline=headline,
                  requirements_stated=[f.value for f in req.facts if f.status == "stated"][:8],
                  key_unknowns=[u.item for u in req.unknowns],
                  clarification_questions=uniq[:6], recommendations=recs, measurement_concept=concept,
                  spectral_range=ranges, risks=risks,
                  feasibility_plan=plan,
                  pathway=Pathway(next_step="Multi-method lab trial on representative client samples.",
                                  likely_path="undecided", why="Too early to choose before lab trials."),
                  assumptions=[])
