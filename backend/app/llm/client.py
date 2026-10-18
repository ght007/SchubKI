"""Groq client: JSON schema, validation+retry, 429 backoff, cache, mock.

Every LLM call in the app goes through `complete_json`. It
  * asks for structured output (json_schema; falls back to json_object per model),
  * validates the reply with Pydantic and retries once with the validation error,
  * waits and retries on HTTP 429 using Groq's retry-after header,
  * caches replies in SQLite by a hash of (model, messages, schema),
  * records a TraceItem (tokens, latency, cache hit) for the Trace tab,
  * uses the caller's `fallback` if the model fails and records that in the trace;
    cancellation propagates to the pipeline without a retry or fallback.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
import time
from typing import Callable, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from ..config import settings
from ..cancellation import RunCancelled, check_cancelled, wait_for_retry
from ..kb import store
from ..schemas import TraceItem

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

_client = None
_lock = threading.Lock()
_json_object_only: set[str] = set()      # models that rejected json_schema
_no_extra_params: set[str] = set()       # models that rejected reasoning params


class LLMUnavailable(Exception):
    pass


def _get_client():
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise LLMUnavailable("GROQ_API_KEY is not set")
        from openai import OpenAI

        _client = OpenAI(api_key=settings.groq_api_key, base_url=settings.groq_base_url,
                         timeout=settings.llm_timeout_s, max_retries=0)
    return _client


def _extra_params(model: str) -> dict:
    if model in _no_extra_params:
        return {}
    m = model.lower()
    if "gpt-oss" in m:
        return {"reasoning_effort": "low", "include_reasoning": False}
    if "qwen" in m:
        return {"reasoning_format": "hidden"}
    return {}


def _strip(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S).strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.S)
    if m:
        text = m.group(1).strip()
    if not text.startswith("{"):
        i, j = text.find("{"), text.rfind("}")
        if i != -1 and j > i:
            text = text[i:j + 1]
    return text


def _schema_hint(schema: Type[BaseModel]) -> str:
    return json.dumps(schema.model_json_schema(), separators=(",", ":"))


def _retry_after(exc) -> float:
    try:
        headers = exc.response.headers
        for h in ("retry-after", "x-ratelimit-reset-tokens", "x-ratelimit-reset-requests"):
            v = headers.get(h)
            if v:
                m = re.match(r"([\d.]+)(ms|s|m)?", v)
                if m:
                    val = float(m.group(1))
                    return val / 1000 if m.group(2) == "ms" else val * 60 if m.group(2) == "m" else val
    except Exception:
        pass
    return 6.0


def _call(model: str, messages: list[dict], schema: Type[BaseModel], max_tokens: int,
          temperature: float) -> tuple[str, dict]:
    client = _get_client()
    use_schema = model not in _json_object_only
    shrunk = False
    for attempt in range(settings.llm_max_retries + 1):
        check_cancelled()
        if use_schema:
            # the schema travels in response_format; do not pay for it twice in the prompt
            msgs = messages
            fmt = {"type": "json_schema", "json_schema": {
                "name": schema.__name__, "schema": schema.model_json_schema(), "strict": False}}
        else:
            msgs = [{"role": "system", "content": messages[0]["content"] + "\n\nThe JSON object must match this "
                     f"JSON schema:\n{_schema_hint(schema)}"}] + messages[1:]
            fmt = {"type": "json_object"}
        kwargs = dict(model=model, messages=msgs, temperature=temperature, max_tokens=max_tokens,
                      response_format=fmt)
        extra = _extra_params(model)
        if extra:
            kwargs["extra_body"] = extra
        try:
            resp = client.chat.completions.create(**kwargs)
            check_cancelled()
            usage = {"prompt_tokens": getattr(resp.usage, "prompt_tokens", 0),
                     "completion_tokens": getattr(resp.usage, "completion_tokens", 0)}
            return resp.choices[0].message.content or "", usage
        except RunCancelled:
            raise
        except Exception as exc:  # openai.* errors
            check_cancelled()
            status = getattr(exc, "status_code", None)
            msg = str(exc).lower()
            if status == 413 and not shrunk:
                # Groq counts prompt + max_tokens against the per-minute limit. If one request is
                # larger than the whole limit, retry once with a smaller output budget.
                m = re.search(r"limit (\d+), requested (\d+)", msg)
                if m:
                    limit, requested = int(m.group(1)), int(m.group(2))
                    new_max = max_tokens - (requested - limit) - 300
                    if new_max >= 900:
                        log.warning("413 from %s: max_tokens %d -> %d", model, max_tokens, new_max)
                        max_tokens, shrunk = new_max, True
                        continue
                raise
            if status == 429:
                wait = min(_retry_after(exc) + 0.5, 30)
                log.warning("429 from %s, waiting %.1fs", model, wait)
                wait_for_retry(wait)
                continue
            if status == 400 and use_schema and ("response_format" in msg or "json_schema" in msg or "schema" in msg):
                _json_object_only.add(model)
                use_schema = False
                continue
            if status == 400 and extra and ("reasoning" in msg or "include_reasoning" in msg or "unsupported" in msg):
                _no_extra_params.add(model)
                continue
            if status == 400 and "json_validate_failed" in msg and use_schema:
                _json_object_only.add(model)
                use_schema = False
                continue
            if status in (500, 502, 503, 504) or status is None:
                wait_for_retry(2 * (attempt + 1))
                if attempt < settings.llm_max_retries:
                    continue
            raise
    raise LLMUnavailable(f"{model}: retries exhausted")


def complete_json(stage: str, model: str, system: str, user: str, schema: Type[T],
                  trace: list[TraceItem], fallback: Optional[Callable[[], T]] = None,
                  max_tokens: int = 2500, temperature: float = 0.2) -> T | None:
    """Return a validated `schema` instance, or fallback() / None if the model fails."""
    check_cancelled()
    system_full = f"{system}\n\nReturn ONLY one JSON object (no prose, no markdown)."
    messages = [{"role": "system", "content": system_full}, {"role": "user", "content": user}]
    key = hashlib.sha256(json.dumps([model, messages, schema.__name__]).encode()).hexdigest()
    t0 = time.time()
    item = TraceItem(stage=stage, model=model)

    def done(result, ok=True, error="", cached=False, usage=None):
        check_cancelled()
        item.ok, item.error, item.cached = ok, error[:300], cached
        item.latency_ms = int((time.time() - t0) * 1000)
        if usage:
            item.prompt_tokens = usage.get("prompt_tokens", 0)
            item.completion_tokens = usage.get("completion_tokens", 0)
        trace.append(item)
        return result

    if settings.llm_mock:
        result = fallback() if fallback else None
        item.model = f"mock ({model})"
        return done(result, ok=result is not None, error="" if result else "mock mode, no fallback")

    if settings.llm_cache:
        hit = store.cache_get(key)
        if hit:
            try:
                return done(schema.model_validate_json(hit[0]), cached=True, usage=hit[1])
            except ValidationError:
                pass

    try:
        text, usage = _call(model, messages, schema, max_tokens, temperature)
        cleaned = _strip(text)
        try:
            parsed = schema.model_validate_json(cleaned)
        except (ValidationError, ValueError) as err:
            # one repair round with the exact validation error
            messages2 = messages + [{"role": "assistant", "content": text[:6000]},
                                    {"role": "user", "content": f"Your JSON did not validate: {str(err)[:1500]}\n"
                                                                f"Return the corrected JSON object only."}]
            text, usage2 = _call(model, messages2, schema, max_tokens, temperature)
            usage = {k: usage.get(k, 0) + usage2.get(k, 0) for k in ("prompt_tokens", "completion_tokens")}
            cleaned = _strip(text)
            parsed = schema.model_validate_json(cleaned)
        if settings.llm_cache:
            store.cache_put(key, model, parsed.model_dump_json(), usage)
        return done(parsed, usage=usage)
    except RunCancelled:
        raise
    except Exception as exc:
        check_cancelled()
        log.warning("LLM stage %s failed on %s: %s", stage, model, exc)
        result = fallback() if fallback else None
        if result is not None:
            item.model = f"{model} -> rule fallback"
        return done(result, ok=False, error=str(exc))


def available_models() -> list[str]:
    try:
        return sorted(m.id for m in _get_client().models.list().data)
    except Exception as exc:
        log.warning("could not list models: %s", exc)
        return []
