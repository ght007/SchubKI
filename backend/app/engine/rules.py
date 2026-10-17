"""Stage 2: deterministic rules from rules.yaml.

Each rule is general domain knowledge with sources. This module only evaluates the
small condition language documented at the top of data/kb/rules.yaml.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml

from ..config import settings
from ..schemas import PathHint, Requirements, RuleHit, RuleQuestion, SourceRef

_UNKNOWN = (None, "", "unknown", [])


@lru_cache(maxsize=1)
def load_rules() -> list[dict]:
    return yaml.safe_load((settings.kb_dir / "rules.yaml").read_text(encoding="utf-8"))["rules"]


def build_context(req: Requirements, enquiry: str, answers: dict[str, str] | None = None) -> dict[str, Any]:
    ctx: dict[str, Any] = req.model_dump()
    ctx["premise_kinds"] = sorted({p.kind for p in req.premises})
    from .paths import general_answers
    answer_text = " ".join(f"{k}: {v}" for k, v in general_answers(answers).items())
    from .glossary import expand
    ctx["text"] = expand(" ".join([enquiry, answer_text, req.summary, " ".join(req.target_variables), req.matrix,
                                   " ".join(req.existing_assets)])).lower()
    return ctx


def _as_text(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(v) for v in value).lower()
    return str(value or "").lower()


def _test(cond: dict, ctx: dict) -> bool:
    if "all" in cond:
        return all(_test(c, ctx) for c in cond["all"])
    if "any" in cond:
        return any(_test(c, ctx) for c in cond["any"])
    value = ctx.get(cond["field"])
    if "eq" in cond:
        return value == cond["eq"]
    if "in" in cond:
        return value in cond["in"]
    if "not_in" in cond:
        return value not in cond["not_in"]
    if "contains" in cond:
        return isinstance(value, list) and cond["contains"] in value
    if "text_any" in cond:
        text = _as_text(value)
        return any(k.lower() in text for k in cond["text_any"])
    if "min_items" in cond:
        return isinstance(value, list) and len(value) >= cond["min_items"]
    if "known" in cond:
        is_known = value not in _UNKNOWN
        return is_known == cond["known"]
    raise ValueError(f"Unknown condition: {cond}")


def evaluate(req: Requirements, enquiry: str, answers: dict[str, str] | None = None) -> list[RuleHit]:
    ctx = build_context(req, enquiry, answers)
    hits: list[RuleHit] = []
    for rule in load_rules():
        if not _test(rule["when"], ctx):
            continue
        flag = rule.get("flag") or {}
        q = rule.get("question")
        hits.append(RuleHit(
            rule_id=rule["id"], title=rule["title"],
            severity=flag.get("severity", "info"), text=flag.get("text", ""),
            scores=rule.get("scores") or {},
            question=RuleQuestion(**q) if q else None,
            cap_confidence=rule.get("cap_confidence"),
            status_hint=rule.get("status_hint"),
            plan=rule.get("plan") or [],
            paths=[PathHint(**p) for p in rule.get("paths", [])],
            sources=[SourceRef(**s) for s in rule.get("sources", [])],
        ))
    order = {"block": 0, "warn": 1, "info": 2}
    hits.sort(key=lambda h: order[h.severity])
    return hits