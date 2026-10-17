"""Quality scorecard + one auto-repair round.

Most checks are deterministic. Failures are sent back to the model once with the
exact problems; anything still failing is shown to the expert as a warning.
"""
from __future__ import annotations

import re

from ..config import settings
from ..llm.client import complete_json
from ..llm.models import model_for
from ..schemas import (Evidence, MethodCoverage, MethodScore, PremiseVerdict, Quality, QualityItem, Report, RuleHit,
                       TraceItem, Verification)
from .context import fmt_evidence, fmt_rules
from .verify import all_text

GUARANTEE = re.compile(r"\b(will work|guarantee[sd]?|proven (for|to)|ensures?|definitely|certainly|"
                       r"ready for (use|production|surgery|clinical)|100 ?%)\b", re.I)
NEGATED = re.compile(r"\b(not|no|cannot|never|without|nor)\b[^.]{0,40}$", re.I)
IMPACT_ORDER = {"high": 0, "medium": 1, "low": 2}


def _item(id_, cat, name, ok, detail="", warn=False) -> QualityItem:
    status = "pass" if ok else ("warn" if warn else "fail")
    return QualityItem(id=id_, category=cat, name=name, status=status, detail=detail if not ok else "")


def check(report: Report, ver: Verification, hits: list[RuleHit], matrix: list[MethodScore],
          coverage: list[MethodCoverage], premises: list[PremiseVerdict]) -> Quality:
    items: list[QualityItem] = []
    r = report
    # ---- structure
    empty = [n for n in ("requirements_stated", "key_unknowns", "clarification_questions", "risks")
             if not getattr(r, n)]
    if r.decision_status == "provisional_assessment" and not r.recommendations:
        empty.append("recommendations")
    items.append(_item("S1", "structure", "All required sections present", not empty, f"empty: {', '.join(empty)}"))
    qs = r.clarification_questions
    ordered = all(IMPACT_ORDER[a.impact] <= IMPACT_ORDER[b.impact] for a, b in zip(qs, qs[1:]))
    items.append(_item("S2", "structure", "3-6 questions, highest impact first", 3 <= len(qs) <= 8 and ordered,
                       f"{len(qs)} questions, ordered={ordered}", warn=True))
    fp = r.feasibility_plan
    missing = [n for n in ("samples", "reference", "comparison", "decision_basis") if not getattr(fp, n)]
    items.append(_item("S3", "structure", "Plan has samples, reference, comparison, decision basis", not missing,
                       f"missing: {', '.join(missing)}"))
    hints = {h.status_hint for h in hits if h.status_hint}
    want = "outside_supported_scope" if "outside_supported_scope" in hints else \
        "insufficient_information" if "insufficient_information" in hints else None
    if want is None and r.decision_status == "outside_supported_scope":
        items.append(_item("S4", "structure", "Decision status consistent with rule findings", False,
                           "no rule finding supports 'outside_supported_scope'; a contradicted premise is a "
                           "provisional assessment with a plain 'cannot be approved' headline"))
    else:
        items.append(_item("S4", "structure", "Decision status consistent with rule findings",
                           want is None or r.decision_status == want, f"rules require '{want}', report says '{r.decision_status}'"))

    # ---- grounding
    ratio = ver.n_verified / ver.n_sourced if ver.n_sourced else 1.0
    bad = [c.location for c in ver.claims if c.status in ("unverified", "no_citation")]
    items.append(_item("G1", "grounding", "Sourced claims verified on the cited page", ratio >= 0.9 and not bad,
                       f"{ver.n_verified}/{ver.n_sourced} verified; problems at {', '.join(bad[:5])}",
                       warn=ratio >= 0.7))
    items.append(_item("G2", "grounding", "No unsupported numbers", ver.n_unsupported_numbers == 0,
                       "; ".join(f"{n.number} at {n.location}" for n in ver.numbers if n.status == "unsupported")[:300]))
    items.append(_item("G3", "grounding", "No invented client facts", ver.n_bad_client_facts == 0,
                       "; ".join(c.text[:80] for c in ver.client_facts if c.status != "verified")[:300]))
    scope = [c for c in ver.claims if c.status == "scope_warning"]
    items.append(_item("G4", "grounding", "Evidence used within its scope", not scope,
                       "; ".join(c.detail for c in scope)[:300]))
    unsupported_recs = [x.method for x in r.recommendations
                        if x.role != "not_recommended" and not any(s.kind == "sourced" and s.citations for s in x.rationale)]
    items.append(_item("G5", "grounding", "Each recommendation has a sourced reason", not unsupported_recs,
                       f"no sourced rationale: {', '.join(unsupported_recs)}"))

    # ---- honesty
    guar = []
    for loc, text in all_text(r):
        for m in GUARANTEE.finditer(text):
            if not NEGATED.search(text[:m.start()]):
                guar.append(f"'{m.group(0)}' at {loc}")
    items.append(_item("H1", "honesty", "No guarantee or readiness wording", not guar, "; ".join(guar[:4])))
    raman_bad = [loc for loc, t in all_text(r) if re.search(r"raman", t, re.I) and re.search(r"\bshift\b[^.]{0,30}\bnm\b", t, re.I)]
    items.append(_item("H2", "honesty", "Units: Raman shift in cm-1, excitation in nm", not raman_bad,
                       f"Raman shift given in nm at {', '.join(raman_bad)}", warn=True))
    silica_asset = any(c.asset_check for c in coverage if c.method_id == "MIR")
    mir_recommended = any("MIR" in x.method_ids and x.role != "not_recommended" for x in r.recommendations)
    text_all = " ".join(t for _, t in all_text(r)).lower()
    fiber_ok = not (silica_asset and mir_recommended) or any(
        w in text_all for w in ("chalcogenide", "polycrystalline", "cir", "pir"))
    items.append(_item("H3", "honesty", "Fiber choice consistent with spectral coverage", fiber_ok,
                       "MIR recommended for a client with a silica link but no IR fiber (CIR/PIR) named"))
    contradicted = [p for p in premises if p.verdict == "contradicted"]
    ack = not contradicted or any(w in r.headline.lower() for w in
                                  ("not", "cannot", "no ", "does not", "unsupported", "outside", "insufficient"))
    items.append(_item("H4", "honesty", "Contradicted premises are stated plainly in the headline", ack,
                       "headline does not address a contradicted premise", warn=True))

    # ---- usefulness
    requested_weak = [m.method_id for m in matrix if m.requested_by_client and m.verdict in ("not_supported", "weak")]
    covered = {mid for x in r.recommendations for mid in x.method_ids}
    why_not = all(mid in covered for mid in requested_weak)
    items.append(_item("U1", "usefulness", "Client-requested weak methods are addressed (why / why not)", why_not,
                       f"not addressed: {', '.join(m for m in requested_weak if m not in covered)}", warn=True))
    steps_ok = len(fp.steps) >= 3 or (len(fp.samples) + len(fp.comparison) >= 3)
    items.append(_item("U2", "usefulness", "Feasibility plan is concrete", steps_ok, "fewer than 3 concrete steps", warn=True))
    high_q = [h.question.text for h in hits if h.question and h.question.impact == "high"]
    q_words = " ".join(q.question.lower() for q in qs)
    hit_q = sum(1 for t in high_q if len(set(re.findall(r"[a-z]{5,}", t.lower())) & set(re.findall(r"[a-z]{5,}", q_words))) >= 2)
    items.append(_item("U3", "usefulness", "Questions cover the high-impact unknowns",
                       not high_q or hit_q >= min(2, len(high_q)), f"{hit_q}/{len(high_q)} high-impact rule questions covered",
                       warn=True))

    passed = sum(1 for i in items if i.status == "pass")
    return Quality(items=items, passed=passed, total=len(items))


def failures_text(q: Quality, ver: Verification) -> str:
    lines = [f"- [{i.id}] {i.name}: {i.detail}" for i in q.items if i.status == "fail"]
    for c in ver.claims:
        if c.status in ("unverified", "no_citation", "scope_warning"):
            lines.append(f"- {c.location}: \"{c.text[:120]}\" -> {c.status}: {c.detail}")
    for n in ver.numbers:
        if n.status == "unsupported":
            lines.append(f"- number '{n.number}' at {n.location} is not supported")
    return "\n".join(lines)


def needs_repair(q: Quality) -> bool:
    return any(i.status == "fail" for i in q.items)


def repair(report: Report, q: Quality, ver: Verification, hits: list[RuleHit], evidence: list[Evidence],
           trace: list[TraceItem]) -> Report | None:
    system = (settings.prompts_dir / "repair.md").read_text(encoding="utf-8")
    # Keep the repair request small (free tier): only the evidence the report cites or that
    # blocking/warning rules rely on, and only rules that carry a status or a block.
    cited = {(cit.source, cit.page) for claim in ver.claims for cit in claim.citations}
    cited |= {(s.source, s.page) for h in hits if h.severity in ("block", "warn") for s in h.sources}
    pack = [e for e in evidence if (e.source, e.page) in cited][:8] or evidence[:5]
    key_rules = [h for h in hits if h.severity in ("block", "warn") or h.status_hint]
    hints = sorted({h.status_hint for h in hits if h.status_hint})
    user = (f"PROBLEMS FOUND:\n{failures_text(q, ver)}\n\nRULE FINDINGS:\n{fmt_rules(key_rules)}\n"
            f"STATUS HINTS: {hints or 'none'}\n\nEVIDENCE PACK:\n{fmt_evidence(pack)}\n\n"
            f"REPORT TO FIX:\n{report.model_dump_json(exclude_none=True)}")
    return complete_json("repair", model_for("repair"), system, user, Report, trace, fallback=None,
                         max_tokens=3500, temperature=0.0)