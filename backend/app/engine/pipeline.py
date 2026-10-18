"""Orchestrates stages, emits SSE events, saves run.

    extract -> rules/coverage/screen -> retrieve -> premise check -> report (fast | council)
            -> verify -> quality (+1 repair) -> coach -> confidence -> save
"""
from __future__ import annotations

import time
import uuid
from typing import Callable, Optional

from ..config import settings
from ..kb import retrieve as retrieve_mod
from ..kb import store
from ..render import outline as outline_mod
from ..llm.models import model_for
from ..schemas import AssessRequest, RunResult
from . import coach as coach_mod
from . import confidence as confidence_mod
from . import council as council_mod
from . import coverage as coverage_mod
from . import extract as extract_mod
from . import paths as paths_mod
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
    "rules": {"rule_hits", "coverage", "matrix", "spectral", "paths"},
    "retrieve": {"evidence", "retrieval"},
    "premise": {"premises"},
    "report": {"report", "council"},
    "council": {"report", "council"},
    "verify": {"report", "verification", "quality"},
    "coach": {"coach", "confidence", "diff", "outline"},
}


def run(request: AssessRequest, emit: Optional[Emit] = None) -> RunResult:
    """Run the pipeline; a chosen model applies to every stage of this run only."""
    from ..llm import models as models_mod
    token = models_mod.use_model(request.model if request.model != "auto" else None)
    try:
        return _run(request, emit)
    finally:
        models_mod.reset_model(token)


def _run(request: AssessRequest, emit: Optional[Emit] = None) -> RunResult:
    emit = emit or (lambda e: None)
    run_ = RunResult(id=uuid.uuid4().hex[:10], created=time.strftime("%Y-%m-%dT%H:%M:%S"), mode=request.mode,
                     enquiry=request.enquiry.strip(), answers=request.answers, parent_run_id=request.parent_run_id,
                     preferred_paths=list(request.preferred_paths), rejected=list(request.rejected),
                     model_choice=request.model if request.model and request.model != "auto" else "")
    trace = run_.trace
    t_all = time.time()

    def stage(name: str, label: str):
        emit({"type": "stage", "stage": name, "status": "start", "label": label})
        return time.time()

    def done(name: str, t0: float, detail: str = ""):
        run_.timings_ms[name] = int((time.time() - t0) * 1000)
        emit({"type": "stage", "stage": name, "status": "done", "detail": detail, "ms": run_.timings_ms[name]})
        emit({"type": "stage_result", "stage": name,
              "data": run_.model_dump(mode="json", include=STAGE_FIELDS[name] | {"trace"})})

    def model_activity(name: str, task: str):
        actor = ("Rule fallback" if settings.llm_mock or not settings.groq_api_key
                 else model_for(name))
        emit({"type": "detail", "stage": name, "detail": f"{actor}: {task}"})

    def council_activity(name: str, detail: str):
        if settings.llm_mock:
            detail += " (no LLM call in mock mode)"
        emit({"type": "detail", "stage": name, "detail": detail})

    try:
        t = stage("extract", "Reading the enquiry")
        model_activity("extract", "extracting facts and unknowns")
        req = extract_mod.extract(run_.enquiry, run_.answers, trace)
        req = extract_mod.apply_rejected(req, run_.rejected)   # readings the user marked as wrong -> unknown
        run_.requirements = req
        done("extract", t, f"{len(req.facts)} facts, {len(req.unknowns)} unknowns, {len(req.premises)} premises")

        t = stage("rules", "Applying AFS rules, fiber coverage and method screening")
        run_.rule_hits = rules_mod.evaluate(req, run_.enquiry, run_.answers)
        run_.coverage = coverage_mod.compute(req)
        run_.matrix = screen_mod.screen(req, run_.rule_hits)
        run_.spectral = coverage_mod.spectral_map(req, run_.enquiry)
        run_.paths = paths_mod.analyse(run_.rule_hits, req, list(request.preferred_paths), run_.answers)
        blocks = sum(1 for h in run_.rule_hits if h.severity == "block")
        done("rules", t, f"{len(run_.rule_hits)} rules fired ({blocks} blocking)")

        t = stage("retrieve", "Retrieving evidence (BM25 + dense, RRF, MMR)")
        pinned = [(s.source, s.page) for h in run_.rule_hits if h.severity in ("block", "warn") for s in h.sources]
        run_.evidence, run_.retrieval = retrieve_mod.retrieve(queries_for(req, run_.enquiry, run_.rule_hits, run_.matrix),
                                                              pinned_pages=pinned)
        done("retrieve", t, f"{len(run_.evidence)} passages")

        t = stage("premise", "Checking the client's premises")
        model_activity("premise", "checking customer claims against evidence")
        run_.premises = premise_mod.check(run_.enquiry, req, run_.rule_hits, run_.evidence, trace)
        done("premise", t, ", ".join(f"{p.premise_id}: {p.verdict}" for p in run_.premises) or "no premises")

        user_prompt = report_mod.build_user_prompt(run_.enquiry, run_.answers, req, run_.rule_hits, run_.matrix,
                                                   run_.coverage, run_.premises, run_.evidence)
        user_prompt += f"\n\nAFS PATH ANALYSIS (computed from sourced rules; do not contradict it):\n{paths_mod.prompt_block(run_.paths)}"
        rule_fallback = lambda: report_mod.rule_report(run_.enquiry, req, run_.rule_hits, run_.matrix,  # noqa: E731
                                                       run_.coverage, run_.premises)
        llm_report = True
        if request.mode == "council":
            t = stage("council", "Council: drafts, gates, blind cross-judging")
            rep, run_.council = council_mod.run(user_prompt, run_.enquiry, run_.answers, run_.rule_hits, run_.matrix,
                                                run_.coverage, run_.premises, run_.evidence, trace,
                                                on_event=council_activity)
            if rep is None:
                rep, llm_report = rule_fallback(), False
            run_.report = rep
            done("council", t, f"winner {run_.council.winner or '-'}, agreement {run_.council.agreement:.0%}")
        else:
            t = stage("report", "Writing the assessment")
            model_activity("report", "drafting the assessment")
            rep = report_mod.draft(model_for("report"), "report", user_prompt, trace)
            if rep is None:
                rep, llm_report = rule_fallback(), False
            run_.report = rep
            done("report", t, rep.decision_status)

        # the pathway is deterministic and traceable: the computed path wins over the model's guess
        if run_.paths:
            if rep.pathway.likely_path != run_.paths.suggested or not rep.pathway.why:
                rep.pathway.why = " ".join(run_.paths.reasons)
            rep.pathway.likely_path = run_.paths.suggested

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
        model_activity("coach", "preparing follow-up questions")
        run_.coach = coach_mod.build(run_.enquiry, req, run_.answers, trace)
        run_.confidence = confidence_mod.compute(req, run_.rule_hits, run_.matrix, run_.premises, ver, run_.coach,
                                                 run_.council, rep)
        if request.parent_run_id:
            parent = store.get_run(request.parent_run_id)
            if parent:
                run_.diff = whatif_mod.diff(RunResult.model_validate(parent), run_)
        run_.outline = outline_mod.build(run_)   # the 11-section output format (page, export, outputs/)
        done("coach", t, f"completeness {run_.coach.completeness}/{run_.coach.total}")
    except Exception as exc:  # never lose a run silently
        run_.error = f"{type(exc).__name__}: {exc}"
        emit({"type": "error", "detail": run_.error})
    run_.timings_ms["total"] = int((time.time() - t_all) * 1000)
    store.save_run(run_.model_dump(mode="json"))
    emit({"type": "result", "run": run_.model_dump(mode="json")})
    return run_