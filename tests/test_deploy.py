"""Hosting config (render.yaml, frontend/vercel.json, scripts/fetch_sources.py) stays consistent with the app."""
from __future__ import annotations

import importlib.util
import io
import json
import re
import zipfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

_SPEC = importlib.util.spec_from_file_location("fetch_sources", ROOT / "scripts" / "fetch_sources.py")
fetch = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(fetch)


def _vercel() -> dict:
    return json.loads((FRONTEND / "vercel.json").read_text(encoding="utf-8"))


def _render_service() -> dict:
    return yaml.safe_load((ROOT / "render.yaml").read_text(encoding="utf-8"))["services"][0]


# ------------------------------------------------------------------ Vercel
def test_vercel_proxies_api_to_an_https_backend():
    api = [r for r in _vercel()["rewrites"] if r["source"] == "/api/:path*"]
    assert len(api) == 1
    assert re.fullmatch(r"https://[\w.-]+/api/:path\*", api[0]["destination"])


def _server_pages() -> dict[str, str]:
    """{route: html file} for every page route in backend/app/main.py (except "/", which redirects)."""
    src = (ROOT / "backend" / "app" / "main.py").read_text(encoding="utf-8")
    pages = {}
    for block in re.split(r"\n(?=@app\.)", src):
        route = re.match(r'@app\.get\("(/[^"]*)"', block)
        html = re.findall(r'frontend_dir / "([\w-]+\.html)"', block)
        if route and html and route.group(1) != "/":
            pages[route.group(1)] = html[-1]
    return pages


def test_server_page_routes_are_found():
    assert {"/app", "/login", "/pricing"} <= set(_server_pages())


def test_vercel_serves_every_page_route_of_the_server():
    rewrites = {r["source"]: r["destination"] for r in _vercel()["rewrites"]}
    for route, html in _server_pages().items():
        assert rewrites.get(route) == f"/{html}", f"frontend/vercel.json has no rewrite {route} -> /{html}"
        assert (FRONTEND / html).is_file(), f"{route} -> {html} does not exist"
    assert rewrites["/static/:path*"] == "/:path*"
    assert {"source": "/", "destination": "/login", "permanent": False} in _vercel()["redirects"]


def test_every_static_reference_in_the_pages_exists():
    for page in FRONTEND.glob("*.html"):
        for ref in re.findall(r'(?:src|href)="/static/([^"]+)"', page.read_text(encoding="utf-8")):
            assert (FRONTEND / ref).is_file(), f"{page.name} refers to /static/{ref}"


def test_api_responses_are_never_cached_by_the_cdn():
    rules = {h["source"]: {x["key"]: x["value"] for x in h["headers"]} for h in _vercel()["headers"]}
    assert rules["/api/(.*)"]["x-vercel-enable-rewrite-caching"] == "0"


# ------------------------------------------------------------------ Render
def test_render_starts_the_app_on_the_given_port_behind_the_proxy():
    svc = _render_service()
    assert "backend.app.main:app" in svc["startCommand"] and "$PORT" in svc["startCommand"]
    assert "--proxy-headers" in svc["startCommand"]          # secure session cookie behind HTTPS proxies
    assert svc["healthCheckPath"] == "/api/live"


def test_render_build_fetches_sources_before_ingest():
    build = _render_service()["buildCommand"]
    assert build.index("scripts/fetch_sources.py") < build.index("backend.app.kb.ingest")


def test_render_keeps_secrets_out_of_the_file():
    env = {e["key"]: e for e in _render_service()["envVars"]}
    for key in ("GROQ_API_KEY", "SUPABASE_DB_URL", "SOURCES_URL", "GOOGLE_CLIENT_ID"):
        assert env[key] == {"key": key, "sync": False}


def test_liveness_probe_needs_no_database():
    from backend.app.main import live
    assert live() == {"ok": True}


# ------------------------------------------------------------------ fetch_sources
def _zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()


def test_required_sources_are_the_supplied_and_cited_pdfs():
    reg = fetch.registered()
    assert all(name.lower().endswith(".pdf") for name in reg.values())
    need = fetch.required()
    for sid in fetch.SUPPLIED | fetch.cited_sources():
        if sid in reg:
            assert reg[sid] in need
    assert len([s for s in fetch.SUPPLIED if s in reg]) == 5


def test_uploaded_documents_are_optional_for_the_build():
    # documents added on the Knowledge base page come from Supabase at startup, not from the zip
    assert not set(fetch.required()) & set(fetch.optional())
    assert set(fetch.required()) | set(fetch.optional()) == set(fetch.registered().values())


def test_extract_takes_wanted_files_by_name_only(tmp_path):
    data = _zip({"sources/S01_Multispectral_Laboratory.pdf": b"%PDF-1",
                 "../S05_AFS_Flyer.pdf": b"%PDF-5",          # path in the archive is ignored (no zip-slip)
                 "notes.txt": b"not wanted"})
    got = fetch.extract(data, tmp_path / "raw", ["S01_Multispectral_Laboratory.pdf", "S05_AFS_Flyer.pdf"])
    assert got == ["S01_Multispectral_Laboratory.pdf", "S05_AFS_Flyer.pdf"]
    assert sorted(p.name for p in (tmp_path / "raw").iterdir()) == got
    assert not (tmp_path / "S05_AFS_Flyer.pdf").exists()


def test_extract_rejects_a_non_zip_download(tmp_path):
    with pytest.raises(ValueError):
        fetch.extract(b"<html>signed URL expired</html>", tmp_path, ["S01_Multispectral_Laboratory.pdf"])


def test_missing_reports_absent_and_empty_files(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"x")
    (tmp_path / "b.pdf").write_bytes(b"")
    assert fetch.missing(tmp_path, ["a.pdf", "b.pdf", "c.pdf"]) == ["b.pdf", "c.pdf"]
