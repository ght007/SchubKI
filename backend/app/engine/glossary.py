"""Glossary: recognise domain terms and aliases (English and German) in free text.

Used by the pre-check, search expansion, band matching, the keyword extractor and the
rule context, and served to the UI for tooltips. Matching is whole-word and case-insensitive.
"""
from __future__ import annotations

import re
from functools import lru_cache

import yaml

from ..config import settings


@lru_cache(maxsize=1)
def entries() -> list[dict]:
    path = settings.kb_dir / "glossary.yaml"
    if not path.exists():
        return []
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("terms", [])


@lru_cache(maxsize=1)
def _patterns() -> list[tuple[re.Pattern, dict, str]]:
    """(compiled pattern, entry, surface form), longest forms first so 'water in oil' beats 'water'."""
    forms = []
    for e in entries():
        for form in [e["term"], *e.get("aliases", [])]:
            forms.append((form, e))
    forms.sort(key=lambda x: -len(x[0]))
    out = []
    for form, e in forms:
        pat = re.compile(rf"(?<![\w-]){re.escape(form)}(?![\w-])", re.IGNORECASE)
        out.append((pat, e, form))
    return out


def find(text: str) -> list[dict]:
    """Recognised terms with position. Overlapping matches keep the longest form."""
    taken: list[tuple[int, int]] = []
    hits = []
    for pat, e, form in _patterns():
        for m in pat.finditer(text or ""):
            s, t = m.span()
            if any(s < b and t > a for a, b in taken):
                continue
            taken.append((s, t))
            hits.append({"term": e["term"], "matched": m.group(0), "start": s, "end": t,
                         "category": e["category"], "definition": e.get("definition", ""),
                         "source": e.get("source"), "ask": e.get("ask")})
    hits.sort(key=lambda h: h["start"])
    return hits


def canonical_terms(text: str) -> list[str]:
    """Distinct canonical terms found in the text (aliases resolved), in order of appearance."""
    return list(dict.fromkeys(h["term"] for h in find(text) if h["category"] != "vague"))


def expand(text: str) -> str:
    """Text plus the canonical form (and first English alias) of every recognised alias.
    'Feuchte im Pulver' -> '... moisture water content powder powder blend'. Used for search and rules."""
    extra = []
    for h in find(text):
        if h["category"] == "vague":
            continue
        e = next(x for x in entries() if x["term"] == h["term"])
        if h["matched"].lower() != e["term"].lower():
            extra.append(e["term"])
            english = [a for a in e.get("aliases", []) if a.isascii()][:1]
            extra += english
    return text if not extra else f"{text} {' '.join(dict.fromkeys(extra))}"


def public() -> list[dict]:
    """Glossary for the UI (tooltips)."""
    return [{"term": e["term"], "aliases": e.get("aliases", []), "category": e["category"],
             "definition": e.get("definition", ""), "source": e.get("source")} for e in entries()]
