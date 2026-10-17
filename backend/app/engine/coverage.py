"""Band <-> method <-> fiber overlap (spectral map data).

Pure arithmetic on the ranges in methods.json, fibers.json and bands.json (S01, S02 p.6,
S02 p.18). This is what makes "silica cannot carry MIR" visible on the spectral map.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from ..config import settings
from ..schemas import FiberFit, MethodCoverage, Requirements

SILICA_WORDS = ("silica", "vis-nir", "visible", "nir cable", "nir fiber", "nir fibre", "glass fiber",
                "glass fibre", "vis/nir", "visible or nir")


@lru_cache(maxsize=1)
def kb() -> dict:
    load = lambda n: json.loads((settings.kb_dir / n).read_text(encoding="utf-8"))  # noqa: E731
    return {"methods": load("methods.json"), "fibers": load("fibers.json")["fibers"], "bands": load("bands.json")}


def method_range(method_id: str) -> tuple[float, float]:
    m = next(m for m in kb()["methods"]["methods"] if m["id"] == method_id)
    lo, hi = m["nominal_range"]["um"]
    return float(lo), float(hi)


def _fit(rng: tuple[float, float], fiber: dict) -> FiberFit:
    lo, hi = rng
    flo, fhi = fiber["range_um"]
    olo, ohi = max(lo, flo), min(hi, fhi)
    if ohi <= olo:
        covers, overlap = "none", None
    elif flo <= lo and fhi >= hi:
        covers, overlap = "full", (olo, ohi)
    else:
        covers, overlap = "partial", (olo, ohi)
    return FiberFit(fiber_id=fiber["id"], name=fiber["name"], range_um=(flo, fhi), overlap_um=overlap, covers=covers)


def has_silica_asset(req: Requirements) -> bool:
    from .glossary import expand
    text = expand(" ".join(req.existing_assets)).lower()
    return any(w in text for w in SILICA_WORDS)


def compute(req: Requirements) -> list[MethodCoverage]:
    silica = has_silica_asset(req)
    out = []
    for m in kb()["methods"]["methods"]:
        rng = method_range(m["id"])
        fits = [_fit(rng, f) for f in kb()["fibers"]]
        asset = None
        if silica:
            silica_max = max(f["range_um"][1] for f in kb()["fibers"] if f["family"] == "silica")
            if rng[0] >= silica_max:
                asset = (f"Client's silica fiber reaches about {silica_max} um; {m['name']} starts at "
                         f"{rng[0]} um, so the existing silica link cannot carry this method [S02 p.6].")
        out.append(MethodCoverage(method_id=m["id"], method_range_um=rng, fibers=fits, asset_check=asset))
    return out


def bands_for(req: Requirements, enquiry: str) -> list[dict]:
    """Bands from bands.json whose analytes appear in the targets / enquiry."""
    from .glossary import expand
    text = expand(" ".join(req.target_variables) + " " + enquiry + " " + req.matrix).lower()
    hits = []
    for b in kb()["bands"]["bands"]:
        if "range_um" not in b:
            continue
        matched = []
        for a in b["analytes"]:
            words = [w for w in re.findall(r"[a-z0-9]+", a.lower()) if w not in ("in", "of", "and", "the")]
            if words and all(re.search(rf"\b{re.escape(w)}s?\b", text) for w in words):
                matched.append(a)
        if matched:
            hits.append({**b, "matched": matched})
    return hits


def spectral_map(req: Requirements, enquiry: str) -> dict:
    """Everything the frontend needs to draw the coverage map."""
    return {
        "methods": [{"id": m["id"], "name": m["name"], "range_um": m["nominal_range"]["um"],
                     "label": m["nominal_range"]["label"], "source": f"{m['nominal_range']['source']} p.{m['nominal_range']['page']}"}
                    for m in kb()["methods"]["methods"]],
        "fibers": [{"id": f["id"], "name": f["name"], "range_um": f["range_um"], "family": f["family"]}
                   for f in kb()["fibers"]],
        "bands": bands_for(req, enquiry),
        "client_silica": has_silica_asset(req),
    }