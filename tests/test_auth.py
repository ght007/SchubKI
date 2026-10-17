"""Accounts: sign-up/login/logout, Google sign-in, per-user saved queries and run history.

Runs on a throwaway SQLite file with Supabase disabled; no network (Google's tokeninfo call is stubbed).
With AUTH_TEST_PG_URL set (a scratch Postgres, e.g. postgresql://postgres@localhost:5433/postgres) every
test also runs with Postgres as the main store and SQLite as the mirror, i.e. the Supabase code path.
"""
from __future__ import annotations

import dataclasses
import os
import sqlite3
import time

import pytest
from fastapi.testclient import TestClient

from backend.app.api import assess as assess_api
from backend.app.api import auth as auth_api
from backend.app.auth import db, plans, security, service
from backend.app.kb import remote, store
from backend.app.main import app
from backend.app.schemas import RunResult

PW = "correct horse battery"


PG_URL = os.getenv("AUTH_TEST_PG_URL", "")


@pytest.fixture(params=["sqlite", "postgres"])
def fresh(request, tmp_path, monkeypatch):
    if request.param == "postgres" and not PG_URL:
        pytest.skip("AUTH_TEST_PG_URL not set")
    con = sqlite3.connect(tmp_path / "auth.db", check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(store.SCHEMA)
    monkeypatch.setattr(store, "_CON", con)
    db.reset_for_tests()
    service._fails.clear()
    remote.reset_for_tests()
    if request.param == "postgres":
        import psycopg
        with psycopg.connect(PG_URL, autocommit=True) as c:
            c.execute("DROP TABLE IF EXISTS " + ", ".join(db.TABLES))
        monkeypatch.setenv("SUPABASE_DB_URL", PG_URL)
        monkeypatch.setenv("DB_BACKEND", "supabase")
        assert db.backend() == "supabase"
    else:
        monkeypatch.setattr(remote, "enabled", lambda: False)
    yield con
    remote.reset_for_tests()


def client() -> TestClient:
    return TestClient(app)          # no `with`: startup (ingest, Supabase sync) is not needed here


def signup(c: TestClient, email="ada@example.com", username="", **kw):
    return c.post("/api/auth/signup", json={"email": email, "password": PW, "name": "Ada", "username": username, **kw})


def test_signup_sets_session_and_stores_only_a_hash(fresh):
    c = client()
    r = signup(c, "Ada@Example.com", "ada")
    assert r.status_code == 200, r.text
    user = r.json()["user"]
    assert user["email"] == "ada@example.com" and user["username"] == "ada"
    assert "password_hash" not in user and user["has_password"] and user["login_count"] == 1
    assert c.cookies.get(auth_api.COOKIE)
    row = fresh.execute("SELECT * FROM users").fetchone()
    assert row["password_hash"].startswith("scrypt$") and PW not in row["password_hash"]
    assert row["last_login_at"] and row["subscription_tier"] == "basic" and user["views"] == ["general"]
    session = fresh.execute("SELECT id FROM user_sessions").fetchone()
    assert session["id"] != c.cookies.get(auth_api.COOKIE)        # only the token's hash is stored
    me = c.get("/api/auth/me").json()
    assert me["user"]["id"] == user["id"] and me["stats"] == {"queries": 0, "runs": 0, "projects": 0}


def test_duplicate_and_invalid_signup(fresh):
    assert signup(client(), username="ada").status_code == 200
    assert signup(client(), "ADA@example.com").status_code == 409
    assert signup(client(), "other@example.com", "ada").status_code == 409
    assert signup(client(), "not-an-email").status_code == 400
    assert client().post("/api/auth/signup", json={"email": "b@example.com", "password": "short"}).status_code == 400


def test_login_logout_and_last_login(fresh):
    signup(client(), username="ada")
    c = client()
    assert c.post("/api/auth/login", json={"identifier": "ada@example.com", "password": "wrong-pass"}).status_code == 401
    r = c.post("/api/auth/login", json={"identifier": "ADA", "password": PW})     # username works too
    assert r.status_code == 200 and r.json()["user"]["login_count"] == 2
    token = c.cookies.get(auth_api.COOKIE)
    assert c.get("/api/auth/me").json()["user"]["username"] == "ada"
    assert c.post("/api/auth/logout").status_code == 200
    assert c.get("/api/auth/me").json()["user"] is None
    replay = client()
    replay.cookies.set(auth_api.COOKIE, token)
    assert replay.get("/api/auth/me").json()["user"] is None                     # revoked server-side
    assert fresh.execute("SELECT revoked_at FROM user_sessions WHERE revoked_at IS NOT NULL").fetchone()


def test_repeated_failures_are_throttled(fresh):
    signup(client())
    c = client()
    for _ in range(service.MAX_FAILS):
        assert c.post("/api/auth/login", json={"identifier": "ada@example.com", "password": "nope-nope"}).status_code == 401
    assert c.post("/api/auth/login", json={"identifier": "ada@example.com", "password": PW}).status_code == 429


def test_expired_session_is_rejected(fresh):
    c = client()
    signup(c)
    db.write("UPDATE user_sessions SET expires_at = ?", ("2000-01-01T00:00:00+00:00",))
    assert c.get("/api/auth/me").json()["user"] is None


class _Resp:
    def __init__(self, status, data):
        self.status_code, self._data = status, data

    def json(self):
        return self._data


def _google(monkeypatch, **claims):
    base = {"aud": "cid.apps.googleusercontent.com", "iss": "https://accounts.google.com", "sub": "g-123",
            "email": "grace@example.com", "email_verified": "true", "name": "Grace H", "picture": "https://p/x.png",
            "exp": str(int(time.time()) + 600)}
    base.update(claims)
    monkeypatch.setattr(security.httpx, "get", lambda *a, **k: _Resp(200, base))
    patched = dataclasses.replace(service.settings, google_client_ids=["cid.apps.googleusercontent.com"])
    monkeypatch.setattr(service, "settings", patched)
    monkeypatch.setattr(auth_api, "settings", patched)


def test_google_sign_in_creates_then_reuses_account(fresh, monkeypatch):
    _google(monkeypatch)
    assert client().get("/api/auth/config").json()["google_enabled"] is True
    c = client()
    r = c.post("/api/auth/google", json={"credential": "x.y.z"})
    assert r.status_code == 200, r.text
    u = r.json()["user"]
    assert u["auth_provider"] == "google" and not u["has_password"] and u["username"] == "grace"
    again = client().post("/api/auth/google", json={"credential": "x.y.z"}).json()["user"]
    assert again["id"] == u["id"] and again["login_count"] == 2
    # a Google-only account cannot log in with a password
    r = client().post("/api/auth/login", json={"identifier": "grace@example.com", "password": PW})
    assert r.status_code == 401 and "Google" in r.json()["detail"]


def test_google_links_existing_password_account(fresh, monkeypatch):
    first = signup(client(), "grace@example.com").json()["user"]
    _google(monkeypatch)
    u = client().post("/api/auth/google", json={"credential": "x.y.z"}).json()["user"]
    assert u["id"] == first["id"] and u["auth_provider"] == "local+google" and u["has_password"]


@pytest.mark.parametrize("bad", [{"aud": "someone-else"}, {"iss": "evil.com"}, {"email_verified": "false"},
                                 {"exp": "1"}])
def test_google_rejects_bad_tokens(fresh, monkeypatch, bad):
    _google(monkeypatch, **bad)
    assert client().post("/api/auth/google", json={"credential": "x.y.z"}).status_code == 401
    assert db.query("SELECT COUNT(*) AS n FROM users")[0]["n"] == 0


def test_saved_queries_are_private_per_user(fresh):
    a, b = client(), client()
    signup(a, "a@example.com")
    signup(b, "b@example.com")
    assert client().get("/api/me/queries").status_code == 401                       # guests have no server history
    q = a.post("/api/me/queries", json={"enquiry": "  Water in   crude oil  ", "mode": "council", "paths": ["B", "X", "A"],
                                         "view": "expert"}).json()
    assert q["title"] == "Water in crude oil" and q["paths"] == ["A", "B"] and q["mode"] == "council"
    assert [x["id"] for x in a.get("/api/me/queries").json()] == [q["id"]]
    assert b.get("/api/me/queries").json() == []
    hijack = b.post("/api/me/queries", json={"id": q["id"], "enquiry": "overwrite"}).json()
    assert hijack["id"] != q["id"]                                                  # never overwrites A's row
    assert a.get("/api/me/queries").json()[0]["enquiry"] == "Water in   crude oil"
    b.delete(f"/api/me/queries/{q['id']}")
    assert len(a.get("/api/me/queries").json()) == 1
    a.delete(f"/api/me/queries/{q['id']}")
    assert a.get("/api/me/queries").json() == []


def test_runs_are_linked_to_user_view_and_query(fresh, monkeypatch):
    def fake_run(request, emit=None):
        return RunResult(id=f"run-{request.mode}", created=service.now(), mode=request.mode, enquiry=request.enquiry)

    monkeypatch.setattr(assess_api.pipeline, "run", fake_run)
    c = client()
    signup(c)
    assert c.post("/api/billing/checkout", json={"plan": "pro"}).json()["user"]["views"] == ["general", "expert"]
    q = c.post("/api/me/queries", json={"enquiry": "Protein in whey"}).json()
    r = c.post("/api/assess/sync", json={"enquiry": "Protein in whey"},
               headers={"X-AFS-View": "expert", "X-AFS-Query-Id": q["id"]})
    assert r.status_code == 200
    runs = c.get("/api/me/runs").json()
    assert [(x["runId"], x["view"], x["queryId"]) for x in runs] == [("run-fast", "expert", q["id"])]
    assert c.get("/api/me/runs?view=general").json() == []
    assert c.get("/api/me/queries").json()[0]["lastRunId"] == "run-fast"
    # guests still run normally and nothing is recorded
    assert client().post("/api/assess/sync", json={"enquiry": "x", "mode": "council"}).status_code == 200
    assert db.query("SELECT COUNT(*) AS n FROM user_runs")[0]["n"] == 1


def test_projects(fresh):
    c = client()
    signup(c)
    p = c.post("/api/me/projects", json={"title": "Dairy line 2"}).json()
    assert [x["title"] for x in c.get("/api/me/projects").json()] == ["Dairy line 2"]
    q = c.post("/api/me/queries", json={"enquiry": "Fat in milk", "projectId": p["id"]}).json()
    assert q["projectId"] == p["id"]
    assert c.post("/api/me/queries", json={"enquiry": "x", "projectId": "nope"}).status_code == 404


def test_password_hash_roundtrip():
    h = security.hash_password("s3cret-pass")
    assert security.verify_password("s3cret-pass", h) and not security.verify_password("other", h)
    assert not security.verify_password("x", None) and not security.verify_password("x", "garbage")


def test_pages_require_login(fresh):
    c = client()
    r = c.get("/", follow_redirects=False)
    assert r.status_code == 307 and r.headers["location"] == "/login"
    r = c.get("/app", follow_redirects=False)
    assert r.status_code == 307 and r.headers["location"].startswith("/login?next=")
    assert c.get("/login").status_code == 200 and c.get("/pricing").status_code == 200
    signup(c)
    assert c.get("/app", follow_redirects=False).status_code == 200
    r = c.get("/login?next=//evil.com", follow_redirects=False)            # signed in: straight to the app,
    assert r.status_code == 307 and r.headers["location"] == "/app"         # never to another site


def test_auth_can_be_switched_off_for_the_demo(fresh, monkeypatch):
    import backend.app.main as main
    monkeypatch.setattr(main, "settings", dataclasses.replace(main.settings, auth_required=False))
    c = client()
    assert c.get("/", follow_redirects=False).status_code == 200
    assert c.get("/app", follow_redirects=False).status_code == 200


def _billing(monkeypatch, mode):
    patched = dataclasses.replace(auth_api.settings, billing_mode=mode)
    monkeypatch.setattr(auth_api, "settings", patched)
    monkeypatch.setattr(plans, "settings", patched)


def test_plans_and_demo_checkout(fresh, monkeypatch):
    _billing(monkeypatch, "demo")
    c = client()
    info = c.get("/api/billing/plans").json()
    assert [(p["id"], p["price_usd"], p["views"]) for p in info["plans"]] == [
        ("basic", 10, ["general"]), ("pro", 30, ["general", "expert"])]
    assert info["current"] is None
    assert c.post("/api/billing/checkout", json={"plan": "pro"}).status_code == 401    # must be logged in
    signup(c)
    assert c.get("/api/billing/plans").json()["current"] == "basic"
    assert c.post("/api/billing/checkout", json={"plan": "gold"}).status_code == 404
    r = c.post("/api/billing/checkout", json={"plan": "pro"}).json()
    assert r["status"] == "active" and r["demo"] and r["user"]["subscription_tier"] == "pro"
    assert c.get("/api/auth/me").json()["user"]["views"] == ["general", "expert"]
    r = c.post("/api/billing/checkout", json={"plan": "basic"}).json()
    assert r["user"]["views"] == ["general"]


def test_checkout_refuses_when_payments_are_off(fresh, monkeypatch):
    _billing(monkeypatch, "off")
    c = client()
    signup(c)
    r = c.post("/api/billing/checkout", json={"plan": "pro"})
    assert r.status_code == 503 and c.get("/api/auth/me").json()["user"]["subscription_tier"] == "basic"


def test_basic_account_cannot_log_expert_runs(fresh, monkeypatch):
    monkeypatch.setattr(assess_api.pipeline, "run", lambda request, emit=None: RunResult(
        id="run-b", created=service.now(), mode="fast", enquiry=request.enquiry))
    c = client()
    signup(c)
    c.post("/api/assess/sync", json={"enquiry": "x"}, headers={"X-AFS-View": "expert"})
    assert [r["view"] for r in c.get("/api/me/runs").json()] == ["general"]


def test_legacy_tier_names_map_to_plans():
    assert plans.tier_of({"subscription_tier": "free"}) == "basic"
    assert plans.tier_of({"subscription_tier": "expert"}) == "pro"
    assert plans.tier_of({"subscription_tier": "nonsense"}) == "basic" and plans.tier_of(None) == "basic"
