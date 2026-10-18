"""The assessment in the team's 11-section output format (frontend: assessment-outline.js).

One builder, three consumers: the Result Assessment page, the Markdown export and the H01-H06 output
files. It only REORGANISES what the pipeline produced (report, premises, confidence, verification, paths,
requirements); it never writes new claims, so every statement keeps its kind, citations and verifier
status. The original report fields stay in the run unchanged (docs/frontend-integration.md, "Data retention").

Section keys, titles and order must match frontend/js/components/assessment-outline.js.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from ..config import settings
from ..schemas import RunResult, Statement

VERSION = 1
SECTIONS = [
    ("decision_status", "Decision Status"),
    ("requirements_stated", "Requirements stated"),
    ("key_unknowns", "Key unknowns"),
    ("clarification_questions", "Clarification questions"),
    ("recommendation", "Recommendation"),
    ("measurement_concept", "Measurement concept"),
    ("spectral_range", "Spectral range"),
    ("risks_and_uncertainty", "Risks and uncertainty"),
    ("decision_basis", "Decision basis"),
    ("sources", "Sources"),
    ("first_feasibility_experiment_prototype", "First feasibility experiment prototype"),
]
STATUS_LABEL = {"provisional_assessment": "Provisional assessment",
                "insufficient_information": "Insufficient information",
                "outside_supported_scope": "Outside the supported scope"}
PATH_TITLES = {"A": "Chemometric model for process automation", "B": "Multi-spectral system for your R&D lab",
               "C": "Low-cost spectral sensors"}
ROLE_ORDER = {"primary": 0, "comparison": 1, "conditional": 2}


@lru_cache(maxsize=1)
def _sources() -> dict[str, dict]:
    try:
        data = json.loads((settings.kb_dir / "sources.json").read_text(encoding="utf-8"))
        return {s["id"]: s for s in data.get("sources", [])}
    except (OSError, ValueError):
        return {}


def _checks(run: RunResult) -> dict[str, str]:
    return {c.location: c.status for c in (run.verification.claims if run.verification else [])}


def _stmt(s: Statement, loc: str, checks: dict[str, str]) -> dict:
    return {"text": s.text, "kind": s.kind, "check": checks.get(loc, "unchecked"),
            "citations": [c.model_dump() for c in s.citations]}


def _stmts(items: list[Statement], name: str, checks: dict[str, str]) -> list[dict]:
    return [_stmt(s, f"{name}[{i}]", checks) for i, s in enumerate(items)]


def _setup(run: RunResult) -> dict:
    """Text form of the project-setup diagram (same rules as frontend project-setup.js)."""
    r = run.report
    paths = [p for p in ("A", "B", "C") if p in (run.preferred_paths or [])]
    recs = sorted([x for x in r.recommendations if x.role in ROLE_ORDER], key=lambda x: ROLE_ORDER[x.role])
    targets = (run.requirements.target_variables if run.requirements else []) or []
    systems = []
    for rec in recs:
        methods = rec.method_ids or [rec.method]
        comps = {
            "A": {"title": "Models", "items": [f"{t} calibration" for t in targets] or ["Target calibration"],
                  "output": "Process predictions"},
            "B": {"title": "Lab system", "items": [f"{m} measurement channel" for m in methods]
                  + ["Sample / probe", "Acquisition + reference data"], "output": "Spectra + reference values"},
            "C": {"title": "Sensor system", "items": [f"{m} sensor" for m in methods]
                  + ["Process probe(s)", "Acquisition + control interface"], "output": "Process monitoring"},
        }
        systems.append({"method": rec.method, "role": rec.role, "components": {p: comps[p] for p in paths}})
    return {"paths": paths, "path_titles": {p: PATH_TITLES[p] for p in paths}, "systems": systems}


def build(run: RunResult) -> dict[str, Any]:
    """{'version', 'sections': [{'key', 'title', 'empty', ...content}]} or {} when the run has no report."""
    r = run.report
    if r is None:
        return {}
    checks = _checks(run)
    conf = run.confidence
    fp = r.feasibility_plan
    content: dict[str, dict] = {}

    blocking = [h for h in run.rule_hits if h.severity == "block"]
    content["decision_status"] = {
        "status": r.decision_status, "status_label": STATUS_LABEL.get(r.decision_status, r.decision_status),
        "headline": r.headline,
        "confidence": {"level": conf.level, "raise_with": conf.raise_with} if conf else None,
        "premises": [{"statement": p.statement, "verdict": p.verdict, "explanation": p.explanation,
                      "citations": [c.model_dump() for c in p.citations]} for p in run.premises],
        "blocking": [{"title": h.title, "text": h.text,
                      "sources": [f"{s.source} p.{s.page}" for s in h.sources]} for h in blocking],
    }
    content["requirements_stated"] = {"items": list(r.requirements_stated)}
    content["key_unknowns"] = {"items": list(r.key_unknowns), "assumptions": list(r.assumptions)}
    content["clarification_questions"] = {"items": [q.model_dump() for q in r.clarification_questions]}
    content["recommendation"] = {"items": [
        {"method": rec.method, "method_ids": rec.method_ids, "role": rec.role, "conditions": rec.conditions,
         "rationale": [_stmt(s, f"recommendations[{i}].rationale[{j}]", checks) for j, s in enumerate(rec.rationale)]}
        for i, rec in enumerate(r.recommendations)]}
    content["measurement_concept"] = {"statements": _stmts(r.measurement_concept, "measurement_concept", checks)}
    content["spectral_range"] = {"statements": _stmts(r.spectral_range, "spectral_range", checks)}
    content["risks_and_uncertainty"] = {
        "statements": _stmts(r.risks, "risks", checks),
        "confidence": {"level": conf.level, "caps": conf.caps,
                       "signals": [{"name": s.name, "level": s.level, "detail": s.detail} for s in conf.signals]}
        if conf else None,
    }
    content["decision_basis"] = {"items": list(fp.decision_basis)}

    # sources: every page cited anywhere in the assessment, with its quotes and the verifier's verdict
    found: dict[tuple[str, int], dict] = {}

    def add(c, status: str) -> None:
        key = (c.source, c.page)
        meta = _sources().get(c.source, {})
        entry = found.setdefault(key, {"source": c.source, "page": c.page, "title": meta.get("title", c.source),
                                       "scope": meta.get("evidence_level") or meta.get("scope", ""), "quotes": []})
        if c.quote and all(q["quote"] != c.quote for q in entry["quotes"]):
            entry["quotes"].append({"quote": c.quote, "check": status})

    for i, rec in enumerate(r.recommendations):
        for j, s in enumerate(rec.rationale):
            for c in s.citations:
                add(c, checks.get(f"recommendations[{i}].rationale[{j}]", "unchecked"))
    for name in ("measurement_concept", "spectral_range", "risks"):
        for j, s in enumerate(getattr(r, name)):
            for c in s.citations:
                add(c, checks.get(f"{name}[{j}]", "unchecked"))
    for p in run.premises:
        for c in p.citations:
            add(c, "unchecked")
    content["sources"] = {"items": sorted(found.values(), key=lambda x: (x["source"], x["page"]))}

    paths = run.paths
    content["first_feasibility_experiment_prototype"] = {
        "plan": {"samples": list(fp.samples), "reference": list(fp.reference), "comparison": list(fp.comparison),
                 "steps": list(fp.steps)},
        "pathway": {"next_step": r.pathway.next_step, "likely_path": r.pathway.likely_path, "why": r.pathway.why,
                    "requested": [f.model_dump() for f in paths.requested] if paths else [],
                    "proceed_anyway": [p.model_dump() for p in paths.proceed_anyway] if paths else []},
        "setup": _setup(run),
    }

    def empty(key: str, c: dict) -> bool:
        if key == "decision_status":
            return False
        if key == "first_feasibility_experiment_prototype":
            return not any(c["plan"].values()) and not c["setup"]["systems"]
        return not any(v for v in c.values() if isinstance(v, list))

    return {"version": VERSION,
            "sections": [{"key": k, "title": t, "empty": empty(k, content[k]), **content[k]} for k, t in SECTIONS]}
