"""Model roles + council list; checks availability at startup."""
from __future__ import annotations

import logging

from ..config import settings
from .client import available_models

log = logging.getLogger(__name__)

# Groq's free tier limits tokens per minute PER MODEL. Only the report uses the big model;
# everything else runs on the fast model so the two budgets are used in parallel.
ROLES = {
    "extract": "fast",
    "premise": "fast",
    "report": "main",
    "repair": "fast",
    "judge": "fast",
    "coach": "fast",
}

_status: dict = {"checked": False, "available": [], "missing": []}


def model_for(stage: str) -> str:
    role = ROLES.get(stage, "main")
    return settings.model_fast if role == "fast" else settings.model_main


def council_models() -> list[str]:
    models = settings.council_models
    avail = _status["available"]
    if avail:
        models = [m for m in models if m in avail] or [settings.model_main]
    return models


def family(model: str) -> str:
    m = model.lower()
    for fam in ("gpt-oss", "qwen", "llama", "kimi", "mixtral", "gemma", "deepseek"):
        if fam in m:
            return fam
    return m.split("/")[0]


def check() -> dict:
    """Called at startup: which configured models does this key actually have?"""
    if settings.llm_mock or not settings.groq_api_key:
        _status.update(checked=True, available=[], missing=[], note="mock mode or no key")
        return _status
    avail = available_models()
    wanted = {settings.model_fast, settings.model_main, *settings.council_models}
    _status.update(checked=True, available=avail, missing=sorted(m for m in wanted if avail and m not in avail))
    if _status["missing"]:
        log.warning("Configured models not available to this key: %s", _status["missing"])
    return _status


def status() -> dict:
    return dict(_status)