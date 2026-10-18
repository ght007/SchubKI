"""FastAPI app: routers, static frontend, startup checks.

Run:  uvicorn backend.app.main:app --reload --port 8000     then open http://localhost:8000
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import assess, runs, sources
from .config import settings
from .kb import store
from .llm import models

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("afs")

app = FastAPI(title="AFS In-line Spectroscopy Assessment Assistant", version="1.0")
app.include_router(assess.router)
app.include_router(sources.router)
app.include_router(runs.router)


@app.on_event("startup")
def startup() -> None:
    if store.kb_size() == 0:
        log.info("Knowledge base empty: running ingest (first start only)")
        from .kb import ingest
        log.info("Ingest: %s", ingest.run())
    status = models.check()
    log.info("LLM mock=%s key=%s models=%s", settings.llm_mock, bool(settings.groq_api_key), status)


@app.middleware("http")
async def no_cache_frontend(request, call_next):
    """Never let the browser cache the page or its JavaScript/CSS: after a code update,
    a normal reload must show the new version (ES modules are otherwise cached aggressively)."""
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


app.mount("/static", StaticFiles(directory=settings.frontend_dir), name="static")


@app.get("/")
def index():
    return FileResponse(settings.frontend_dir / "index.html")