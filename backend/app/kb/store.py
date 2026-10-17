"""SQLite: chunks, FTS5, vectors, runs, llm_cache, feedback.

One file (data/cache/afs.db) holds everything. FTS5 gives BM25 keyword search;
embeddings are float32 blobs searched by brute-force cosine in numpy (a few
hundred chunks, so this takes microseconds).
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


# ------------------------------------------------------------------ knowledge base
def reset_kb() -> None:
    with tx() as c:
        c.execute("DELETE FROM chunks")
        c.execute("DELETE FROM chunks_fts")
        c.execute("DELETE FROM vectors")


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


def all_chunks() -> list[dict[str, Any]]:
    return [dict(r) for r in con().execute("SELECT * FROM chunks ORDER BY id")]


def get_chunks(ids: list[int]) -> dict[int, dict[str, Any]]:
    if not ids:
        return {}
    q = ",".join("?" * len(ids))
    return {r["id"]: dict(r) for r in con().execute(f"SELECT * FROM chunks WHERE id IN ({q})", ids)}


_VEC_CACHE: tuple[np.ndarray, np.ndarray] | None = None


def load_vectors() -> tuple[np.ndarray, np.ndarray]:
    """(ids, matrix L2-normalised). Cached in memory after first load."""
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


_FTS_SAFE = re.compile(r"[A-Za-z0-9]+")


def bm25_search(query: str, k: int = 20) -> list[tuple[int, float]]:
    """FTS5 BM25. Query is turned into an OR of its words so it never raises a syntax error."""
    words = [w for w in _FTS_SAFE.findall(query.lower()) if len(w) > 1]
    if not words:
        return []
    match = " OR ".join(f'"{w}"' for w in dict.fromkeys(words))
    rows = con().execute(
        "SELECT rowid, bm25(chunks_fts) AS s FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY s LIMIT ?",
        (match, k)).fetchall()
    return [(r[0], -float(r[1])) for r in rows]  # bm25() is lower-is-better


def set_meta(key: str, value: str) -> None:
    with tx() as c:
        c.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, value))


def get_meta(key: str, default: str = "") -> str:
    r = con().execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return r[0] if r else default


def kb_size() -> int:
    return con().execute("SELECT COUNT(*) FROM chunks").fetchone()[0]


# ------------------------------------------------------------------ runs
def save_run(run: dict[str, Any]) -> None:
    status = (run.get("report") or {}).get("decision_status", "")
    with tx() as c:
        c.execute("INSERT OR REPLACE INTO runs(id, created, parent, mode, enquiry, status, json) VALUES (?,?,?,?,?,?,?)",
                  (run["id"], run["created"], run.get("parent_run_id"), run.get("mode"),
                   run.get("enquiry", ""), status, json.dumps(run)))


def get_run(run_id: str) -> dict[str, Any] | None:
    r = con().execute("SELECT json FROM runs WHERE id=?", (run_id,)).fetchone()
    return json.loads(r[0]) if r else None


def list_runs(limit: int = 50) -> list[dict[str, Any]]:
    rows = con().execute("SELECT id, created, parent, mode, enquiry, status FROM runs ORDER BY created DESC LIMIT ?",
                         (limit,)).fetchall()
    return [dict(r) for r in rows]


# ------------------------------------------------------------------ llm cache
def cache_get(key: str) -> tuple[str, dict] | None:
    r = con().execute("SELECT response, usage FROM llm_cache WHERE key=?", (key,)).fetchone()
    return (r[0], json.loads(r[1] or "{}")) if r else None


def cache_put(key: str, model: str, response: str, usage: dict) -> None:
    with tx() as c:
        c.execute("INSERT OR REPLACE INTO llm_cache(key, model, response, usage, created) VALUES (?,?,?,?,?)",
                  (key, model, response, json.dumps(usage), time.time()))


# ------------------------------------------------------------------ feedback
def add_feedback(run_id: str, target: str, verdict: str, comment: str) -> int:
    with tx() as c:
        cur = c.execute("INSERT INTO feedback(run_id, created, target, verdict, comment) VALUES (?,?,?,?,?)",
                        (run_id, time.strftime("%Y-%m-%dT%H:%M:%S"), target, verdict, comment))
        return cur.lastrowid


def list_feedback(run_id: str | None = None) -> list[dict[str, Any]]:
    if run_id:
        rows = con().execute("SELECT * FROM feedback WHERE run_id=? ORDER BY id", (run_id,))
    else:
        rows = con().execute("SELECT * FROM feedback ORDER BY id DESC LIMIT 200")
    return [dict(r) for r in rows]
