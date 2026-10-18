"""POST /api/assess (SSE stream), /api/coach, /api/whatif."""
from __future__ import annotations

import asyncio
import json
import logging
import threading

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..auth import service as accounts
from ..cancellation import RunCancelled, cancellation_scope, check_cancelled
from ..engine import paths as paths_mod
from ..engine import pipeline
from ..kb import store
from ..schemas import AssessRequest, RunResult
from .auth import current_user

router = APIRouter(prefix="/api")
_RUN_LOCK = threading.Semaphore(2)   # free tier: at most two pipelines at once
log = logging.getLogger("afs.assess")


def _owner(http: Request | None) -> tuple[str, str, str | None] | None:
    """(user id, view, saved-query id) when a logged-in user starts a run; None for guests.
    The view (general/expert) and the sidebar query id come from headers so the run request is unchanged."""
    user = current_user(http) if http is not None else None
    if not user:
        return None
    view = http.headers.get("x-afs-view", "general")
    query_id = (http.headers.get("x-afs-query-id") or "")[:64] or None
    return user["id"], view, query_id


def _record(owner: tuple[str, str, str | None] | None, run: RunResult | None) -> None:
    if owner and run is not None:
        try:
            accounts.record_run(owner[0], run.model_dump(mode="json"), owner[1], owner[2])
        except Exception as exc:  # noqa: BLE001  (history is a convenience; never fail a run over it)
            log.warning("Could not link run to user: %s", exc)


def _stream(request: AssessRequest, owner: tuple[str, str, str | None] | None = None) -> StreamingResponse:
    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()
    cancelled = threading.Event()

    def enqueue(event: dict | None) -> None:
        if cancelled.is_set():
            return
        try:
            loop.call_soon_threadsafe(queue.put_nowait, event)
        except RuntimeError:  # the client and its event loop have already gone away
            cancelled.set()

    def emit(event: dict) -> None:
        if cancelled.is_set():
            raise RunCancelled("Assessment stopped")
        enqueue(event)

    def work() -> None:
        acquired = False
        try:
            # A cancelled request must not start later when a busy pipeline slot opens.
            while not cancelled.is_set():
                if _RUN_LOCK.acquire(timeout=0.1):
                    acquired = True
                    break
            if not acquired:
                return
            with cancellation_scope(cancelled):
                result = pipeline.run(request, emit)
                check_cancelled()
                _record(owner, result)   # linked before the stream closes
        except RunCancelled:
            pass
        finally:
            if acquired:
                _RUN_LOCK.release()
            enqueue(None)

    async def gen():
        try:
            threading.Thread(target=work, daemon=True).start()
            yield "retry: 60000\n\n"
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
                    continue
                if event is None:
                    break
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            cancelled.set()

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def _model(model: str | None) -> str | None:
    """Validate a chosen model (None / 'auto' = server defaults); 400 for a model this key cannot use."""
    from ..llm import models as models_mod
    try:
        return models_mod.validate_choice(model)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/models")
def models_list():
    """Models a user may choose for a run (every stage uses the choice; Council keeps its draft models)."""
    from ..config import settings
    from ..llm import models as models_mod
    return {"models": models_mod.selectable(),
            "defaults": {"fast": settings.model_fast, "main": settings.model_main},
            "council": models_mod.council_models(), "mock": settings.llm_mock or not settings.groq_api_key}


@router.post("/assess")
async def assess(request: AssessRequest, http: Request = None):
    request.model = _model(request.model)
    if not request.enquiry.strip():
        raise HTTPException(400, "Empty enquiry")
    if len(request.enquiry) > 6000:
        raise HTTPException(400, "Enquiry too long (max 6000 characters)")
    return _stream(request, _owner(http))


@router.post("/assess/sync")
def assess_sync(request: AssessRequest, http: Request = None):
    """Same pipeline without streaming (used by eval scripts and curl)."""
    request.model = _model(request.model)
    with _RUN_LOCK:
        result = pipeline.run(request)
    _record(_owner(http), result)
    return result.model_dump(mode="json")


class WhatIfRequest(BaseModel):
    run_id: str
    answers: dict[str, str]
    mode: str | None = None
    preferred_paths: list[str] | None = None
    model: str | None = None          # None = keep the parent run's model


@router.post("/whatif")
async def whatif(body: WhatIfRequest, http: Request = None):
    parent = store.get_run(body.run_id)
    if not parent:
        raise HTTPException(404, "Run not found")
    preferred_paths = body.preferred_paths if body.preferred_paths is not None else parent.get("preferred_paths", [])
    active_paths = set(preferred_paths) | set((parent.get("requirements") or {}).get("preferred_paths", []))
    answers = {**parent.get("answers", {}), **{k: v for k, v in body.answers.items() if v.strip()}}
    answers = {key: value for key, value in answers.items()
               if not paths_mod.is_path_answer(key) or key[5:6] in active_paths}
    req = AssessRequest(enquiry=parent["enquiry"], answers=answers, mode=body.mode or parent.get("mode", "fast"),
                        preferred_paths=preferred_paths, rejected=parent.get("rejected", []),
                        model=_model(body.model if body.model is not None else parent.get("model_choice") or None),
                        parent_run_id=body.run_id)
    return _stream(req, _owner(http))


class PrecheckRequest(BaseModel):
    enquiry: str
    answers: dict[str, str] = {}


@router.post("/precheck")
def precheck(body: PrecheckRequest):
    """Instant keyword pre-check before a run (no LLM, no tokens)."""
    from ..engine import precheck as precheck_mod
    if not body.enquiry.strip():
        return {"terms": [], "vague": [], "warnings": [], "missing": [], "completeness": 0, "total": 10, "words": 0}
    return precheck_mod.run(body.enquiry[:6000], body.answers)


class UnderstandRequest(BaseModel):
    enquiry: str
    answers: dict[str, str] = {}
    preferred_paths: list[str] = []
    model: str | None = None          # same model as the run, so the run reuses this cached reading


@router.post("/understand")
def understand(body: UnderstandRequest):
    """Step 1 of a UI run: what the assistant understood + one list of open questions ("Is this what you mean?").
    Uses the run's own extraction call, so confirming without new free-text answers reuses the cached reading."""
    from ..engine import understand as understand_mod
    if not body.enquiry.strip():
        raise HTTPException(400, "Empty enquiry")
    from ..llm import models as models_mod
    model = _model(body.model)
    with _RUN_LOCK:
        token = models_mod.use_model(model)
        try:
            return understand_mod.run(body.enquiry.strip()[:6000], body.answers,
                                      [p for p in body.preferred_paths if p in ("A", "B", "C")])
        finally:
            models_mod.reset_model(token)


@router.get("/paths")
def path_questions():
    """Full AFS path names and the optional questions asked when a path is chosen."""
    from ..engine import paths as paths_mod
    return paths_mod.questions_public()


@router.get("/glossary")
def glossary():
    from ..engine import glossary as glossary_mod
    return glossary_mod.public()


@router.get("/coach/{run_id}")
def coach(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return run.get("coach") or {}
