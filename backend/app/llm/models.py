"""Model roles + council list; checks availability at startup; per-run model choice.

A run may choose one model for every stage (AssessRequest.model). The choice is held in a context
variable for the duration of pipeline.run, so model_for() returns it everywhere without passing it
through every engine function. Council drafts keep their own model list (comparing models is the point
of Council); every other stage of a Council run uses the chosen model.
Only chat models this key can use are selectable; speech, voice and guard models are filtered out.
"""
from __future__ import annotations

import contextvars
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


_override: contextvars.ContextVar[str | None] = contextvars.ContextVar("afs_model_override", default=None)

# not chat models, or not general-purpose ones: never offered
_EXCLUDE = ("whisper", "orpheus", "tts", "guard", "embed", "distil")
# short notes for the picker; unknown models are still offered, marked "not tested"
_NOTES = {
    "openai/gpt-oss-120b": "Most capable; slower and the tightest free-tier limit",
    "openai/gpt-oss-20b": "Fast; good for most enquiries",
    "qwen/qwen3.8-27b": "Different model family; useful for a second opinion",
}


def use_model(model: str | None):
    """Set the run's model (None = server default per stage). Returns a token for reset_model()."""
    return _override.set(model or None)


def reset_model(token) -> None:
    _override.reset(token)


def chosen_model() -> str | None:
    return _override.get()


def selectable() -> list[dict]:
    """Models a user may choose: chat models this key has (or the configured ones in mock / no-key mode)."""
    configured = [settings.model_fast, settings.model_main, *settings.council_models]
    pool = _status["available"] or configured
    ids = [m for m in dict.fromkeys(configured + sorted(pool)) if m in pool and not any(x in m.lower() for x in _EXCLUDE)]
    roles = {settings.model_fast: "server default for reading, claims, repair and coach",
             settings.model_main: "server default for the report"}
    return [{"id": m, "note": _NOTES.get(m, "Not tested with this assistant"), "default_role": roles.get(m, ""),
             "tested": m in _NOTES} for m in ids]


def validate_choice(model: str | None) -> str | None:
    """None / "" / "auto" = server default. Anything else must be selectable, else ValueError."""
    if not model or model == "auto":
        return None
    if model not in {m["id"] for m in selectable()}:
        raise ValueError(f"Model '{model}' is not available. Choose one of: "
                         + ", ".join(m["id"] for m in selectable()))
    return model


def model_for(stage: str) -> str:
    chosen = _override.get()
    if chosen:
        return chosen
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