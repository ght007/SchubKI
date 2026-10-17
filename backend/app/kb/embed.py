"""fastembed wrapper (bge-small-en-v1.5), with an offline fallback.

The first run downloads the ONNX model (~130 MB) from Hugging Face. If that is not
possible (no network, blocked proxy), a deterministic hashing embedder of word and
character n-grams is used instead, so dense retrieval keeps working. The active
backend is stored in the DB meta table and shown in /api/health.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re

import numpy as np

from ..config import settings

log = logging.getLogger(__name__)
_DIM_FALLBACK = 1024
_model = None
_backend = None  # "fastembed:<name>" | "hashing"


def _load():
    global _model, _backend
    if _backend is not None:
        return
    if os.getenv("EMBED_BACKEND", "").lower() == "hashing":
        _model, _backend = None, "hashing"
        return
    try:
        from fastembed import TextEmbedding

        _model = TextEmbedding(model_name=settings.embed_model, cache_dir=str(settings.cache_dir / "models"))
        _backend = f"fastembed:{settings.embed_model}"
    except Exception as exc:  # network / install problems
        log.warning("fastembed unavailable (%s); using hashing embedder", exc)
        _model, _backend = None, "hashing"


def backend() -> str:
    _load()
    return _backend or "hashing"


def _hash_embed(texts: list[str]) -> np.ndarray:
    out = np.zeros((len(texts), _DIM_FALLBACK), dtype=np.float32)
    for i, t in enumerate(texts):
        t = t.lower()
        words = re.findall(r"[a-z0-9]+", t)
        feats = words + [f"{a}_{b}" for a, b in zip(words, words[1:])]
        for w in words:
            padded = f" {w} "
            feats += [padded[j:j + 4] for j in range(max(1, len(padded) - 3))]
        for f in feats:
            h = int(hashlib.md5(f.encode()).hexdigest()[:8], 16)
            out[i, h % _DIM_FALLBACK] += 1.0 if (h >> 31) & 1 == 0 else -1.0
    norms = np.linalg.norm(out, axis=1, keepdims=True) + 1e-9
    return out / norms


def embed(texts: list[str], is_query: bool = False) -> np.ndarray:
    """L2-normalised embeddings, shape (n, d)."""
    _load()
    if _model is None:
        return _hash_embed(texts)
    if is_query and "bge" in settings.embed_model.lower():
        texts = [f"Represent this sentence for searching relevant passages: {t}" for t in texts]
    vecs = np.array(list(_model.embed(texts)), dtype=np.float32)
    return vecs / (np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9)
