"""Accounts logic: sign-up, login (password or Google), sessions, projects, saved queries, run history."""
from __future__ import annotations

import json
import re
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone

from ..config import settings
from . import db, plans
from .security import AuthError, hash_password, new_token, token_id, verify_google, verify_password

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_RE = re.compile(r"^[a-z0-9_.-]{3,32}$")
VIEWS = ("general", "expert")
MAX_FAILS, FAIL_WINDOW_S = 8, 600

_fails: dict[str, list[float]] = {}
_fails_lock = threading.Lock()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_id() -> str:
    return uuid.uuid4().hex


# ------------------------------------------------------------------ brute-force guard (in memory)
def _check_rate(*keys: str) -> None:
    t = time.time()
    with _fails_lock:
        for k in keys:
            recent = [x for x in _fails.get(k, []) if t - x < FAIL_WINDOW_S]
            _fails[k] = recent
            if len(recent) >= MAX_FAILS:
                raise AuthError("Too many failed attempts. Wait a few minutes and try again.", 429)


def _record_fail(*keys: str) -> None:
    with _fails_lock:
        for k in keys:
            _fails.setdefault(k, []).append(time.time())


def _clear_fails(*keys: str) -> None:
    with _fails_lock:
        for k in keys:
            _fails.pop(k, None)


# ------------------------------------------------------------------ users
def public_user(u: dict) -> dict:
    """What the browser may see: never the hash, never the Google subject id."""
    return {"id": u["id"], "email": u["email"], "username": u.get("username"), "name": u.get("name") or "",
            "avatar_url": u.get("avatar_url") or "", "auth_provider": u.get("auth_provider", "local"),
            "has_password": bool(u.get("password_hash")), "subscription_tier": plans.tier_of(u),
            "views": plans.views_for(u),
            "created_at": u.get("created_at"), "last_login_at": u.get("last_login_at"),
            "login_count": int(u.get("login_count") or 0)}


def _norm_email(email: str) -> str:
    e = (email or "").strip().lower()
    if not EMAIL_RE.match(e) or len(e) > 254:
        raise AuthError("Enter a valid e-mail address")
    return e


def _norm_username(username: str) -> str:
    u = (username or "").strip().lower()
    if not USERNAME_RE.match(u):
        raise AuthError("Username: 3-32 characters, letters, digits, '.', '_' or '-'")
    return u


def _free_username(base: str) -> str:
    base = re.sub(r"[^a-z0-9_.-]", "", base.lower())[:24] or "user"
    base = base if len(base) >= 3 else f"{base}user"
    for i in range(0, 50):
        cand = base if i == 0 else f"{base}{i + 1}"
        if not db.one("SELECT id FROM users WHERE username = ?", (cand,)):
            return cand
    return f"{base}{uuid.uuid4().hex[:6]}"


def get_user(user_id: str) -> dict | None:
    return db.one("SELECT * FROM users WHERE id = ?", (user_id,))


def find_user(identifier: str) -> dict | None:
    ident = (identifier or "").strip().lower()
    col = "email" if "@" in ident else "username"
    return db.one(f"SELECT * FROM users WHERE {col} = ?", (ident,))


def _save_user(u: dict) -> None:
    db.upsert("users", u)          # upsert, not update: also copies an offline-created account up


def signup(email: str, password: str, name: str = "", username: str = "") -> dict:
    email = _norm_email(email)
    if not 8 <= len(password or "") <= 256:
        raise AuthError("Password: at least 8 characters")
    uname = _norm_username(username) if username.strip() else _free_username(email.split("@")[0])
    if find_user(email):
        raise AuthError("An account with this e-mail already exists. Log in instead.", 409)
    if db.one("SELECT id FROM users WHERE username = ?", (uname,)):
        raise AuthError("This username is taken", 409)
    t = now()
    u = {"id": _new_id(), "email": email, "username": uname, "name": (name or "").strip()[:120],
         "password_hash": hash_password(password), "auth_provider": "local", "google_sub": None,
         "avatar_url": None, "subscription_tier": plans.DEFAULT_TIER, "subscription_expires_at": None,
         "created_at": t, "updated_at": t, "last_login_at": None, "login_count": 0, "is_active": 1,
         "preferences": "{}"}
    try:
        _save_user(u)
    except db.Duplicate as exc:
        raise AuthError("This e-mail or username is already registered", 409) from exc
    return u


def _mark_login(u: dict) -> dict:
    t = now()
    u = {**u, "last_login_at": t, "updated_at": t, "login_count": int(u.get("login_count") or 0) + 1}
    _save_user(u)
    return u


def login(identifier: str, password: str, ip: str = "") -> dict:
    ident = (identifier or "").strip().lower()
    keys = (f"id:{ident}", f"ip:{ip}") if ip else (f"id:{ident}",)
    _check_rate(*keys)
    u = find_user(ident) if ident else None
    ok = verify_password(password or "", u.get("password_hash") if u else None)
    if not u or not ok:
        _record_fail(*keys)
        if u and not u.get("password_hash"):
            raise AuthError("This account uses Google sign-in. Use 'Continue with Google'.", 401)
        raise AuthError("Wrong e-mail/username or password", 401)
    if not int(u.get("is_active", 1)):
        raise AuthError("This account is disabled", 403)
    _clear_fails(*keys)
    return _mark_login(u)


def google_login(credential: str) -> dict:
    claims = verify_google(credential, settings.google_client_ids)
    sub, email = str(claims["sub"]), str(claims["email"]).lower()
    u = db.one("SELECT * FROM users WHERE google_sub = ?", (sub,)) or find_user(email)
    t = now()
    if u is None:
        u = {"id": _new_id(), "email": email, "username": _free_username(email.split("@")[0]),
             "name": (claims.get("name") or "")[:120], "password_hash": None, "auth_provider": "google",
             "google_sub": sub, "avatar_url": claims.get("picture"), "subscription_tier": plans.DEFAULT_TIER,
             "subscription_expires_at": None, "created_at": t, "updated_at": t, "last_login_at": None,
             "login_count": 0, "is_active": 1, "preferences": "{}"}
    else:
        if u.get("google_sub") and u["google_sub"] != sub:
            raise AuthError("This e-mail is linked to a different Google account", 409)
        # Google verified this e-mail, so linking it to an existing password account is safe
        u = {**u, "google_sub": sub, "avatar_url": u.get("avatar_url") or claims.get("picture"),
             "name": u.get("name") or (claims.get("name") or "")[:120],
             "auth_provider": u["auth_provider"] if u.get("auth_provider") == "google" or not u.get("password_hash")
             else "local+google"}
    if not int(u.get("is_active", 1)):
        raise AuthError("This account is disabled", 403)
    return _mark_login(u)


def update_profile(user: dict, name: str | None = None, username: str | None = None) -> dict:
    u = dict(user)
    if name is not None:
        u["name"] = name.strip()[:120]
    if username is not None and username.strip().lower() != (user.get("username") or ""):
        uname = _norm_username(username)
        if db.one("SELECT id FROM users WHERE username = ?", (uname,)):
            raise AuthError("This username is taken", 409)
        u["username"] = uname
    u["updated_at"] = now()
    _save_user(u)
    return u


def set_plan(user: dict, plan_id: str) -> dict:
    """Switch the user's plan. Called by checkout in demo mode, and later by the payment webhook."""
    if not plans.plan(plan_id):
        raise AuthError("Unknown plan", 404)
    u = {**user, "subscription_tier": plan_id, "updated_at": now()}
    _save_user(u)
    return u


# ------------------------------------------------------------------ sessions
def create_session(user_id: str, method: str, user_agent: str = "", ip: str = "") -> str:
    token = new_token()
    created = datetime.now(timezone.utc)
    db.upsert("user_sessions", {
        "id": token_id(token), "user_id": user_id, "created_at": created.isoformat(timespec="seconds"),
        "expires_at": (created + timedelta(days=settings.session_days)).isoformat(timespec="seconds"),
        "revoked_at": None, "auth_method": method, "user_agent": (user_agent or "")[:300], "ip": (ip or "")[:64]})
    return token


def user_for_token(token: str | None) -> dict | None:
    if not token or len(token) > 200:
        return None
    s = db.one("SELECT * FROM user_sessions WHERE id = ?", (token_id(token),))
    if not s or s.get("revoked_at") or s["expires_at"] < now():
        return None
    u = get_user(s["user_id"])
    return u if u and int(u.get("is_active", 1)) else None


def logout(token: str | None) -> None:
    if token:
        db.write("UPDATE user_sessions SET revoked_at = ? WHERE id = ? AND revoked_at IS NULL", (now(), token_id(token)))


def logout_everywhere(user_id: str) -> None:
    db.write("UPDATE user_sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL", (now(), user_id))


# ------------------------------------------------------------------ projects
def list_projects(user_id: str) -> list[dict]:
    rows = db.query_merged("SELECT id, title, description, created_at, updated_at FROM projects "
                           "WHERE user_id = ? AND archived = 0", (user_id,))
    return sorted(rows, key=lambda r: r["updated_at"], reverse=True)


def create_project(user_id: str, title: str, description: str = "") -> dict:
    title = (title or "").strip()[:120]
    if not title:
        raise AuthError("Project title is required")
    t = now()
    row = {"id": _new_id(), "user_id": user_id, "title": title, "description": (description or "").strip()[:1000],
           "created_at": t, "updated_at": t, "archived": 0}
    db.upsert("projects", row)
    return {k: row[k] for k in ("id", "title", "description", "created_at", "updated_at")}


def _owns_project(user_id: str, project_id: str | None) -> bool:
    return not project_id or bool(db.one("SELECT id FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id)))


# ------------------------------------------------------------------ saved queries (the sidebar)
def _query_out(r: dict) -> dict:
    try:
        paths = json.loads(r.get("paths") or "[]")
    except ValueError:
        paths = []
    return {"id": r["id"], "title": r["title"], "enquiry": r["enquiry"], "mode": r.get("mode") or "fast",
            "modelChoice": r.get("model_choice") or "auto", "paths": paths, "view": r.get("view"),
            "projectId": r.get("project_id"), "lastRunId": r.get("last_run_id"), "lastStatus": r.get("last_status"),
            "createdAt": r["created_at"], "updatedAt": r["updated_at"]}


def list_queries(user_id: str, limit: int = 100) -> list[dict]:
    rows = db.query_merged("SELECT * FROM saved_queries WHERE user_id = ?", (user_id,))
    rows.sort(key=lambda r: r["updated_at"], reverse=True)
    return [_query_out(r) for r in rows[:limit]]


def save_query(user_id: str, draft: dict) -> dict:
    enquiry = (draft.get("enquiry") or "").strip()
    if not enquiry:
        raise AuthError("Empty enquiry")
    qid = str(draft.get("id") or "")[:64] or _new_id()
    existing = db.one("SELECT * FROM saved_queries WHERE id = ?", (qid,))
    if existing and existing["user_id"] != user_id:
        qid, existing = _new_id(), None          # someone else's id: save as a new query, never overwrite
    project_id = draft.get("projectId") or (existing or {}).get("project_id")
    if not _owns_project(user_id, project_id):
        raise AuthError("Unknown project", 404)
    paths = sorted({p for p in (draft.get("paths") or []) if p in ("A", "B", "C")})
    view = draft.get("view") if draft.get("view") in VIEWS else (existing or {}).get("view")
    t = now()
    row = {"id": qid, "user_id": user_id, "project_id": project_id,
           "title": " ".join(enquiry.split())[:72], "enquiry": enquiry[:6000],
           "mode": "council" if draft.get("mode") == "council" else "fast",
           "model_choice": str(draft.get("modelChoice") or "auto")[:40], "paths": json.dumps(paths), "view": view,
           "last_run_id": (existing or {}).get("last_run_id"), "last_status": (existing or {}).get("last_status"),
           "created_at": (existing or {}).get("created_at") or t, "updated_at": t}
    db.upsert("saved_queries", row)
    return _query_out(row)


def delete_query(user_id: str, query_id: str) -> None:
    db.write("DELETE FROM saved_queries WHERE id = ? AND user_id = ?", (query_id, user_id))


# ------------------------------------------------------------------ run history (results per user)
def record_run(user_id: str, run: dict, view: str = "general", query_id: str | None = None) -> None:
    """Link a finished run to its user. The full result stays in the runs table (one copy)."""
    if not run.get("id"):
        return
    view = view if view in VIEWS else "general"
    if not plans.can_view(get_user(user_id), view):
        view = "general"                       # a Basic account cannot log runs as Expert
    status = (run.get("report") or {}).get("decision_status")
    conf = (run.get("confidence") or {}).get("level")
    db.upsert("user_runs", {
        "run_id": run["id"], "user_id": user_id, "query_id": query_id, "parent_run_id": run.get("parent_run_id"),
        "view": view, "mode": run.get("mode"), "title": " ".join((run.get("enquiry") or "").split())[:72],
        "status": status, "confidence": conf, "created_at": run.get("created") or now()}, key="run_id")
    if query_id:
        db.write("UPDATE saved_queries SET last_run_id = ?, last_status = ?, view = ?, updated_at = ? "
                 "WHERE id = ? AND user_id = ?", (run["id"], status, view, now(), query_id, user_id))


def list_runs(user_id: str, view: str | None = None, limit: int = 50) -> list[dict]:
    sql, params = "SELECT * FROM user_runs WHERE user_id = ?", (user_id,)
    if view in VIEWS:
        sql, params = sql + " AND view = ?", (user_id, view)
    rows = db.query_merged(sql, params, key="run_id")
    rows.sort(key=lambda r: r["created_at"], reverse=True)
    return [{"runId": r["run_id"], "queryId": r.get("query_id"), "parentRunId": r.get("parent_run_id"),
             "view": r["view"], "mode": r.get("mode"), "title": r.get("title") or "", "status": r.get("status"),
             "confidence": r.get("confidence"), "createdAt": r["created_at"]} for r in rows[:limit]]


def stats(user_id: str) -> dict:
    return {"queries": len(db.query_merged("SELECT id FROM saved_queries WHERE user_id = ?", (user_id,))),
            "runs": len(db.query_merged("SELECT run_id FROM user_runs WHERE user_id = ?", (user_id,), key="run_id")),
            "projects": len(list_projects(user_id))}
