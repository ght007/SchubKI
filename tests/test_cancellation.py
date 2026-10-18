"""Stopping a stream must stop subsequent work, retries and completed-run history."""
import asyncio
from dataclasses import replace
from threading import Event, Semaphore, Thread
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from backend.app.api import assess
from backend.app.cancellation import RunCancelled, cancellation_scope, wait_for_retry
from backend.app.engine import pipeline
from backend.app.llm import client
from backend.app.schemas import AssessRequest, Requirements, RunResult


def test_cancelled_pipeline_does_not_advance_or_save(monkeypatch):
    cancelled = Event()
    events, saved, later_stages = [], [], []

    def extract(*args):
        cancelled.set()  # user stops while the current model call is finishing
        return Requirements(summary="Water in oil")

    monkeypatch.setattr(pipeline.extract_mod, "extract", extract)
    monkeypatch.setattr(pipeline.rules_mod, "evaluate", lambda *args: later_stages.append("rules"))
    monkeypatch.setattr(pipeline.store, "save_run", saved.append)
    with cancellation_scope(cancelled), pytest.raises(RunCancelled):
        pipeline.run(AssessRequest(enquiry="Water in oil"), events.append)

    assert not later_stages
    assert not saved
    assert not any(event["type"] in ("result", "error") for event in events)


def test_stop_interrupts_llm_backoff_without_retry_or_fallback(monkeypatch):
    class Reply(BaseModel):
        answer: str

    class RateLimited(Exception):
        status_code = 429

    attempted, cancelled, finished = Event(), Event(), Event()
    calls, fallbacks, outcome = [], [], []

    def create(**kwargs):
        calls.append(kwargs)
        attempted.set()
        raise RateLimited("retry later")

    monkeypatch.setattr(client, "settings", replace(client.settings, llm_mock=False, llm_cache=False))
    monkeypatch.setattr(client, "_get_client", lambda: SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    monkeypatch.setattr(client, "_retry_after", lambda exc: 30)

    def work():
        try:
            with cancellation_scope(cancelled):
                client.complete_json("report", "test-model", "system", "user", Reply, [],
                                     fallback=lambda: fallbacks.append(True))
        except RunCancelled:
            outcome.append("cancelled")
        finally:
            finished.set()

    worker = Thread(target=work, daemon=True)
    worker.start()
    try:
        assert attempted.wait(2)
        cancelled.set()
        assert finished.wait(2)
    finally:
        cancelled.set()
        worker.join(2)
    assert outcome == ["cancelled"]
    assert len(calls) == 1
    assert not fallbacks


def test_disconnected_stream_cancels_worker_and_does_not_record(monkeypatch):
    started, finished = Event(), Event()
    recorded = []

    def fake_run(request, emit):
        started.set()
        try:
            wait_for_retry(30)
            return RunResult(id="late", created="now", mode="fast", enquiry=request.enquiry)
        finally:
            finished.set()

    monkeypatch.setattr(assess.pipeline, "run", fake_run)
    monkeypatch.setattr(assess, "_RUN_LOCK", Semaphore(1))
    monkeypatch.setattr(assess, "_record", lambda *args: recorded.append(args))

    async def disconnect():
        response = assess._stream(AssessRequest(enquiry="Water in oil"), ("user", "general", None))
        body = response.body_iterator
        await anext(body)
        try:
            assert await asyncio.to_thread(started.wait, 2)
        finally:
            await body.aclose()
        assert await asyncio.to_thread(finished.wait, 2)

    asyncio.run(disconnect())
    assert not recorded
    assert assess._RUN_LOCK.acquire(timeout=2)  # the cancelled worker releases its slot


def test_completed_stream_still_delivers_and_records_result(monkeypatch):
    recorded = []
    result = RunResult(id="complete", created="now", mode="fast", enquiry="Water in oil")

    def fake_run(request, emit):
        emit({"type": "result", "run": result.model_dump(mode="json")})
        return result

    monkeypatch.setattr(assess.pipeline, "run", fake_run)
    monkeypatch.setattr(assess, "_record", lambda *args: recorded.append(args))

    async def complete():
        response = assess._stream(AssessRequest(enquiry=result.enquiry), ("user", "general", None))
        return "".join([chunk async for chunk in response.body_iterator])

    body = asyncio.run(complete())
    assert '"type": "result"' in body
    assert recorded == [(("user", "general", None), result)]


def test_cancelled_queued_stream_never_starts_pipeline(monkeypatch):
    workers, calls = [], []

    def worker_thread(*args, **kwargs):
        thread = Thread(*args, **kwargs)
        workers.append(thread)
        return thread

    monkeypatch.setattr(assess, "threading", SimpleNamespace(Event=Event, Thread=worker_thread))
    monkeypatch.setattr(assess, "_RUN_LOCK", Semaphore(0))
    monkeypatch.setattr(assess.pipeline, "run", lambda *args: calls.append(args))

    async def disconnect():
        body = assess._stream(AssessRequest(enquiry="Queued enquiry")).body_iterator
        await anext(body)
        await body.aclose()
        await asyncio.to_thread(workers[0].join, 2)

    asyncio.run(disconnect())
    assert not workers[0].is_alive()
    assert not calls
