"""Accounts API: /api/auth/* (sign-up, login, Google, logout, me) and /api/me/* (history, projects).

Login is optional: every other endpoint keeps working for guests. The session lives in an HttpOnly,
SameSite=Lax cookie; the database stores only its SHA-256 hash.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from ..auth import db, plans, service
from ..auth.security import AuthError
from ..config import settings

router = APIRouter(prefix="/api")
COOKIE = "afs_session"


# ------------------------------------------------------------------ helpers used by other routers
def current_user(request: Request) -> dict | None:
    """The logged-in user, or None for a guest. Never raises: a broken accounts store must not block runs."""
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    try:
        return service.user_for_token(token)
    except Exception:  # noqa: BLE001
        return None


def require_user(request: Request) -> dict:
    user = current_user(request)
    if not user:
        raise HTTPException(401, "Not logged in")
    return user


def _ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "")


def _secure(request: Request) -> bool:
    return request.url.scheme == "https" or request.headers.get("x-forwarded-proto", "") == "https"


def _start_session(request: Request, response: Response, user: dict, method: str) -> dict:
    token = service.create_session(user["id"], method, request.headers.get("user-agent", ""), _ip(request))
    response.set_cookie(COOKIE, token, max_age=settings.session_days * 86400, httponly=True,
                        samesite="lax", secure=_secure(request), path="/")
    return {"user": service.public_user(user)}


def _fail(exc: AuthError):
    raise HTTPException(exc.status, str(exc))


# ------------------------------------------------------------------ /api/auth
@router.get("/auth/config")
def auth_config():
    return {"google_client_id": settings.google_client_ids[0] if settings.google_client_ids else "",
            "google_enabled": bool(settings.google_client_ids), "session_days": settings.session_days,
            "auth_required": settings.auth_required}


class SignupBody(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=256)
    name: str = Field("", max_length=120)
    username: str = Field("", max_length=32)


@router.post("/auth/signup")
def signup(body: SignupBody, request: Request, response: Response):
    try:
        user = service.signup(body.email, body.password, body.name, body.username)
        user = service.login(user["email"], body.password, _ip(request))
    except AuthError as exc:
        _fail(exc)
    return _start_session(request, response, user, "password")


class LoginBody(BaseModel):
    identifier: str = Field(max_length=254, description="E-mail or username")
    password: str = Field(max_length=256)


@router.post("/auth/login")
def login(body: LoginBody, request: Request, response: Response):
    try:
        user = service.login(body.identifier, body.password, _ip(request))
    except AuthError as exc:
        _fail(exc)
    return _start_session(request, response, user, "password")


class GoogleBody(BaseModel):
    credential: str = Field(max_length=4096)


@router.post("/auth/google")
def google(body: GoogleBody, request: Request, response: Response):
    try:
        user = service.google_login(body.credential)
    except AuthError as exc:
        _fail(exc)
    return _start_session(request, response, user, "google")


@router.post("/auth/logout")
def logout(request: Request, response: Response, everywhere: bool = False):
    token = request.cookies.get(COOKIE)
    user = current_user(request)
    if everywhere and user:
        service.logout_everywhere(user["id"])
    else:
        service.logout(token)
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@router.get("/auth/me")
def me(request: Request):
    user = current_user(request)
    if not user:
        return {"user": None}
    return {"user": service.public_user(user), "stats": service.stats(user["id"]), "storage": db.backend()}


class ProfileBody(BaseModel):
    name: str | None = Field(None, max_length=120)
    username: str | None = Field(None, max_length=32)


@router.patch("/auth/me")
def update_me(body: ProfileBody, request: Request):
    user = require_user(request)
    try:
        return {"user": service.public_user(service.update_profile(user, body.name, body.username))}
    except AuthError as exc:
        _fail(exc)


# ------------------------------------------------------------------ /api/me (per-user data)
class QueryBody(BaseModel):
    id: str | None = Field(None, max_length=64)
    enquiry: str = Field(max_length=6000)
    mode: str = "fast"
    modelChoice: str = "auto"
    paths: list[str] = []
    view: str | None = None
    projectId: str | None = Field(None, max_length=64)


@router.get("/me/queries")
def my_queries(request: Request, limit: int = 100):
    return service.list_queries(require_user(request)["id"], min(max(limit, 1), 500))


@router.post("/me/queries")
def save_my_query(body: QueryBody, request: Request):
    user = require_user(request)
    try:
        return service.save_query(user["id"], body.model_dump())
    except AuthError as exc:
        _fail(exc)


@router.delete("/me/queries/{query_id}")
def delete_my_query(query_id: str, request: Request):
    service.delete_query(require_user(request)["id"], query_id)
    return {"ok": True}


@router.get("/me/runs")
def my_runs(request: Request, view: str | None = None, limit: int = 50):
    return service.list_runs(require_user(request)["id"], view, min(max(limit, 1), 500))


class ProjectBody(BaseModel):
    title: str = Field(max_length=120)
    description: str = Field("", max_length=1000)


@router.get("/me/projects")
def my_projects(request: Request):
    return service.list_projects(require_user(request)["id"])


@router.post("/me/projects")
def create_my_project(body: ProjectBody, request: Request):
    try:
        return service.create_project(require_user(request)["id"], body.title, body.description)
    except AuthError as exc:
        _fail(exc)


# ------------------------------------------------------------------ /api/billing (plans; payments come later)
@router.get("/billing/plans")
def billing_plans(request: Request):
    user = current_user(request)
    return {**plans.public(), "current": plans.tier_of(user) if user else None}


class CheckoutBody(BaseModel):
    plan: str = Field(max_length=20)


@router.post("/billing/checkout")
def checkout(body: CheckoutBody, request: Request):
    """Start a subscription. Payment provider goes here later: create a hosted checkout session and return
    {"status": "redirect", "checkout_url": ...}; its webhook then calls service.set_plan()."""
    user = require_user(request)
    if not plans.plan(body.plan):
        raise HTTPException(404, "Unknown plan")
    if settings.billing_mode != "demo":
        raise HTTPException(503, "Payments are not connected yet. Your plan has not been changed.")
    if plans.tier_of(user) == body.plan:
        return {"status": "unchanged", "plan": body.plan, "demo": True, "user": service.public_user(user)}
    user = service.set_plan(user, body.plan)
    return {"status": "active", "plan": body.plan, "demo": True, "user": service.public_user(user)}
