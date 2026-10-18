"""Knowledge-base editor API (Knowledge base page). Pro users only, unless KB_EDIT says otherwise.

GET    /api/kb/files                         editable files and uploaded documents, rebuild status
GET    /api/kb/files/{area}/{name}           file text (area "kb") or size (area "raw")
POST   /api/kb/files/kb/{name}/preview       checks + diff, nothing saved
PUT    /api/kb/files/kb/{name}               checked save -> new version -> rebuild + publish
GET    /api/kb/files/{area}/{name}/history   versions (author, time, comment)
POST   /api/kb/files/{area}/{name}/restore   restore a version (saved as a new version)
POST   /api/kb/upload                        upload a document (base64 JSON; no multipart dependency)
POST   /api/kb/sources                       register an uploaded document in sources.json
GET    /api/kb/status                        rebuild / publish progress
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..auth import plans
from ..config import settings
from ..kb import files
from .auth import current_user

router = APIRouter(prefix="/api/kb")


def _editor(request: Request) -> str:
    """Who is editing. KB_EDIT=pro (default): logged-in Pro users; open: anyone (local demo); off: nobody."""
    mode = settings.kb_edit
    if mode == "off":
        raise HTTPException(403, "Knowledge-base editing is switched off (KB_EDIT=off)")
    user = current_user(request)
    if mode == "open":
        return (user or {}).get("email") or "guest"
    if not user:
        raise HTTPException(401, "Log in to edit the knowledge base")
    if not plans.can_view(user, "expert"):
        raise HTTPException(403, "Editing the knowledge base is part of the Pro plan")
    return user.get("email") or user.get("username") or user["id"]


def _call(fn, *args):
    try:
        return fn(*args)
    except files.KBError as exc:
        raise HTTPException(exc.status, {"message": str(exc), "problems": exc.problems}) from exc


class TextBody(BaseModel):
    text: str
    comment: str = ""
    base_sha: str | None = None


class UploadBody(BaseModel):
    filename: str
    content_b64: str
    comment: str = ""


class SourceBody(BaseModel):
    id: str | None = None
    file: str
    title: str
    type: str = ""
    scope: str = ""
    evidence_level: str
    notes: str = ""


class RestoreBody(BaseModel):
    version: int


@router.get("/files")
def list_files(request: Request):
    _editor(request)
    return files.list_files()


@router.get("/status")
def rebuild_status(request: Request):
    _editor(request)
    return files.status()


@router.get("/files/{area}/{name}")
def read_file(area: str, name: str, request: Request):
    _editor(request)
    return _call(files.read, area, name)


@router.post("/files/kb/{name}/preview")
def preview(name: str, body: TextBody, request: Request):
    _editor(request)
    return _call(files.preview, name, body.text)


@router.put("/files/kb/{name}")
def save(name: str, body: TextBody, request: Request):
    who = _editor(request)
    return _call(files.save_kb, name, body.text, who, body.comment, body.base_sha)


@router.get("/files/{area}/{name}/history")
def history(area: str, name: str, request: Request):
    _editor(request)
    return _call(files.history, area, name)


@router.post("/files/{area}/{name}/restore")
def restore(area: str, name: str, body: RestoreBody, request: Request):
    who = _editor(request)
    return _call(files.restore, area, name, body.version, who)


@router.post("/upload")
def upload(body: UploadBody, request: Request):
    who = _editor(request)
    return _call(files.upload_raw, body.filename, body.content_b64, who, body.comment)


@router.post("/sources")
def register(body: SourceBody, request: Request):
    who = _editor(request)
    return _call(files.register_source, body.model_dump(), who)
