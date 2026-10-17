"""scripts/push_to_supabase.py: read, validate and SQL rendering, all offline (no Postgres needed)."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
from array import array
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "push_to_supabase", Path(__file__).resolve().parents[1] / "scripts" / "push_to_supabase.py")
push = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(push)

SCHEMA = """
CREATE TABLE chunks (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, source TEXT NOT NULL, page INTEGER NOT NULL,
                     text TEXT NOT NULL, quote TEXT, scope TEXT, claim_id TEXT);
CREATE TABLE vectors (chunk_id INTEGER PRIMARY KEY, vec BLOB NOT NULL);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE runs (id TEXT PRIMARY KEY, created TEXT NOT NULL, parent TEXT, mode TEXT, enquiry TEXT,
                   status TEXT, json TEXT NOT NULL);
CREATE TABLE llm_cache (key TEXT PRIMARY KEY, model TEXT, response TEXT NOT NULL, usage TEXT, created REAL);
CREATE TABLE feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, created TEXT, target TEXT,
                       verdict TEXT, comment TEXT);
"""


def _blob(xs):
    return array("f", xs).tobytes()


def _make_db(path: Path, run_id: str = "r1", dim: int = 4) -> Path:
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.execute("INSERT INTO chunks VALUES (1,'chunk','S01',6,'NIR 780-2500 nm, the client''s probe',NULL,'overview',NULL)")
    con.execute("INSERT INTO chunks VALUES (2,'claim','S02',6,?,'q','fiber','C1')", ("silica\x00 fiber",))
    con.execute("INSERT INTO vectors VALUES (1, ?)", (_blob([0.1, -0.2, 0.3, 1 / 3][:dim]),))
    con.execute("INSERT INTO vectors VALUES (2, ?)", (_blob([0.0, 1.0, 0.0, 0.0][:dim]),))
    con.execute("INSERT INTO meta VALUES ('embed_backend','fastembed:BAAI/bge-small-en-v1.5')")
    con.execute("INSERT INTO runs VALUES (?, '2026-10-17T13:21:06', NULL, 'fast', 'enq', 'provisional_assessment', ?)",
                (run_id, json.dumps({"id": run_id})))
    con.execute("INSERT INTO llm_cache VALUES ('k-' || ?, 'm', 'resp', NULL, 1.5)", (run_id,))
    con.commit()
    con.close()
    return path


def test_read_and_validate(tmp_path):
    data = push.read_sqlite(_make_db(tmp_path / "a.db"))
    assert push.validate(data) == 4
    assert [c["id"] for c in data["chunks"]] == [1, 2]
    assert "\x00" not in data["chunks"][1]["text"]  # Postgres text cannot hold NUL
    assert data["vectors"][0]["embedding"][3] == pytest.approx(1 / 3, rel=1e-6)


def test_vec_literal_round_trips_float32():
    xs = array("f", [1 / 3, -1e-7, 123.456]).tolist()
    back = [float(x) for x in push.vec_literal(xs)[1:-1].split(",")]
    assert array("f", back).tobytes() == array("f", xs).tobytes()


def test_validate_rejects_orphan_vectors(tmp_path):
    data = push.read_sqlite(_make_db(tmp_path / "a.db"))
    data["vectors"].append({"chunk_id": 99, "embedding": [0.0] * 4})
    with pytest.raises(SystemExit, match="missing chunks"):
        push.validate(data)


def test_merge_extra_adds_new_runs_only(tmp_path):
    data = push.read_sqlite(_make_db(tmp_path / "a.db", "r1"))
    push.merge_extra(data, push.read_sqlite(_make_db(tmp_path / "b.db", "r2"), kb=False))
    push.merge_extra(data, push.read_sqlite(_make_db(tmp_path / "c.db", "r1"), kb=False))
    assert sorted(r["id"] for r in data["runs"]) == ["r1", "r2"]
    assert len(data["llm_cache"]) == 2


def test_write_sql_quotes_and_orders(tmp_path):
    data = push.read_sqlite(_make_db(tmp_path / "a.db"))
    files = push.write_sql(data, push.validate(data), tmp_path / "sql")
    names = [f.name for f in files]
    assert names[0] == "00_schema.sql" and names[-1].endswith("_finish.sql")
    assert names.index("01_chunks_1.sql") < names.index("02_vectors_1.sql")
    body = "".join(f.read_text(encoding="utf-8") for f in files)
    assert "extensions.vector(4)" in body
    assert "'NIR 780-2500 nm, the client''s probe'" in body
    assert "%s" not in body
    assert "enable row level security" in body


def test_safe_target_hides_password():
    url = "postgresql://postgres.abc:s3cret@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"
    assert "s3cret" not in push.safe_target(url)


def test_pooler_candidates_from_direct_url():
    url = "postgresql://postgres:pa%40ss@db.abcref.supabase.co:5432/postgres"
    cands = push.pooler_candidates(url)
    assert cands[0] == "postgresql://postgres.abcref:pa%40ss@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"
    assert all(c.endswith(".pooler.supabase.com:5432/postgres") for c in cands)
    assert push.pooler_candidates("postgresql://u:p@localhost:5432/x") == []
