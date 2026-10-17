"""Report JSON -> Markdown (outputs/ and export)."""
from __future__ import annotations

from ..schemas import RunResult, Statement

KIND_TAG = {"client_fact": "client fact", "sourced": "sourced", "assumption": "assumption", "proposal": "proposal"}
STATUS = {"provisional_assessment": "Provisional assessment", "insufficient_information": "Insufficient information",
          "outside_supported_scope": "Outside the supported scope"}


def _cite(s: Statement) -> str:
    if not s.citations:
        return ""
    return " " + " ".join(f"[{c.source} p.{c.page}]" for c in s.citations)


def _stmt(s: Statement) -> str:
    return f"- {s.text}{_cite(s)} _({KIND_TAG.get(s.kind, s.kind)})_"


def render(run: RunResult, title: str = "") -> str:
    r = run.report
    if r is None:
        return f"# {title or 'Assessment'}\n\nNo report produced. {run.error}\n"
    L: list[str] = []
    L.append(f"# {title or 'First technical assessment'}")
    L.append("")
    L.append(f"> **Enquiry:** {run.enquiry}")
    if run.answers:
        L.append(">")
        L.append("> **Answers added:** " + "; ".join(f"{k}: {v}" for k, v in run.answers.items()))
    L.append("")
    conf = run.confidence.level if run.confidence else "n/a"
    q = f"{run.quality.passed}/{run.quality.total}" if run.quality else "n/a"
    v = run.verification
    ver = f"{v.n_verified}/{v.n_sourced}" if v else "n/a"
    L.append(f"**Decision status:** {STATUS[r.decision_status]} · **Confidence:** {conf} · "
             f"**Quality checks:** {q} · **Sourced claims verified:** {ver} · "
             f"**Unsupported numbers:** {v.n_unsupported_numbers if v else 'n/a'}")
    L.append("")
    L.append(f"**Answer:** {r.headline}")
    L.append("")

    if run.premises:
        L.append("## Premise check")
        for p in run.premises:
            cites = " ".join(f"[{c.source} p.{c.page}]" for c in p.citations)
            L.append(f"- **{p.verdict.replace('_', ' ')}**: \"{p.statement}\". {p.explanation} {cites}".rstrip())
        L.append("")

    L.append("## Requirements")
    L.append("**Stated by the client**")
    L += [f"- {x}" for x in r.requirements_stated] or ["- (none)"]
    L.append("")
    L.append("**Key unknowns**")
    L += [f"- {x}" for x in r.key_unknowns] or ["- (none)"]
    if r.assumptions:
        L.append("")
        L.append("**Assumptions made**")
        L += [f"- {x}" for x in r.assumptions]
    L.append("")

    L.append("## Clarification questions (highest impact first)")
    for i, qq in enumerate(r.clarification_questions, 1):
        L.append(f"{i}. **{qq.question}** _({qq.impact} impact)_. Why: {qq.why}")
    L.append("")

    L.append("## Recommendation")
    for rec in r.recommendations:
        L.append(f"### {rec.method} ({rec.role.replace('_', ' ')})")
        L += [_stmt(s) for s in rec.rationale]
        if rec.conditions:
            L.append(f"- _Applies if:_ {rec.conditions}")
        L.append("")

    if run.matrix:
        L.append("**Method screening (deterministic, from sourced rules)**")
        L.append("")
        L.append("| Method | Score | Verdict | Contributions |")
        L.append("|---|---|---|---|")
        for m in run.matrix:
            contrib = "; ".join(f"{c.delta:+d} {c.reason}" for c in m.contributions) or "-"
            L.append(f"| {m.name} | {m.score} | {m.verdict.replace('_', ' ')} | {contrib} |")
        L.append("")

    L.append("## Measurement concept")
    L += [_stmt(s) for s in r.measurement_concept]
    L.append("")
    L.append("## Spectral range")
    L += [_stmt(s) for s in r.spectral_range]
    L.append("")
    L.append("## Risks and uncertainty")
    L += [_stmt(s) for s in r.risks]
    if run.confidence:
        L.append("")
        L.append(f"**Confidence: {run.confidence.level}** (computed, not self-reported)")
        L += [f"- {s.name}: {s.level} ({s.detail})" for s in run.confidence.signals]
        L += [f"- Cap: {c}" for c in run.confidence.caps]
        if run.confidence.raise_with:
            L.append("- To raise confidence, answer: " + " / ".join(run.confidence.raise_with))
    L.append("")

    fp = r.feasibility_plan
    L.append("## First feasibility experiment")
    for name, items in (("Samples", fp.samples), ("Reference measurements", fp.reference),
                        ("Comparison", fp.comparison), ("Decision basis", fp.decision_basis)):
        L.append(f"**{name}**")
        L += [f"- {x}" for x in items]
    if fp.steps:
        L.append("**Steps**")
        L += [f"{i}. {x}" for i, x in enumerate(fp.steps, 1)]
    L.append("")
    L.append("## AFS pathway")
    L.append(f"- Next step: {r.pathway.next_step}")
    L.append(f"- Likely path: {r.pathway.likely_path} {('- ' + r.pathway.why) if r.pathway.why else ''}")
    L.append("")

    cited = sorted({(c.source, c.page) for rec in r.recommendations for s in rec.rationale for c in s.citations} |
                   {(c.source, c.page) for s in r.measurement_concept + r.spectral_range + r.risks for c in s.citations} |
                   {(c.source, c.page) for p in run.premises for c in p.citations})
    L.append("## Sources")
    L.append(", ".join(f"{s} p.{p}" for s, p in cited) or "-")
    if run.verification:
        bad = [c for c in run.verification.claims if c.status not in ("verified", "fuzzy")]
        if bad:
            L.append("")
            L.append("**Verifier warnings**")
            L += [f"- {c.location}: {c.status} {c.detail}" for c in bad]
    if run.council and run.council.drafts:
        L.append("")
        L.append("## Council")
        L.append(f"Winner: draft {run.council.winner}; agreement {run.council.agreement:.0%} ({run.council.agreement_detail})")
        for d in run.council.drafts:
            L.append(f"- Draft {d.letter} ({d.model}): judge score {d.judge_total}, gate failures: "
                     f"{', '.join(d.gate_failures) or 'none'}")
    models = sorted({t.model for t in run.trace})
    L.append("")
    L.append(f"_Generated by the AFS assessment assistant (run {run.id}, mode {run.mode}, models: {', '.join(models) or '-'})._")
    return "\n".join(L) + "\n"
