"""Page-level text of every source, plus the text normaliser used for quote matching.

S02 is image-based, so its page text is the PDF text plus the transcription in
data/kb/s02_notes.md. Everything that checks a quote goes through `normalize`.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

from ..config import SOURCE_FILES, settings

_QUOTES = {"‘": "'", "’": "'", "“": '"', "”": '"', "´": "'",
           "−": "-", "‐": "-", "‑": "-", "­": ""}


def normalize(text: str) -> str:
    """NFKC (ligatures, micro sign), unify quotes and minus signs, collapse whitespace, lowercase."""
    text = unicodedata.normalize("NFKC", text)
    for a, b in _QUOTES.items():
        text = text.replace(a, b)
    text = text.replace("µ", "u").replace("μ", "u")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\w)- (\w)", r"\1-\2", text)  # "well-\nsuited" line-break artefacts
    return text.strip().lower()


def _parse_s02_notes() -> dict[int, str]:
    path = settings.kb_dir / "s02_notes.md"
    notes: dict[int, str] = {}
    if not path.exists():
        return notes
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## S02 p\.(\d+)", line)
        if m:
            current = int(m.group(1))
            notes[current] = ""
        elif current is not None:
            notes[current] += line + "\n"
    return notes


@lru_cache(maxsize=1)
def load_pages() -> dict[tuple[str, int], str]:
    """{(source_id, page): raw page text}. Pages are 1-based PDF pages."""
    import pymupdf  # imported lazily so the rest of the app works without it

    pages: dict[tuple[str, int], str] = {}
    s02_notes = _parse_s02_notes()
    for sid, fname in SOURCE_FILES.items():
        path = settings.raw_dir / fname
        if not path.exists():
            continue
        if path.suffix == ".txt":
            pages[(sid, 1)] = path.read_text(encoding="utf-8")
            continue
        with pymupdf.open(path) as doc:
            for i, page in enumerate(doc, start=1):
                text = page.get_text()
                if sid == "S02":
                    text = f"{s02_notes.get(i, '')}\n[PDF text]\n{text}"
                pages[(sid, i)] = text
    return pages


@lru_cache(maxsize=1)
def normalized_pages() -> dict[tuple[str, int], str]:
    return {k: normalize(v) for k, v in load_pages().items()}


def page_text(source: str, page: int) -> str | None:
    return load_pages().get((source, page))


def quote_on_page(quote: str, source: str, page: int) -> bool:
    """Exact (normalised) substring check."""
    norm = normalized_pages().get((source, page))
    return bool(norm) and normalize(quote) in norm
