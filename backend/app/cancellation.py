"""Cooperative cancellation for a pipeline running in its own worker thread."""
from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from threading import Event

_cancelled: ContextVar[Event | None] = ContextVar("run_cancelled", default=None)


class RunCancelled(Exception):
    """A disconnected caller stopped the run; do not fall back or save a result."""


@contextmanager
def cancellation_scope(event: Event):
    token = _cancelled.set(event)
    try:
        check_cancelled()
        yield
    finally:
        _cancelled.reset(token)


def check_cancelled() -> None:
    event = _cancelled.get()
    if event is not None and event.is_set():
        raise RunCancelled("Assessment stopped")


def wait_for_retry(seconds: float) -> None:
    event = _cancelled.get()
    if event is None:
        time.sleep(seconds)
    elif event.wait(seconds):
        raise RunCancelled("Assessment stopped")
