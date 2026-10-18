"""Storage: Supabase (Postgres) as the main database, SQLite as the local copy and offline fallback.

SQLite (data/cache/afs.db) holds chunks, FTS5, vectors, runs, llm_cache and feedback. The ingest always
builds the knowledge base here; `python scripts/push_to_supabase.py` publishes it to Supabase.

With SUPABASE_DB_URL set (DB_BACKEND not "sqlite"), kb/remote.py makes Supabase the source of truth:
  - retrieval (keyword + dense search, chunk and vector reads) runs in Supabase when its knowledge base
    matches the local ingest; otherwise, and whenever Supabase is offline, the local index is used;
  - runs, LLM cache and feedback are written to Supabase and kept locally too; reads come from Supabase
    (the LLM cache is checked locally first).
Every public function below keeps the same signature as the SQLite-only version.
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Any, Iterator

import numpy as np

from ..config import settings
from . import remote

_LOCK = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id        INTEGER PRIMARY KEY,
    kind      TEXT NOT NULL,          -- 'chunk' | 'claim'
    source    TEXT NOT NULL,
    page      INTEGER NOT NULL,
    text      TEXT NOT NULL,
    quote     TEXT,
    scope     TEXT,
    claim_id  TEXT
);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, tokenize='porter unicode61');
CREATE TABLE IF NOT EXISTS vectors (
    chunk_id  INTEGER PRIMARY KEY,
    vec       BLOB NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS runs (
    id        TEXT PRIMARY KEY,
    created   TEXT NOT NULL,
    parent    TEXT,
    mode      TEXT,
    enquiry   TEXT,
    status    TEXT,
    json      TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS llm_cache (
    key       TEXT PRIMARY KEY,
    model     TEXT,
    response  TEXT NOT NULL,
    usage     TEXT,
    created   REAL
);
CREATE TABLE IF NOT EXISTS feedback (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id    TEXT,
    created   TEXT,
    target    TEXT,
    verdict   TEXT,
    comment   TEXT
);
"""


def connect() -> sqlite3.Connection:
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(settings.db_path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


_CON: sqlite3.Connection | None = None


def con() -> sqlite3.Connection:
    global _CON
    if _CON is None:
        _CON = connect()
    return _CON


@contextmanager
def tx() -> Iterator[sqlite3.Connection]:
    with _LOCK:
        c = con()
        try:
            yield c
            c.commit()
        except Exception:
            c.rollback()
            raise


# ------------------------------------------------------------------ which knowledge base answers
def _local_meta(key: str, default: str = "") -> str:
    r = con().execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return r[0] if r else default


def kb_online() -> bool:
    """True when retrieval should run in Supabase (online, pushed, same embeddings and ingest as here)."""
    if not remote.enabled():
        return False
    from . import embed
    return remote.kb_ready(_local_meta("embed_backend") or embed.backend(), _local_meta("ingested_at"),
                           _local_meta("kb_hash"))


def db_status() -> dict:
    from . import embed
    return remote.status(_local_meta("embed_backend") or embed.backend(), _local_meta("ingested_at"),
                         _local_meta("kb_hash"))


# ------------------------------------------------------------------ knowledge base: writes (always local; push publishes)
def reset_kb() -> None:
    with tx() as c:
        c.execute("DELETE FROM chunks")
        c.execute("DELETE FROM chunks_fts")
        c.execute("DELETE FROM vectors")
    remote.forget_kb_check()


def add_chunk(kind: str, source: str, page: int, text: str, quote: str | None = None,
              scope: str | None = None, claim_id: str | None = None) -> int:
    with tx() as c:
        cur = c.execute(
            "INSERT INTO chunks(kind, source, page, text, quote, scope, claim_id) VALUES (?,?,?,?,?,?,?)",
            (kind, source, page, text, quote, scope, claim_id))
        cid = cur.lastrowid
        c.execute("INSERT INTO chunks_fts(rowid, text) VALUES (?, ?)", (cid, text))
        return cid


def add_vectors(ids: list[int], vecs: np.ndarray) -> None:
    with tx() as c:
        c.executemany("INSERT OR REPLACE INTO vectors(chunk_id, vec) VALUES (?, ?)",
                      [(i, v.astype(np.float32).tobytes()) for i, v in zip(ids, vecs)])


def set_meta(key: str, value: str) -> None:
    with tx() as c:
        c.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, value))
    remote.forget_kb_check()


# ------------------------------------------------------------------ knowledge base: reads
def all_chunks() -> list[dict[str, Any]]:
    return [dict(r) for r in con().execute("SELECT * FROM chunks ORDER BY id")]


def get_chunks(ids: list[int]) -> dict[int, dict[str, Any]]:
    if not ids:
        return {}
    if kb_online():
        online = remote.get_chunks(ids)
        if online is not None:
            return online
    q = ",".join("?" * len(ids))
    return {r["id"]: dict(r) for r in con().execute(f"SELECT * FROM chunks WHERE id IN ({q})", ids)}


def claims_on_pages(pages: list[tuple[str, int]]) -> list[int]:
    """Ids of evidence cards on the given (source, page) pairs (pinned evidence)."""
    if not pages:
        return []
    if kb_online():
        online = remote.claims_on_pages(pages)
        if online is not None:
            return online
    wanted = set(pages)
    return [r["id"] for r in con().execute("SELECT id, source, page FROM chunks WHERE kind='claim' ORDER BY id")
            if (r["source"], r["page"]) in wanted]


_VEC_CACHE: tuple[np.ndarray, np.ndarray] | None = None


def load_vectors() -> tuple[np.ndarray, np.ndarray]:
    """Local (ids, matrix L2-normalised). Cached in memory after first load."""
    global _VEC_CACHE
    if _VEC_CACHE is None:
        rows = con().execute("SELECT chunk_id, vec FROM vectors ORDER BY chunk_id").fetchall()
        if not rows:
            return np.zeros(0, dtype=int), np.zeros((0, 1), dtype=np.float32)
        ids = np.array([r[0] for r in rows])
        mat = np.vstack([np.frombuffer(r[1], dtype=np.float32) for r in rows])
        mat = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-9)
        _VEC_CACHE = (ids, mat)
    return _VEC_CACHE


def clear_vector_cache() -> None:
    global _VEC_CACHE
    _VEC_CACHE = None


def dense_search(query_vec: np.ndarray, k: int) -> list[int]:
    """Cosine nearest neighbours: pgvector in Supabase, numpy locally (same order)."""
    if kb_online():
        online = remote.dense_search(query_vec, k)
        if online is not None:
            return online
    ids, mat = load_vectors()
    if len(ids) == 0:
        return []
    order = np.argsort(-(mat @ query_vec))[:k]
    return [int(ids[i]) for i in order]


def get_vectors(ids: list[int]) -> dict[int, np.ndarray]:
    """Normalised vectors of the given chunks (MMR diversity)."""
    if kb_online():
        online = remote.get_vectors(ids)
        if online is not None:
            return online
    all_ids, mat = load_vectors()
    index = {int(i): n for n, i in enumerate(all_ids)}
    return {i: mat[index[i]] for i in ids if i in index}


_FTS_SAFE = re.compile(r"[A-Za-z0-9]+")


def bm25_search(query: str, k: int = 20) -> list[tuple[int, float]]:
    """Keyword search: Postgres full text in Supabase, FTS5 BM25 locally. The query is an OR of its words."""
    if kb_online():
        online = remote.keyword_search(query, k)
        if online is not None:
            return online
    words = [w for w in _FTS_SAFE.findall(query.lower()) if len(w) > 1]
    if not words:
        return []
    match = " OR ".join(f'"{w}"' for w in dict.fromkeys(words))
    rows = con().execute(
        "SELECT rowid, bm25(chunks_fts) AS s FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY s LIMIT ?",
        (match, k)).fetchall()
    return [(r[0], -float(r[1])) for r in rows]  # bm25() is lower-is-better


def get_meta(key: str, default: str = "") -> str:
    if kb_online():
        online = remote.get_meta(key)
        if online is not None:
            return online or default
    return _local_meta(key, default)


def local_kb_size() -> int:
    return con().execute("SELECT COUNT(*) FROM chunks").fetchone()[0]


def kb_size() -> int:
    if kb_online():
        online = remote.kb_size()
        if online is not None:
            return online
    return local_kb_size()


# ------------------------------------------------------------------ runs
def _save_run_local(run: dict[str, Any]) -> tuple:
    status = (run.get("report") or {}).get("decision_status", "")
    row = (run["id"], run["created"], run.get("parent_run_id"), run.get("mode"), run.get("enquiry", ""), status,
           json.dumps(run))
    with tx() as c:
        c.execute("INSERT OR REPLACE INTO runs(id, created, parent, mode, enquiry, status, json) VALUES (?,?,?,?,?,?,?)", row)
    return row


def save_run(run: dict[str, Any]) -> None:
    row = _save_run_local(run)          # local copy first: never lose a run
    if remote.enabled():
        remote.save_run(row)            # offline: stays local and is uploaded by the next sync
        schedule_sync()                 # upload anything else that is still only local


def get_run(run_id: str) -> dict[str, Any] | None:
    if remote.enabled():
        online = remote.get_run_json(run_id)
        if online is not None:
            return online if isinstance(online, dict) else json.loads(online)
    r = con().execute("SELECT json FROM runs WHERE id=?", (run_id,)).fetchone()
    return json.loads(r[0]) if r else None


def list_runs(limit: int = 50) -> list[dict[str, Any]]:
    if remote.enabled():
        online = remote.list_runs(limit)
        if online is not None:
            return online
    rows = con().execute("SELECT id, created, parent, mode, enquiry, status FROM runs ORDER BY created DESC LIMIT ?",
                         (limit,)).fetchall()
    return [dict(r) for r in rows]


# ------------------------------------------------------------------ llm cache
def _cache_put_local(key: str, model: str | None, response: str, usage: str, created: float) -> None:
    with tx() as c:
        c.execute("INSERT OR REPLACE INTO llm_cache(key, model, response, usage, created) VALUES (?,?,?,?,?)",
                  (key, model, response, usage, created))


def cache_get(key: str) -> tuple[str, dict] | None:
    r = con().execute("SELECT response, usage FROM llm_cache WHERE key=?", (key,)).fetchone()
    if r:                                                                 # same key = same reply: local is fine
        return r[0], json.loads(r[1] or "{}")
    online = remote.cache_get(key) if remote.enabled() else None          # shared cache: saves Groq quota
    if not online:
        return None
    response, usage, model, created = online
    _cache_put_local(key, model, response, usage or "{}", created or time.time())
    return response, json.loads(usage or "{}")


def cache_put(key: str, model: str, response: str, usage: dict) -> None:
    row = (key, model, response, json.dumps(usage), time.time())
    _cache_put_local(*row)
    if remote.enabled():
        remote.cache_put(row)


# ------------------------------------------------------------------ feedback
def add_feedback(run_id: str, target: str, verdict: str, comment: str) -> int:
    created = time.strftime("%Y-%m-%dT%H:%M:%S")
    fid = remote.add_feedback(run_id, created, target, verdict, comment) if remote.enabled() else None
    with tx() as c:
        if fid is not None:   # Supabase gave the id: keep the same id locally
            c.execute("INSERT OR REPLACE INTO feedback(id, run_id, created, target, verdict, comment) VALUES (?,?,?,?,?,?)",
                      (fid, run_id, created, target, verdict, comment))
        else:
            fid = c.execute("INSERT INTO feedback(run_id, created, target, verdict, comment) VALUES (?,?,?,?,?)",
                            (run_id, created, target, verdict, comment)).lastrowid
    return fid


def list_feedback(run_id: str | None = None) -> list[dict[str, Any]]:
    if remote.enabled():
        online = remote.list_feedback(run_id)
        if online is not None:
            return online
    if run_id:
        rows = con().execute("SELECT * FROM feedback WHERE run_id=? ORDER BY id", (run_id,))
    else:
        rows = con().execute("SELECT * FROM feedback ORDER BY id DESC LIMIT 200")
    return [dict(r) for r in rows]


# ------------------------------------------------------------------ automatic sync to Supabase
# After every saved run (and once at startup) anything that exists only in the local file is uploaded:
# runs and cache rows by key, feedback by content. At startup the knowledge base is also published when
# Supabase has none, or one from another ingest. Runs in a background thread; never blocks or fails a run.
# AUTO_SYNC=0 in .env turns it off (then use scripts/push_to_supabase.py by hand).
_SYNC_LOCK = threading.Lock()
_sync_log = __import__("logging").getLogger("afs.sync")


def _auto_sync_on() -> bool:
    import os
    return remote.enabled() and os.getenv("AUTO_SYNC", "1") != "0"


def sync_to_supabase() -> dict | None:
    """Upload local-only runs, cache and feedback. Returns counts, or None when offline / busy."""
    if not remote.enabled() or not _SYNC_LOCK.acquire(blocking=False):
        return None
    try:
        out = {"runs": 0, "llm_cache": 0, "feedback": 0}
        ids = [r[0] for r in con().execute("SELECT id FROM runs")]
        missing = remote.missing_keys("runs", "id", ids)
        if missing is None:
            return None
        for row in con().execute("SELECT id, created, parent, mode, enquiry, status, json FROM runs").fetchall():
            if row[0] in missing and remote.save_run(tuple(row)):
                out["runs"] += 1
        keys = [r[0] for r in con().execute("SELECT key FROM llm_cache")]
        missing = remote.missing_keys("llm_cache", "key", keys) or set()
        for row in con().execute("SELECT key, model, response, usage, created FROM llm_cache").fetchall():
            if row[0] in missing and remote.cache_put(tuple(row)):
                out["llm_cache"] += 1
        fb = [tuple(r) for r in con().execute("SELECT run_id, created, target, verdict, comment FROM feedback")]
        out["feedback"] = remote.feedback_if_new(fb) or 0
        if any(out.values()):
            _sync_log.info("Synced local-only rows to Supabase: %s", out)
        return out
    finally:
        _SYNC_LOCK.release()


def publish_kb_if_needed() -> bool:
    """Publish the local knowledge base (and merge runs/cache/feedback) with scripts/push_to_supabase.py
    when Supabase has no knowledge base or one from another ingest. Returns True if it pushed."""
    if not remote.enabled() or kb_online() or not remote.online():
        return False
    import importlib.util
    script = settings.db_path.resolve().parents[2] / "scripts" / "push_to_supabase.py"
    if not script.exists():
        from pathlib import Path
        script = Path(__file__).resolve().parents[3] / "scripts" / "push_to_supabase.py"
    spec = importlib.util.spec_from_file_location("push_to_supabase", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _sync_log.info("Publishing the local knowledge base to Supabase (%s) ...", remote.kb_reason() or "first time")
    data = mod.read_sqlite(settings.db_path.resolve())
    counts = mod.push(data, remote.effective_url(), mod.validate(data))
    remote.forget_kb_check()
    _sync_log.info("Knowledge base published: %s; retrieval now %s", counts, "online" if kb_online() else "local")
    return True


def _sync_job(startup: bool) -> None:
    try:
        if startup:
            publish_kb_if_needed()
        sync_to_supabase()
    except Exception as exc:  # noqa: BLE001  (sync must never break the app)
        _sync_log.warning("Sync to Supabase failed, will retry after the next run: %s", str(exc).splitlines()[0][:200])


def schedule_sync(startup: bool = False) -> None:
    if _auto_sync_on():
        threading.Thread(target=_sync_job, args=(startup,), name="supabase-sync", daemon=True).start()