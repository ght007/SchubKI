"""GET page text and highlighted page PNG."""
from __future__ import annotations

import json
import re

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from ..config import SOURCE_FILES, settings
from ..kb.pages import load_pages, normalize, quote_on_page

router = APIRouter(prefix="/api/source")


def _registry() -> dict:
    data = json.loads((settings.kb_dir / "sources.json").read_text(encoding="utf-8"))
    return {s["id"]: s for s in data["sources"]}


@router.get("")
def list_sources():
    pages = load_pages()
    reg = _registry()
    out = []
    for sid in SOURCE_FILES:
        n = sum(1 for (s, _) in pages if s == sid)
        out.append({**reg.get(sid, {"id": sid}), "pages_loaded": n})
    return out


@router.get("/{doc}/{page}")
def page_text(doc: str, page: int, q: str = ""):
    text = load_pages().get((doc, page))
    if text is None:
        raise HTTPException(404, f"{doc} p.{page} not found")
    return {"source": doc, "page": page, "text": text, "meta": _registry().get(doc, {}),
            "quote_found": quote_on_page(q, doc, page) if q else None,
            "transcribed": doc == "S02"}


_IMG_CACHE: dict[tuple, bytes] = {}


def _fragments(quote: str) -> list[str]:
    """Split a quote into searchable fragments (PDF line breaks defeat long searches)."""
    words = quote.split()
    if len(words) <= 8:
        return [quote]
    return [" ".join(words[i:i + 6]) for i in range(0, len(words), 6) if len(words[i:i + 6]) >= 3]


@router.get("/{doc}/{page}/image")
def page_image(doc: str, page: int, q: str = Query("", max_length=600), zoom: float = 1.6):
    if doc not in SOURCE_FILES or not SOURCE_FILES[doc].endswith(".pdf"):
        raise HTTPException(404, "No page image for this source")
    key = (doc, page, q, zoom)
    if key in _IMG_CACHE:
        return Response(_IMG_CACHE[key], media_type="image/png")
    import pymupdf

    path = settings.raw_dir / SOURCE_FILES[doc]
    with pymupdf.open(path) as pdf:
        if not 1 <= page <= len(pdf):
            raise HTTPException(404, "Page out of range")
        p = pdf[page - 1]
        found = 0
        if q:
            clean = re.sub(r"\s+", " ", q).strip()
            for frag in _fragments(clean):
                for rect in p.search_for(frag):
                    annot = p.add_highlight_annot(rect)
                    annot.set_colors(stroke=(1.0, 0.85, 0.2))
                    annot.update()
                    found += 1
        pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), annots=True)
        data = pix.tobytes("png")
    if len(_IMG_CACHE) > 200:
        _IMG_CACHE.clear()
    _IMG_CACHE[key] = data
    return Response(data, media_type="image/png", headers={"X-Highlights": str(found)})
