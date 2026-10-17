"""Stage 5: method screening matrix (scored, explained).

Scores are sums of rule contributions, so every point in the matrix traces back to a
sourced rule. The LLM later explains the matrix; it does not invent it.
"""
from __future__ import annotations

from ..schemas import METHOD_IDS, METHOD_NAMES, Contribution, MethodScore, Requirements, RuleHit


def screen(req: Requirements, hits: list[RuleHit]) -> list[MethodScore]:
    rows = {m: MethodScore(method_id=m, name=METHOD_NAMES[m], score=0,
                           requested_by_client=m in req.requested_methods) for m in METHOD_IDS}
    for h in hits:
        for method, delta in h.scores.items():
            if method in rows and delta:
                rows[method].score += delta
                src = ", ".join(f"{s.source} p.{s.page}" for s in h.sources[:2])
                rows[method].contributions.append(Contribution(rule_id=h.rule_id, delta=delta,
                                                               reason=f"{h.title} [{src}]"))
    ranked = sorted(rows.values(), key=lambda r: r.score, reverse=True)
    top = ranked[0].score if ranked else 0
    for r in ranked:
        if r.score <= -2:
            r.verdict = "not_supported"
        elif top >= 2 and r.score == top:
            r.verdict = "lead"
        elif r.score >= 1:
            r.verdict = "candidate"
        else:
            r.verdict = "weak"
    return ranked
