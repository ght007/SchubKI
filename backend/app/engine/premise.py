"""Stage 4: premise check (rules + LLM).

The LLM judges each client premise against the evidence pack and the fired rules.
Fallback: map premise kinds to fired block/warn rules deterministically.
"""
from __future__ import annotations

from ..config import settings
from ..llm.client import complete_json
from ..llm.models import model_for
from ..schemas import Evidence, PremiseCheckOut, PremiseVerdict, Requirements, RuleHit, TraceItem
from .context import citations_for_rule, fmt_evidence, fmt_rules

KIND_RULES = {
    "reuse_claim": ["R_FIBER_SILICA_MIR", "R_CALIBRATION_MATRIX", "R_ADD_METHOD_NOT_A_FIX", "R_REMOTE_MIR_LINK"],
    "evidence_claim": ["R_CLINICAL_SCOPE", "R_EVIDENCE_AS_PROOF"],
    "certainty_request": ["R_TARGET_UNDEFINED", "R_CERTAINTY_DEMAND", "R_FIBER_SILICA_MIR", "R_CLINICAL_SCOPE"],
    "method_claim": ["R_FLUO_NEEDS_TARGET", "R_OD_NOT_VIABILITY", "R_ADD_METHOD_NOT_A_FIX"],
}


def fallback(req: Requirements, hits: list[RuleHit]) -> PremiseCheckOut:
    by_id = {h.rule_id: h for h in hits}
    out = []
    for p in req.premises:
        related = [by_id[r] for r in KIND_RULES.get(p.kind, []) if r in by_id]
        if related:
            h = related[0]
            verdict = "contradicted" if h.severity == "block" else "unverifiable"
            out.append(PremiseVerdict(premise_id=p.id, statement=p.statement, verdict=verdict,
                                      explanation=h.text, citations=citations_for_rule(h)))
        else:
            out.append(PremiseVerdict(premise_id=p.id, statement=p.statement, verdict="unverifiable",
                                      explanation="The supplied material does not settle this; it needs to be tested.",
                                      citations=[]))
    return PremiseCheckOut(verdicts=out)


def check(enquiry: str, req: Requirements, hits: list[RuleHit], evidence: list[Evidence],
          trace: list[TraceItem]) -> list[PremiseVerdict]:
    if not req.premises:
        return []
    premises = "\n".join(f"- {p.id} ({p.kind}): {p.statement}" for p in req.premises)
    user = (f"ENQUIRY:\n{enquiry}\n\nCLIENT PREMISES:\n{premises}\n\nRULE FINDINGS:\n{fmt_rules(hits)}\n\n"
            f"EVIDENCE PACK:\n{fmt_evidence(evidence)}")
    prompt = (settings.prompts_dir / "premise.md").read_text(encoding="utf-8")
    out = complete_json("premise", model_for("premise"), prompt, user, PremiseCheckOut, trace,
                        fallback=lambda: fallback(req, hits), max_tokens=1500, temperature=0.0)
    verdicts = out.verdicts if out else []
    stated = {p.id: p.statement for p in req.premises}
    for v in verdicts:  # keep the client's exact wording
        v.statement = stated.get(v.premise_id, v.statement)
    return verdicts
