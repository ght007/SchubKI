"""PDF/txt -> page chunks -> SQLite (FTS5 + embeddings).

Run:  python -m backend.app.kb.ingest

Indexes two kinds of records:
  * chunk  - overlapping windows (~180 words) of every source page, with source/page/scope
  * claim  - each curated evidence card from data/kb/claims.jsonl (claim text + quote)
Before indexing, every claim quote is checked against its page; ingest stops if one fails.
"""
from __future__ import annotations

import json
import re
import sys
import time

from ..config import settings
from . import embed, store
from .pages import load_pages, quote_on_page

WINDOW = 180   # words per chunk
STRIDE = 120   # overlap of 60 words


def _scope_of(source: str) -> str:
    try:
        reg = json.loads((settings.kb_dir / "sources.json").read_text(encoding="utf-8"))
        return next((s["evidence_level"] for s in reg["sources"] if s["id"] == source), "unknown")
    except Exception:
        return "unknown"


def load_claims() -> list[dict]:
    path = settings.kb_dir / "claims.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def check_claims(claims: list[dict]) -> list[str]:
    return [c["id"] for c in claims if not quote_on_page(c["quote"], c["source"], c["page"])]


def windows(text: str) -> list[str]:
    words = re.sub(r"\s+", " ", text).strip().split(" ")
    if len(words) <= WINDOW:
        return [" ".join(words)] if words and words[0] else []
    out = []
    for start in range(0, len(words), STRIDE):
        out.append(" ".join(words[start:start + WINDOW]))
        if start + WINDOW >= len(words):
            break
    return out


def run() -> dict:
    t0 = time.time()
    pages = load_pages()
    if not pages:
        raise SystemExit(f"No sources found in {settings.raw_dir}. Copy S01-S06 there first.")
    claims = load_claims()
    bad = check_claims(claims)
    if bad:
        raise SystemExit(f"Claim quotes not found on their pages: {bad}")

    store.reset_kb()
    ids, texts = [], []
    for (source, page), text in sorted(pages.items()):
        scope = _scope_of(source)
        for w in windows(text):
            if len(w) < 40:
                continue
            ids.append(store.add_chunk("chunk", source, page, w, scope=scope))
            texts.append(w)
    for c in claims:
        text = f"{c['claim']} Quote: \"{c['quote']}\" Topics: {', '.join(c.get('topics', []))}"
        ids.append(store.add_chunk("claim", c["source"], c["page"], text, quote=c["quote"],
                                   scope=c.get("scope"), claim_id=c["id"]))
        texts.append(text)

    vecs = embed.embed(texts)
    store.add_vectors(ids, vecs)
    store.clear_vector_cache()
    store.set_meta("embed_backend", embed.backend())
    store.set_meta("ingested_at", time.strftime("%Y-%m-%dT%H:%M:%S"))
    stats = {"pages": len(pages), "records": len(ids), "claims": len(claims),
             "embed_backend": embed.backend(), "seconds": round(time.time() - t0, 1)}
    store.set_meta("ingest_stats", json.dumps(stats))
    return stats


if __name__ == "__main__":
    logging_ok = "-q" not in sys.argv
    print(json.dumps(run(), indent=2))
