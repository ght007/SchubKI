"""Fetch the AFS source PDFs (S01-S05) for a hosted build. The PDFs are not in git.

Render runs:  python scripts/fetch_sources.py && python -m backend.app.kb.ingest

SOURCES_URL is a private link (e.g. a Supabase Storage signed URL) to a .zip holding the PDFs named as in
SOURCE_FILES (backend/app/config.py). Files are matched by file name; folders and other files in the zip
are ignored. Without SOURCES_URL the script only checks that the PDFs are already in data/raw.
Exit code 1 = a source is missing, so the build stops instead of deploying an empty knowledge base.
The URL is a secret and is never printed.
"""
from __future__ import annotations

import io
import os
import sys
import urllib.request
import zipfile
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.config import SOURCE_FILES, settings  # noqa: E402


def required() -> list[str]:
    return sorted(name for name in SOURCE_FILES.values() if name.lower().endswith(".pdf"))


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
    names, raw_dir = required(), settings.raw_dir
    url = os.getenv("SOURCES_URL", "").strip()
    if url and missing(raw_dir, names):
        try:
            got = extract(download(url), raw_dir, names)
        except Exception as exc:  # noqa: BLE001
            print(f"fetch_sources: download failed ({type(exc).__name__}: {str(exc)[:200]})", file=sys.stderr)
            return 1
        print(f"fetch_sources: extracted {len(got)} file(s): {', '.join(got)}")
    gaps = missing(raw_dir, names)
    if gaps:
        hint = "check the zip contents" if url else "set SOURCES_URL (see docs/DEPLOY.md)"
        print(f"fetch_sources: missing in {raw_dir}: {', '.join(gaps)}; {hint}", file=sys.stderr)
        return 1
    print(f"fetch_sources: all {len(names)} source PDFs present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
