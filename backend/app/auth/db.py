"""Accounts storage: users, sessions, projects, saved queries and each user's runs.

Same pattern as kb/store.py. With SUPABASE_DB_URL set, Supabase (Postgres) is the main database and the
local SQLite file is a copy and the offline fallback; without it, SQLite is the only store.

  write   goes to the main database first (a duplicate e-mail is reported from there), then best-effort
          to the other one.
  read    asks the main database; if the row is not there, the other one (an account created while
          Supabase was offline still logs in, and is copied up on its next login).

The SQL is written once with "?" placeholders and runs on both engines. No foreign keys: the two copies
can briefly disagree, and a missing parent row must not block a login. Passwords are never stored (only a
scrypt hash, see security.py); session tokens are stored as SHA-256 hashes.
"""
from __future__ import annotations

import logging
import sqlite3
import threading
from typing import Any, Callable

from ..kb import remote, store

log = logging.getLogger("afs.auth")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id                      TEXT PRIMARY KEY,
    email                   TEXT NOT NULL UNIQUE,
    username                TEXT UNIQUE,
    name                    TEXT,
    password_hash           TEXT,
    auth_provider           TEXT NOT NULL DEFAULT 'local',
    google_sub              TEXT UNIQUE,
    avatar_url              TEXT,
    subscription_tier       TEXT NOT NULL DEFAULT 'basic',
    subscription_expires_at TEXT,
    created_at              TEXT NOT NULL,
    updated_at              TEXT NOT NULL,
    last_login_at           TEXT,
    login_count             INTEGER NOT NULL DEFAULT 0,
    is_active               INTEGER NOT NULL DEFAULT 1,
    preferences             TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS user_sessions (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    expires_at    TEXT NOT NULL,
    revoked_at    TEXT,
    auth_method   TEXT,
    user_agent    TEXT,
    ip            TEXT
);
CREATE INDEX IF NOT EXISTS user_sessions_user_idx ON user_sessions (user_id);
CREATE TABLE IF NOT EXISTS projects (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL,
    title         TEXT NOT NULL,
    description   TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    archived      INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS projects_user_idx ON projects (user_id);
CREATE TABLE IF NOT EXISTS saved_queries (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL,
    project_id    TEXT,
    title         TEXT NOT NULL,
    enquiry       TEXT NOT NULL,
    mode          TEXT NOT NULL DEFAULT 'fast',
    model_choice  TEXT NOT NULL DEFAULT 'auto',
    paths         TEXT NOT NULL DEFAULT '[]',
    view          TEXT,
    last_run_id   TEXT,
    last_status   TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS saved_queries_user_idx ON saved_queries (user_id, updated_at);
CREATE TABLE IF NOT EXISTS user_runs (
    run_id        TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL,
    query_id      TEXT,
    parent_run_id TEXT,
    view          TEXT NOT NULL DEFAULT 'general',
    mode          TEXT,
    title         TEXT,
    status        TEXT,
    confidence    TEXT,
    created_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS user_runs_user_idx ON user_runs (user_id, created_at);
"""

TABLES = ("users", "user_sessions", "projects", "saved_queries", "user_runs")
# Supabase exposes public tables through its REST API; RLS with no policies closes that door.
# The app connects as the database owner, which bypasses RLS.
RLS = "".join(f"\nALTER TABLE public.{t} ENABLE ROW LEVEL SECURITY;" for t in TABLES)


class Duplicate(Exception):
    """A unique column (e-mail, username, Google account) is already taken."""


_local_lock = threading.Lock()
_local_ready = False
_remote_ready = False


# ------------------------------------------------------------------ engines
def _local(fn: Callable[[sqlite3.Connection], Any]) -> Any:
    global _local_ready
    with store.tx() as c:
        if not _local_ready:
            c.executescript(SCHEMA)
            _local_ready = True
        try:
            return fn(c)
        except sqlite3.IntegrityError as exc:
            raise Duplicate(str(exc)) from exc


def _remote(fn: Callable[[Any], Any]) -> tuple[bool, Any]:
    """(True, value) when Supabase answered; (False, None) when it is not configured or offline."""
    if not remote.enabled():
        return False, None

    def go(c):
        global _remote_ready
        if not _remote_ready:
            c.execute(SCHEMA + RLS)
            _remote_ready = True
        try:
            return ("ok", fn(c))
        except Exception as exc:  # noqa: BLE001
            # remote._run treats any exception as "offline"; a unique violation is a normal answer
            if str(getattr(exc, "sqlstate", "") or "").startswith("23"):
                return ("dup", str(exc).splitlines()[0])
            raise

    res = remote._run(go)  # noqa: SLF001  (shared connection, lock and offline handling)
    if res is None:
        return False, None
    if res[0] == "dup":
        raise Duplicate(res[1])
    return True, res[1]


def _pg(sql: str) -> str:
    return sql.replace("?", "%s")


def _dicts(cur) -> list[dict]:
    if cur.description is None:
        return []
    cols = [getattr(d, "name", None) or d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def backend() -> str:
    """Which store answers right now: 'supabase' or 'local'."""
    ok, _ = _remote(lambda c: c.execute("select 1").fetchone())
    return "supabase" if ok else "local"


# ------------------------------------------------------------------ public API
def write(sql: str, params: tuple = ()) -> int:
    """Run an INSERT/UPDATE/DELETE on the main store (errors propagate), then mirror it. Returns rowcount."""
    ok, n = _remote(lambda c: c.execute(_pg(sql), params).rowcount)
    if ok:
        try:
            _local(lambda c: c.execute(sql, params))
        except Exception as exc:  # noqa: BLE001  (the copy is best-effort)
            log.debug("local mirror write skipped: %s", exc)
        return n
    return _local(lambda c: c.execute(sql, params).rowcount)


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Rows from the main store; if it has none, from the other one."""
    ok, rows = _remote(lambda c: _dicts(c.execute(_pg(sql), params)))
    if ok and rows:
        return rows
    return _local(lambda c: _dicts(c.execute(sql, params)))


def query_merged(sql: str, params: tuple = (), key: str = "id") -> list[dict]:
    """Rows from both stores, de-duplicated by key (main store wins). For history lists."""
    ok, rows = _remote(lambda c: _dicts(c.execute(_pg(sql), params)))
    local = _local(lambda c: _dicts(c.execute(sql, params)))
    if not ok:
        return local
    seen = {r[key] for r in rows}
    return rows + [r for r in local if r[key] not in seen]


def one(sql: str, params: tuple = ()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def upsert(table: str, row: dict, key: str = "id") -> None:
    cols = list(row)
    sets = ", ".join(f"{c} = excluded.{c}" for c in cols if c != key)
    sql = (f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)}) "
           f"ON CONFLICT ({key}) DO UPDATE SET {sets}")
    write(sql, tuple(row[c] for c in cols))


def reset_for_tests() -> None:
    global _local_ready, _remote_ready
    _local_ready = _remote_ready = False
