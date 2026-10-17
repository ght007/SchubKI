"""Check the Supabase database the app uses. Read-mostly; the round-trip test row is deleted again.

Run from the repo root (uses SUPABASE_DB_URL from .env):
    python scripts/check_supabase.py              # all checks
    python scripts/check_supabase.py --no-write   # skip the write/read/delete round-trip

Checks
 1. connection (and the IPv6 / pooler hint if it fails)
 2. tables and row counts online vs the local SQLite file
 3. knowledge base match: embedding backend and ingest time (otherwise the app uses the local index)
 4. retrieval: the same 4 queries through local and Supabase search, overlap of the top results
 5. round-trip: write a test run, cache row and feedback row, read them back, delete them
Exit code 0 = everything the app needs works online.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

QUERIES = ["moisture in powder NIR diffuse reflection", "silica fiber cannot transmit mid infrared ATR",
           "Raman fluorescence background water", "calibration model reference values chemometrics"]


def ok(msg: str) -> None:
    print(f"  OK    {msg}")


def bad(msg: str) -> None:
    print(f"  FAIL  {msg}")


def main() -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()

    from backend.app.kb import embed, remote, store

    failures = 0
    print("1. Connection")
    if not remote.url():
        bad("SUPABASE_DB_URL is not set in .env")
        return 1
    if not remote.enabled():
        bad("DB_BACKEND=sqlite in .env: the app ignores Supabase. Remove that line or set DB_BACKEND=supabase.")
        return 1
    if not remote.online():
        bad(f"cannot connect to {remote.target()}: {remote._state['error']}")
        print("        Fix: Supabase > Connect > 'Session pooler' URI into SUPABASE_DB_URL; write '@' in the password as %40.")
        return 1
    ok(f"connected to {remote.target()}")

    print("2. Tables (online vs local)")
    local = {t: store.con().execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
             for t in ("chunks", "vectors", "meta", "runs", "llm_cache", "feedback")}
    for t, n_local in local.items():
        row = remote._run(lambda c, t=t: c.execute(f"select count(*) from public.{t}").fetchone())
        if row is None:
            bad(f"{t}: missing online ({remote._state['error']}). Run: python scripts/push_to_supabase.py")
            failures += 1
            remote._state["next_try"] = 0.0
            continue
        note = "" if t in ("runs", "llm_cache", "feedback") else ("" if row[0] == n_local else "  <- differs: push again")
        print(f"        {t:10s} online {row[0]:6d}   local {n_local:6d}{note}")

    print("3. Knowledge base match")
    local_backend = store._local_meta("embed_backend") or embed.backend()
    if store.kb_online():
        ok(f"online knowledge base is used for retrieval (embeddings: {local_backend})")
    else:
        bad(f"retrieval uses the LOCAL index: {remote._state['kb_reason'] or remote._state['error']}")
        failures += 1

    print("4. Retrieval: local vs Supabase")
    if store.kb_online():
        from backend.app.kb import retrieve
        qv = embed.embed(QUERIES, is_query=True)
        for q, v in zip(QUERIES, qv):
            on_kw = [i for i, _ in remote.keyword_search(q, 10) or []]
            on_de = remote.dense_search(v, 10) or []
            os.environ["DB_BACKEND"] = "sqlite"
            try:
                lo_kw = [i for i, _ in store.bm25_search(q, 10)]
                lo_de = retrieve.dense_search(v, 10)
            finally:
                os.environ.pop("DB_BACKEND", None)
            kw, de = len(set(on_kw) & set(lo_kw)), len(set(on_de) & set(lo_de))
            print(f"        '{q[:42]}': keyword top-10 overlap {kw}/10, dense {de}/10")
            if de < 9:
                failures += 1
                bad("dense search differs: the online vectors are not the local ones (push again)")
        t0 = time.time()
        retrieve.retrieve(QUERIES[:2])
        ok(f"full retrieval through Supabase took {time.time() - t0:.2f} s for 2 queries")
    else:
        print("        skipped (online knowledge base not usable)")

    print("5. Round-trip write / read / delete")
    if a.no_write:
        print("        skipped (--no-write)")
    else:
        rid = f"selftest-{uuid.uuid4().hex[:8]}"
        key = f"selftest-{uuid.uuid4().hex}"
        run = {"id": rid, "created": time.strftime("%Y-%m-%dT%H:%M:%S"), "mode": "selftest", "enquiry": "check_supabase.py"}
        try:
            store.save_run(run)
            back = remote.get_run_json(rid)
            (ok if back and (back if isinstance(back, dict) else json.loads(back))["id"] == rid else bad)("run saved and read back")
            store.cache_put(key, "selftest", '{"ok": true}', {"prompt_tokens": 0})
            row = remote.cache_get(key)
            (ok if row and row[0] == '{"ok": true}' else bad)("LLM cache row saved and read back")
            fid = store.add_feedback(rid, "selftest", "ok", "written by check_supabase.py")
            fb = remote.list_feedback(rid) or []
            (ok if any(f["id"] == fid for f in fb) else bad)(f"feedback saved online with id {fid}")
        finally:
            remote._run(lambda c: c.execute("delete from public.feedback where run_id = %s", (rid,)))
            remote._run(lambda c: c.execute("delete from public.runs where id = %s", (rid,)))
            remote._run(lambda c: c.execute("delete from public.llm_cache where key = %s", (key,)))
            with store.tx() as c:
                c.execute("DELETE FROM feedback WHERE run_id=?", (rid,))
                c.execute("DELETE FROM runs WHERE id=?", (rid,))
                c.execute("DELETE FROM llm_cache WHERE key=?", (key,))
            print("        test rows deleted (online and local)")

    print()
    st = store.db_status()
    print(f"App will show: {st['mode']} - {st['detail']}")
    print("RESULT:", "all good" if failures == 0 else f"{failures} problem(s), see FAIL lines above")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())