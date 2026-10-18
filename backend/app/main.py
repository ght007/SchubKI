"""FastAPI app: routers, static frontend, startup checks.

Run:  uvicorn backend.app.main:app --reload --port 8000     then open http://localhost:8000
"""
from __future__ import annotations

import logging

from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .api import assess, auth, runs, sources
from .config import settings
from .kb import store
from .llm import models

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("afs")

app = FastAPI(title="AFS In-line Spectroscopy Assessment Assistant", version="1.0")
app.include_router(assess.router)
app.include_router(sources.router)
app.include_router(runs.router)
app.include_router(auth.router)


@app.on_event("startup")
def startup() -> None:
    if store.local_kb_size() == 0:      # the local index is also the offline fallback, so it must exist
        log.info("Knowledge base empty: running ingest (first start only)")
        from .kb import ingest
        log.info("Ingest: %s", ingest.run())
    log.info("Database: %s", store.db_status().get("detail"))
    store.schedule_sync(startup=True)   # publish the knowledge base if needed, upload local-only rows
    status = models.check()
    log.info("LLM mock=%s key=%s models=%s", settings.llm_mock, bool(settings.groq_api_key), status)


@app.middleware("http")
async def no_cache_frontend(request, call_next):
    """Never let the browser cache the page or its JavaScript/CSS: after a code update,
    a normal reload must show the new version (ES modules are otherwise cached aggressively)."""
    response = await call_next(request)
    if request.url.path in ("/", "/app", "/login", "/pricing") or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


app.mount("/static", StaticFiles(directory=settings.frontend_dir), name="static")


# Pages. With AUTH_REQUIRED=1 (default): / opens the login page, the assistant lives at /app and needs a
# session, /login forwards signed-in users to the app, /pricing is public. AUTH_REQUIRED=0 restores the
# open guest app at / (fallback for an offline demo).
def _safe_next(target: str | None) -> str:
    return target if target and target.startswith("/") and not target.startswith("//") else "/app"


@app.get("/")
def index():
    if not settings.auth_required:
        return FileResponse(settings.frontend_dir / "index.html")
    return RedirectResponse("/login", status_code=307)


@app.get("/app")
def assistant(request: Request):
    if settings.auth_required and not auth.current_user(request):
        return RedirectResponse(f"/login?next={quote('/app')}", status_code=307)
    return FileResponse(settings.frontend_dir / "index.html")


@app.get("/login")
def login_page(request: Request, next: str | None = None):  # noqa: A002  (query parameter name)
    if auth.current_user(request):
        return RedirectResponse(_safe_next(next), status_code=307)
    return FileResponse(settings.frontend_dir / "login.html")


@app.get("/pricing")
def pricing_page():
    return FileResponse(settings.frontend_dir / "pricing.html")