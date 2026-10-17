"""POST /api/assess (SSE stream), /api/coach, /api/whatif."""
from __future__ import annotations

import asyncio
import json
import threading

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..engine import pipeline
from ..kb import store
from ..schemas import AssessRequest

router = APIRouter(prefix="/api")
_RUN_LOCK = threading.Semaphore(2)   # free tier: at most two pipelines at once


def _stream(request: AssessRequest) -> StreamingResponse:
    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def emit(event: dict) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, event)

    def work() -> None:
        with _RUN_LOCK:
            try:
                pipeline.run(request, emit)
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

    threading.Thread(target=work, daemon=True).start()

    async def gen():
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

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.post("/assess")
async def assess(request: AssessRequest):
    if not request.enquiry.strip():
        raise HTTPException(400, "Empty enquiry")
    if len(request.enquiry) > 6000:
        raise HTTPException(400, "Enquiry too long (max 6000 characters)")
    return _stream(request)


@router.post("/assess/sync")
def assess_sync(request: AssessRequest):
    """Same pipeline without streaming (used by eval scripts and curl)."""
    with _RUN_LOCK:
        return pipeline.run(request).model_dump(mode="json")


class WhatIfRequest(BaseModel):
    run_id: str
    answers: dict[str, str]
    mode: str | None = None


@router.post("/whatif")
async def whatif(body: WhatIfRequest):
    parent = store.get_run(body.run_id)
    if not parent:
        raise HTTPException(404, "Run not found")
    answers = {**parent.get("answers", {}), **{k: v for k, v in body.answers.items() if v.strip()}}
    req = AssessRequest(enquiry=parent["enquiry"], answers=answers, mode=body.mode or parent.get("mode", "fast"),
                        parent_run_id=body.run_id)
    return _stream(req)


@router.get("/coach/{run_id}")
def coach(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return run.get("coach") or {}
