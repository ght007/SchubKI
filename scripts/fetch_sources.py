"""Fetch the source PDFs for a hosted build. The PDFs are not in git.

Render runs:  python scripts/fetch_sources.py && python -m backend.app.kb.ingest

SOURCES_URL is a private link (e.g. a Supabase Storage signed URL) to a .zip holding PDFs named as in
data/kb/sources.json. Files are matched by file name; folders and other files in the zip are ignored.
Without SOURCES_URL the script only checks data/raw.

Required (build fails without them, exit 1): the supplied AFS PDFs (S01-S05) and every PDF a curated claim
cites (ingest checks each claim quote against its page, so it would fail anyway).
Optional (warning only): other registered PDFs, e.g. documents uploaded on the Knowledge base page; those
live in Supabase (kb_files) and the server pulls them at startup (kb/files.py sync_from_db).
The URL is a secret and is never printed.
"""
from __future__ import annotations

import io
import json
import os
import sys
import urllib.request
import zipfile
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.config import settings  # noqa: E402

SUPPLIED = {"S01", "S02", "S03", "S04", "S05"}   # the AFS challenge materials


def registered() -> dict[str, str]:
    """{source id: PDF file name} for every registered PDF (data/kb/sources.json)."""
    try:
        from backend.app.config import source_files
        files = source_files()
    except ImportError:                              # older config.py
        from backend.app.config import SOURCE_FILES as files
    return {sid: name for sid, name in files.items() if name.lower().endswith(".pdf")}


def cited_sources() -> set[str]:
    path = settings.kb_dir / "claims.jsonl"
    if not path.exists():
        return set()
    return {json.loads(line)["source"] for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def required() -> list[str]:
    need = SUPPLIED | cited_sources()
    return sorted(name for sid, name in registered().items() if sid in need)


def optional() -> list[str]:
    return sorted(set(registered().values()) - set(required()))


def missing(raw_dir: Path, names: Iterable[str]) -> list[str]:
    return [n for n in names if not (raw_dir / n).is_file() or (raw_dir / n).stat().st_size == 0]


def extract(data: bytes, raw_dir: Path, names: Iterable[str]) -> list[str]:
    """Write the wanted files from a zip into raw_dir, by base name only (no paths from the archive)."""
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise ValueError("SOURCES_URL did not return a .zip file")
    wanted = set(names)
    raw_dir.mkdir(parents=True, exist_ok=True)
    written = []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for info in zf.infolist():
            base = info.filename.replace("\\", "/").rsplit("/", 1)[-1]
            if info.is_dir() or base not in wanted:
                continue
            (raw_dir / base).write_bytes(zf.read(info))
            written.append(base)
    return sorted(written)


def download(url: str, timeout: float = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "schubki-build"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310  (URL comes from our own env)
        return resp.read()


def main() -> int:
    raw_dir = settings.raw_dir
    need, extra = required(), optional()
    url = os.getenv("SOURCES_URL", "").strip()
    if url and missing(raw_dir, need + extra):
        try:
            got = extract(download(url), raw_dir, need + extra)
        except Exception as exc:  # noqa: BLE001
            print(f"fetch_sources: download failed ({type(exc).__name__}: {str(exc)[:200]})", file=sys.stderr)
            return 1
        print(f"fetch_sources: extracted {len(got)} file(s): {', '.join(got)}")
    absent = missing(raw_dir, extra)
    if absent:
        print(f"fetch_sources: warning, not in the build (pulled from Supabase at startup if uploaded "
              f"on the Knowledge base page): {', '.join(absent)}")
    gaps = missing(raw_dir, need)
    if gaps:
        hint = "check the zip contents" if url else "set SOURCES_URL (see docs/DEPLOY.md)"
        print(f"fetch_sources: missing in {raw_dir}: {', '.join(gaps)}; {hint}", file=sys.stderr)
        return 1
    print(f"fetch_sources: all {len(need)} required source PDFs present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
