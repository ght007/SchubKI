"""Multi-model drafts -> gates -> blind cross-judge -> merge.

1. Each council model writes a full draft from the same inputs.
2. Hard gates (deterministic verifier + quality checks) run on every draft.
3. Each model judges the OTHER drafts, anonymised as letters in shuffled order,
   against a rubric copied from the jury criteria (self-judging is excluded).
4. Winner = gate-passing draft with the best mean judge score. Its questions and
   plan are swapped for the drafts judged best on those sections (deterministic merge).
5. Agreement on the lead method and the decision status is reported as a signal.
"""
from __future__ import annotations

import random
from collections import Counter

from ..config import settings
from ..llm.client import complete_json
from ..llm.models import council_models, family
from ..schemas import (Council, CouncilDraft, Evidence, JudgeOut, MethodCoverage, MethodScore, PremiseVerdict, Report,
                       RuleHit, TraceItem)
from . import quality as quality_mod
from . import report as report_mod
from . import verify as verify_mod
from .context import fmt_rules

LETTERS = "ABCDE"


def _lead(r: Report) -> list[str]:
    prim = [m for x in r.recommendations if x.role == "primary" for m in x.method_ids]
    return sorted(set(prim))


def _summary(r: Report) -> str:
    """Compact rendering of a draft for judges (keeps judge prompts small)."""
    recs = "\n".join(f"  - {x.role}: {x.method} | " + " / ".join(s.text for s in x.rationale[:2]) for x in r.recommendations)
    qs = "\n".join(f"  - ({q.impact}) {q.question}" for q in r.clarification_questions)
    risks = "\n".join(f"  - {s.text}" for s in r.risks[:5])
    fp = r.feasibility_plan
    plan = "\n".join(f"  - {t}" for t in (fp.samples + fp.reference + fp.comparison + fp.decision_basis + fp.steps)[:10])
    return (f"STATUS: {r.decision_status}\nHEADLINE: {r.headline}\nRECOMMENDATIONS:\n{recs}\nQUESTIONS:\n{qs}\n"
            f"RISKS:\n{risks}\nPLAN:\n{plan}\nPATHWAY: {r.pathway.likely_path} - {r.pathway.next_step}")


def run(user_prompt: str, enquiry: str, answers: dict, hits: list[RuleHit], matrix: list[MethodScore],
        coverage: list[MethodCoverage], premises: list[PremiseVerdict], evidence: list[Evidence],
        trace: list[TraceItem], on_event=None) -> tuple[Report | None, Council]:
    models = council_models()
    council = Council(families=len({family(m) for m in models}))
    drafts: dict[str, Report] = {}
    for i, model in enumerate(models):
        letter = LETTERS[i]
        if on_event:
            on_event("council", f"Draft {letter} by {model}")
        rep = report_mod.draft(model, f"council_draft_{letter}", user_prompt, trace)
        d = CouncilDraft(letter=letter, model=model, ok=rep is not None, error="" if rep else "model failed")
        if rep:
            ver = verify_mod.verify(rep, enquiry, answers, evidence)
            q = quality_mod.check(rep, ver, hits, matrix, coverage, premises)
            d.gate_failures = [f"{i.id} {i.name}" for i in q.items if i.status == "fail" and i.category in ("grounding", "honesty")]
            d.lead_methods, d.status = _lead(rep), rep.decision_status
            drafts[letter] = rep
        council.drafts.append(d)
    if not drafts:
        return None, council

    # blind cross-judging
    totals: dict[str, list[float]] = {k: [] for k in drafts}
    section_votes = {"questions": Counter(), "plan": Counter()}
    for jd in council.drafts:
        if not jd.ok:
            continue
        others = [k for k in drafts if k != jd.letter]
        if not others:
            continue
        random.shuffle(others)
        alias = {k: LETTERS[n] for n, k in enumerate(others)}
        back = {v: k for k, v in alias.items()}
        body = "\n\n".join(f"=== DRAFT {alias[k]} ===\n{_summary(drafts[k])}" for k in others)
        system = (settings.prompts_dir / "judge.md").read_text(encoding="utf-8")
        user = f"ENQUIRY:\n{enquiry}\n\nRULE FINDINGS:\n{fmt_rules(hits)}\n\n{body}"
        if on_event:
            on_event("council", f"{jd.model} judges drafts {', '.join(others)}")
        out = complete_json(f"council_judge_{jd.letter}", jd.model, system, user, JudgeOut, trace,
                            max_tokens=900, temperature=0.0)
        if not out:
            continue
        rec = {"judge": jd.letter, "judge_model": jd.model, "scores": {}}
        for s in out.scores:
            real = back.get(s.draft.strip().upper()[:1])
            if not real:
                continue
            total = (s.technical + s.grounding + s.plan + s.clarification + s.explainability + s.honesty) / 6
            totals[real].append(total)
            rec["scores"][real] = round(total, 2)
        rec["best"] = back.get(out.best.strip().upper()[:1], "")
        for key, val in (("questions", out.best_questions_from), ("plan", out.best_plan_from)):
            real = back.get((val or "").strip().upper()[:1])
            if real:
                section_votes[key][real] += 1
        council.judgements.append(rec)

    for d in council.drafts:
        if d.letter in totals and totals[d.letter]:
            d.judge_total = round(sum(totals[d.letter]) / len(totals[d.letter]), 2)

    def rank_key(d: CouncilDraft):
        return (len(d.gate_failures) == 0, d.judge_total, -ord(d.letter))

    ok = [d for d in council.drafts if d.ok]
    winner = max(ok, key=rank_key)
    council.winner = winner.letter
    final = drafts[winner.letter].model_copy(deep=True)

    # deterministic merge of the best-voted sections (only from gate-passing drafts)
    passing = {d.letter for d in ok if not d.gate_failures}
    for key, attr in (("questions", "clarification_questions"), ("plan", "feasibility_plan")):
        if section_votes[key]:
            best, _ = section_votes[key].most_common(1)[0]
            if best != winner.letter and best in passing:
                setattr(final, attr, getattr(drafts[best], attr))
                council.merged_from[attr] = best

    leads = [tuple(d.lead_methods) for d in ok]
    statuses = [d.status for d in ok]
    lead_agree = Counter(leads).most_common(1)[0][1] / len(leads)
    status_agree = Counter(statuses).most_common(1)[0][1] / len(statuses)
    council.agreement = round(min(lead_agree, status_agree), 2)
    council.agreement_detail = (f"{Counter(leads).most_common(1)[0][1]}/{len(leads)} drafts share the lead method(s) "
                                f"{'+'.join(Counter(leads).most_common(1)[0][0]) or 'none'}; "
                                f"{Counter(statuses).most_common(1)[0][1]}/{len(statuses)} share the status "
                                f"'{Counter(statuses).most_common(1)[0][0]}'")
    return final, council
