"""Runs list/detail, markdown export, feedback, trace, examples, health."""
from __future__ import annotations

import json

import yaml
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from ..config import settings
from ..kb import embed, store
from ..llm import models
from ..render.markdown import render_full
from ..schemas import RunResult

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    stats = store.get_meta("ingest_stats", "{}")
    return {"ok": store.kb_size() > 0, "kb_records": store.kb_size(), "ingest": json.loads(stats or "{}"),
            "embed_backend": store.get_meta("embed_backend", embed.backend()),
            "mock": settings.llm_mock, "has_key": bool(settings.groq_api_key),
            "models": {"fast": settings.model_fast, "main": settings.model_main,
                       "council": models.council_models()}, "model_status": models.status()}


@router.get("/kb/summary")
def kb_summary():
    claims = [json.loads(line) for line in (settings.kb_dir / "claims.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    rules = yaml.safe_load((settings.kb_dir / "rules.yaml").read_text(encoding="utf-8"))["rules"]
    return {"claims": len(claims), "rules": len(rules),
            "rules_list": [{"id": r["id"], "title": r["title"],
                            "sources": [f"{s['source']} p.{s['page']}" for s in r["sources"]]} for r in rules]}


@router.get("/examples")
def examples():
    """Scenarios for the UI loader. Our own adversarial cases (A01-A07) are development-only:
    they are hidden unless SHOW_DEV_CASES=1 is set in .env."""
    import os
    sets = [("final_cases.yaml", "Final (H)"), ("dev_cases.yaml", "Development (D)")]
    if os.getenv("SHOW_DEV_CASES", "0") == "1":
        sets.append(("adversarial_cases.yaml", "Adversarial (A, our own)"))
    out = []
    for name, group in sets:
        path = settings.kb_dir.parent.parent / "eval" / "cases" / name
        if path.exists():
            for c in yaml.safe_load(path.read_text(encoding="utf-8"))["cases"]:
                out.append({"id": c["id"], "title": c["title"], "enquiry": " ".join(c["enquiry"].split()), "group": group})
    return out


@router.get("/runs")
def runs(limit: int = 50):
    return store.list_runs(limit)


@router.get("/runs/{run_id}")
def run_detail(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return run


@router.get("/runs/{run_id}/export.md", response_class=PlainTextResponse)
def export_md(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return PlainTextResponse(render_full(RunResult.model_validate(run)), media_type="text/markdown",
                             headers={"Content-Disposition": f'attachment; filename="assessment_{run_id}.md"'})


@router.get("/runs/{run_id}/trace")
def trace(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return {"trace": run.get("trace", []), "timings_ms": run.get("timings_ms", {}), "retrieval": run.get("retrieval", {})}


class Feedback(BaseModel):
    run_id: str
    target: str
    verdict: str
    comment: str = ""


@router.post("/feedback")
def feedback(body: Feedback):
    return {"id": store.add_feedback(body.run_id, body.target, body.verdict, body.comment)}


@router.get("/feedback")
def list_feedback(run_id: str | None = None):
    return store.list_feedback(run_id)