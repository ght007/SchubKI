"""Knowledge-base editor: checks before saving, versions, restore, guards and permissions.
Runs on a temporary copy of data/kb and data/raw; the real files are never touched."""
import json
import shutil
import time

import pytest
from fastapi.testclient import TestClient

from backend.app.config import settings
from backend.app.kb import files, remote, store

QUOTE = "Mid-IR, NIR, Raman, and fluorescence spectra"


@pytest.fixture
def kb(tmp_path, monkeypatch):
    shutil.copytree(settings.kb_dir, tmp_path / "kb")
    shutil.copytree(settings.raw_dir, tmp_path / "raw")
    saved = {k: getattr(settings, k) for k in ("kb_dir", "raw_dir", "db_path", "kb_edit")}
    for k, v in (("kb_dir", tmp_path / "kb"), ("raw_dir", tmp_path / "raw"), ("db_path", tmp_path / "afs.db")):
        object.__setattr__(settings, k, v)        # Settings is frozen; every module shares this one object
    monkeypatch.setattr(store, "_CON", None)
    monkeypatch.setattr(files, "_local_ready", False)
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    monkeypatch.setattr(files, "start_rebuild", lambda reason: None)     # rebuild tested separately
    remote.reset_for_tests()
    files.clear_caches()
    yield tmp_path
    for k, v in saved.items():
        object.__setattr__(settings, k, v)
    store._CON = None                             # noqa: SLF001
    files.clear_caches()


def _card(page):
    return json.dumps({"id": "C990", "claim": "Same spot.", "source": "S01", "page": page, "quote": QUOTE}) + "\n"


def test_quote_must_be_on_its_page(kb):
    text = (kb / "kb/claims.jsonl").read_text(encoding="utf-8")
    problems, _ = files.check("claims.jsonl", text + _card(5))
    assert problems == ["line 96 (C990): the quote is not on S01 p.5"]
    assert files.check("claims.jsonl", text + _card(8)) == ([], [])


def test_rule_conditions_are_checked_in_every_branch(kb):
    text = (kb / "kb/rules.yaml").read_text(encoding="utf-8")
    assert files.check("rules.yaml", text) == ([], [])
    i = text.index("eq:", text.index("rules:"))
    problems, _ = files.check("rules.yaml", text[:i] + "equals:" + text[i + 3:])
    assert problems and "use exactly one of" in problems[0]


def test_save_versions_and_restore(kb):
    text = (kb / "kb/claims.jsonl").read_text(encoding="utf-8")
    with pytest.raises(files.KBError) as err:
        files.save_kb("claims.jsonl", text + _card(5), "tester")
    assert err.value.problems
    r = files.save_kb("claims.jsonl", text + _card(8), "tester", "add C990")
    assert r["version"] == 2 and "C990" in (kb / "kb/claims.jsonl").read_text(encoding="utf-8")
    assert [h["version"] for h in files.history("kb", "claims.jsonl")] == [2, 1]
    files.restore("kb", "claims.jsonl", 1, "tester")
    assert (kb / "kb/claims.jsonl").read_text(encoding="utf-8") == text
    with pytest.raises(files.KBError) as err:          # someone else saved in between
        files.save_kb("claims.jsonl", text + _card(8), "tester", base_sha="stale")
    assert err.value.status == 409


def test_upload_and_register_a_document(kb):
    import base64
    data = base64.b64encode(b"Oven drying is the reference method for moisture in milk powder.").decode()
    r = files.upload_raw("S07_Note.txt", data, "tester")
    assert r["next_id"] == "S07" and r["registered_as"] is None
    files.register_source({"file": "S07_Note.txt", "title": "Note", "evidence_level": "lab_demonstration"}, "tester")
    from backend.app.config import source_files
    assert source_files()["S07"] == "S07_Note.txt"


def test_evaluation_cases_never_enter_the_knowledge_base(kb):
    import base64
    assert all("scenario" not in f["name"] for f in files.list_files()["raw"])
    with pytest.raises(files.KBError):
        files.upload_raw("customer_scenarios_for_final_evaluation.txt", base64.b64encode(b"x").decode(), "tester")


def test_rebuild_makes_a_change_live(kb, monkeypatch):
    from backend.app.kb import ingest
    ingest.run()
    before = store.local_kb_size()
    text = (kb / "kb/claims.jsonl").read_text(encoding="utf-8")

    def run_now(reason):                          # same as start_rebuild, without the background thread
        assert files._rebuild_lock.acquire(blocking=False)   # noqa: SLF001
        files._rebuild(reason)                    # noqa: SLF001
    monkeypatch.setattr(files, "start_rebuild", run_now)
    files.save_kb("claims.jsonl", text + _card(8), "tester")
    assert files.status()["state"] == "done"
    assert store.local_kb_size() == before + 1


@pytest.mark.parametrize("mode,user,expected", [("pro", None, 401), ("pro", "basic", 403), ("pro", "pro", 200),
                                               ("off", "pro", 403), ("open", None, 200)])
def test_permissions(kb, monkeypatch, mode, user, expected):
    from backend.app.api import kb_admin
    from backend.app.main import app
    object.__setattr__(settings, "kb_edit", mode)
    users = {"basic": {"id": "u1", "email": "b@x", "subscription_tier": "basic"},
             "pro": {"id": "u2", "email": "p@x", "subscription_tier": "pro"}}
    monkeypatch.setattr(kb_admin, "current_user", lambda request: users.get(user))
    assert TestClient(app).get("/api/kb/files").status_code == expected
