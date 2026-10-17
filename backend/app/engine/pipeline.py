"""Orchestrates stages, emits SSE events, saves run.

    extract -> rules/coverage/screen -> retrieve -> premise check -> report (fast | council)
            -> verify -> quality (+1 repair) -> coach -> confidence -> save
"""
from __future__ import annotations

import time
import uuid
from typing import Callable, Optional

from ..kb import retrieve as retrieve_mod
from ..kb import store
from ..llm.models import model_for
from ..schemas import AssessRequest, RunResult
from . import coach as coach_mod
from . import confidence as confidence_mod
from . import council as council_mod
from . import coverage as coverage_mod
from . import extract as extract_mod
from . import premise as premise_mod
from . import quality as quality_mod
from . import report as report_mod
from . import rules as rules_mod
from . import screen as screen_mod
from . import verify as verify_mod
from . import whatif as whatif_mod
from .context import queries_for

Emit = Callable[[dict], None]

STAGE_FIELDS = {
    "extract": {"requirements"},
    "rules": {"rule_hits", "coverage", "matrix", "spectral"},
    "retrieve": {"evidence", "retrieval"},
    "premise": {"premises"},
    "report": {"report", "council"},
    "council": {"report", "council"},
    "verify": {"report", "verification", "quality"},
    "coach": {"coach", "confidence", "diff"},
}


def run(request: AssessRequest, emit: Optional[Emit] = None) -> RunResult:
    emit = emit or (lambda e: None)
    run_ = RunResult(id=uuid.uuid4().hex[:10], created=time.strftime("%Y-%m-%dT%H:%M:%S"), mode=request.mode,
                     enquiry=request.enquiry.strip(), answers=request.answers, parent_run_id=request.parent_run_id)
    trace = run_.trace
    t_all = time.time()

    def stage(name: str, label: str):
        emit({"type": "stage", "stage": name, "status": "start", "label": label})
        return time.time()

    def done(name: str, t0: float, detail: str = ""):
        run_.timings_ms[name] = int((time.time() - t0) * 1000)
        emit({"type": "stage", "stage": name, "status": "done", "detail": detail, "ms": run_.timings_ms[name]})
        emit({"type": "stage_result", "stage": name,
              "data": run_.model_dump(mode="json", include=STAGE_FIELDS[name])})

    try:
        t = stage("extract", "Reading the enquiry")
        req = extract_mod.extract(run_.enquiry, run_.answers, trace)
        run_.requirements = req
        done("extract", t, f"{len(req.facts)} facts, {len(req.unknowns)} unknowns, {len(req.premises)} premises")

        t = stage("rules", "Applying AFS rules, fiber coverage and method screening")
        run_.rule_hits = rules_mod.evaluate(req, run_.enquiry, run_.answers)
        run_.coverage = coverage_mod.compute(req)
        run_.matrix = screen_mod.screen(req, run_.rule_hits)
        run_.spectral = coverage_mod.spectral_map(req, run_.enquiry)
        blocks = sum(1 for h in run_.rule_hits if h.severity == "block")
        done("rules", t, f"{len(run_.rule_hits)} rules fired ({blocks} blocking)")

        t = stage("retrieve", "Retrieving evidence (BM25 + dense, RRF, MMR)")
        pinned = [(s.source, s.page) for h in run_.rule_hits if h.severity in ("block", "warn") for s in h.sources]
        run_.evidence, run_.retrieval = retrieve_mod.retrieve(queries_for(req, run_.enquiry, run_.rule_hits, run_.matrix),
                                                              pinned_pages=pinned)
        done("retrieve", t, f"{len(run_.evidence)} passages")

        t = stage("premise", "Checking the client's premises")
        run_.premises = premise_mod.check(run_.enquiry, req, run_.rule_hits, run_.evidence, trace)
        done("premise", t, ", ".join(f"{p.premise_id}: {p.verdict}" for p in run_.premises) or "no premises")

        user_prompt = report_mod.build_user_prompt(run_.enquiry, run_.answers, req, run_.rule_hits, run_.matrix,
                                                   run_.coverage, run_.premises, run_.evidence)
        rule_fallback = lambda: report_mod.rule_report(run_.enquiry, req, run_.rule_hits, run_.matrix,  # noqa: E731
                                                       run_.coverage, run_.premises)
        llm_report = True
        if request.mode == "council":
            t = stage("council", "Council: drafts, gates, blind cross-judging")
            rep, run_.council = council_mod.run(user_prompt, run_.enquiry, run_.answers, run_.rule_hits, run_.matrix,
                                                run_.coverage, run_.premises, run_.evidence, trace,
                                                on_event=lambda s, d: emit({"type": "detail", "stage": s, "detail": d}))
            if rep is None:
                rep, llm_report = rule_fallback(), False
            run_.report = rep
            done("council", t, f"winner {run_.council.winner or '-'}, agreement {run_.council.agreement:.0%}")
        else:
            t = stage("report", "Writing the assessment")
            rep = report_mod.draft(model_for("report"), "report", user_prompt, trace)
            if rep is None:
                rep, llm_report = rule_fallback(), False
            run_.report = rep
            done("report", t, rep.decision_status)

        t = stage("verify", "Verifying citations, numbers and client facts")
        ver = verify_mod.verify(rep, run_.enquiry, run_.answers, run_.evidence)
        q = quality_mod.check(rep, ver, run_.rule_hits, run_.matrix, run_.coverage, run_.premises)
        if llm_report and quality_mod.needs_repair(q):
            emit({"type": "detail", "stage": "verify", "detail": "Quality gate failed: one repair round"})
            fixed = quality_mod.repair(rep, q, ver, run_.rule_hits, run_.evidence, trace)
            if fixed:
                ver2 = verify_mod.verify(fixed, run_.enquiry, run_.answers, run_.evidence)
                q2 = quality_mod.check(fixed, ver2, run_.rule_hits, run_.matrix, run_.coverage, run_.premises)
                if q2.passed >= q.passed:
                    notes = [f"{i.id} fixed" for i in q.items if i.status == "fail" and
                             next(x for x in q2.items if x.id == i.id).status != "fail"]
                    rep, ver, q = fixed, ver2, q2
                    q.repaired, q.repair_notes = True, notes
        run_.report, run_.verification, run_.quality = rep, ver, q
        done("verify", t, f"{ver.n_verified}/{ver.n_sourced} claims verified, quality {q.passed}/{q.total}")

        t = stage("coach", "Enquiry coach")
        run_.coach = coach_mod.build(run_.enquiry, req, run_.answers, trace)
        run_.confidence = confidence_mod.compute(req, run_.rule_hits, run_.matrix, run_.premises, ver, run_.coach,
                                                 run_.council, rep)
        if request.parent_run_id:
            parent = store.get_run(request.parent_run_id)
            if parent:
                run_.diff = whatif_mod.diff(RunResult.model_validate(parent), run_)
        done("coach", t, f"completeness {run_.coach.completeness}/{run_.coach.total}")
    except Exception as exc:  # never lose a run silently
        run_.error = f"{type(exc).__name__}: {exc}"
        emit({"type": "error", "detail": run_.error})
    run_.timings_ms["total"] = int((time.time() - t_all) * 1000)
    store.save_run(run_.model_dump(mode="json"))
    emit({"type": "result", "run": run_.model_dump(mode="json")})
    return run_
