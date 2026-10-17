"""Shared helpers: format rules, evidence and requirements compactly for prompts,
and look up curated claims by page (used by rule-based fallbacks)."""
from __future__ import annotations

import json
from functools import lru_cache

from ..kb.ingest import load_claims
from ..schemas import Citation, Evidence, MethodCoverage, MethodScore, Requirements, RuleHit


@lru_cache(maxsize=1)
def claims_by_page() -> dict[tuple[str, int], list[dict]]:
    out: dict[tuple[str, int], list[dict]] = {}
    for c in load_claims():
        out.setdefault((c["source"], c["page"]), []).append(c)
    return out


def citations_for_rule(hit: RuleHit, limit: int = 2) -> list[Citation]:
    """Verbatim citations from curated claims on the pages a rule cites."""
    cites: list[Citation] = []
    for s in hit.sources:
        for c in claims_by_page().get((s.source, s.page), [])[:1]:
            cites.append(Citation(source=c["source"], page=c["page"], quote=c["quote"]))
        if len(cites) >= limit:
            break
    return cites


def fmt_requirements(req: Requirements) -> str:
    d = req.model_dump(exclude={"facts", "unknowns", "premises"})
    d = {k: v for k, v in d.items() if v not in ("unknown", [], "")}
    unknowns = [f"{u.item} ({u.impact})" for u in req.unknowns]
    return json.dumps({"known": d, "unknown": unknowns}, ensure_ascii=False)


def fmt_rules(hits: list[RuleHit]) -> str:
    lines = []
    for h in hits:
        if not h.text and not h.question:
            continue
        src = ", ".join(f"{s.source} p.{s.page}" for s in h.sources)
        lines.append(f"- {h.rule_id} [{h.severity}] {h.text} (sources: {src})")
    return "\n".join(lines) or "- none"


def fmt_matrix(matrix: list[MethodScore], coverage: list[MethodCoverage]) -> str:
    lines = []
    cov = {c.method_id: c for c in coverage}
    for m in matrix:
        why = "; ".join(f"{c.delta:+d} {c.reason}" for c in m.contributions) or "no rule fired"
        req = " (requested by client)" if m.requested_by_client else ""
        lines.append(f"- {m.method_id}: score {m.score}, {m.verdict}{req}: {why}")
        c = cov.get(m.method_id)
        if c and c.asset_check:
            lines.append(f"  ! {c.asset_check}")
    return "\n".join(lines)


def fmt_evidence(evidence: list[Evidence]) -> str:
    out = []
    for e in evidence:
        head = f"[{e.ref}] {e.source} p.{e.page} (scope: {e.scope or 'n/a'})"
        if e.kind == "claim" and e.quote:
            out.append(f"{head}\n  claim: {e.text.split(' Quote:')[0]}\n  QUOTE: \"{e.quote}\"")
        else:
            out.append(f"{head}\n  TEXT: {e.text}")
    return "\n".join(out)


def queries_for(req: Requirements, enquiry: str, hits: list[RuleHit], matrix: list[MethodScore]) -> list[str]:
    targets = ", ".join(req.target_variables) or "composition"
    leads = [m.name for m in matrix if m.verdict in ("lead", "candidate")][:3]
    q = [
        f"{targets} in {req.matrix} {req.phase}",
        f"{req.optical_behavior} {req.phase} probe geometry {' '.join(leads)}",
        " ".join(h.title for h in hits[:4]),
        enquiry[:300],
    ]
    if req.existing_assets:
        q.append(" ".join(req.existing_assets)[:200])
    if req.requested_methods:
        q.append(" ".join(req.requested_methods) + " limitations " + targets)
    return q
