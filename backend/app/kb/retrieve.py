"""Multi-query BM25 + dense -> RRF -> MMR -> evidence pack.

1. Several queries (built from the extracted requirements) are run through two
   rankers: keyword search (Postgres full text in Supabase, or SQLite FTS5 BM25 locally) and dense
   cosine similarity (pgvector in Supabase, or numpy locally). kb/store.py decides which.
2. All rankings are fused with Reciprocal Rank Fusion: score(d) = sum 1/(k + rank).
3. Maximal Marginal Relevance picks a relevant but non-redundant subset within a
   token budget (important on the Groq free tier).
4. Pinned evidence (claims on pages cited by fired rules) is always included first.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np

from ..config import settings
from ..schemas import Evidence
from . import embed, store

RRF_K = 60
MMR_LAMBDA = 0.7
PER_RANKER_K = 25


def rrf(rankings: list[list[int]], k: int = RRF_K) -> dict[int, float]:
    scores: dict[int, float] = defaultdict(float)
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            scores[doc] += 1.0 / (k + rank)
    return dict(scores)


def mmr(candidates: list[int], relevance: dict[int, float], vecs: dict[int, np.ndarray],
        lam: float = MMR_LAMBDA, top_n: int = 10) -> list[int]:
    """Greedy MMR: lam * relevance - (1 - lam) * max similarity to already selected."""
    if not candidates:
        return []
    rel = np.array([relevance[c] for c in candidates])
    rel = (rel - rel.min()) / (rel.max() - rel.min() + 1e-9)
    rel_of = dict(zip(candidates, rel))
    selected: list[int] = []
    pool = list(candidates)
    while pool and len(selected) < top_n:
        best, best_score = None, -1e9
        for c in pool:
            div = max((float(vecs[c] @ vecs[s]) for s in selected), default=0.0)
            score = lam * rel_of[c] - (1 - lam) * div
            if score > best_score:
                best, best_score = c, score
        selected.append(best)
        pool.remove(best)
    return selected


def _tokens(text: str) -> int:
    return int(len(text.split()) * 1.35) + 8


_STOP = {"the", "and", "for", "with", "that", "this", "from", "are", "can", "into", "which", "such", "than", "have",
         "has", "its", "their", "used", "use", "using", "also", "more", "most", "not", "only", "unknown"}


def best_sentence(text: str, queries: list[str]) -> str | None:
    """The sentence of a chunk that best matches the queries (for highlighting what was retrieved).
    Score = query words found in the sentence, lightly normalised by sentence length."""
    import math
    import re

    qwords = {w for q in queries for w in re.findall(r"[a-z0-9]{3,}", q.lower())} - _STOP
    if not qwords:
        return None
    best, best_score = None, 0.0
    for sent in re.split(r"(?<=[.!?;])\s+|\s+-\s+", text):
        sent = sent.strip(' "')
        if not 30 <= len(sent) <= 400:
            continue
        words = set(re.findall(r"[a-z0-9]{3,}", sent.lower()))
        hits = len(words & qwords)
        score = hits / math.sqrt(max(4, len(words)))
        if hits >= 2 and score > best_score:
            best, best_score = sent, score
    return best


def dense_search(query_vec: np.ndarray, k: int = PER_RANKER_K) -> list[int]:
    return store.dense_search(query_vec, k)


def retrieve(queries: list[str], pinned_pages: list[tuple[str, int]] | None = None,
             budget_tokens: int | None = None, max_items: int = 14) -> tuple[list[Evidence], dict]:
    budget = budget_tokens or settings.max_evidence_tokens
    queries = [q for q in dict.fromkeys(q.strip() for q in queries) if q]
    debug: dict = {"queries": queries, "bm25": {}, "dense": {}, "fused": [], "mmr": [], "pinned": []}

    rankings: list[list[int]] = []
    qvecs = embed.embed(queries, is_query=True) if queries else np.zeros((0, 1))
    for q, qv in zip(queries, qvecs):
        b = [doc for doc, _ in store.bm25_search(q, PER_RANKER_K)]
        d = dense_search(qv)
        rankings += [b, d]
        debug["bm25"][q], debug["dense"][q] = b[:8], d[:8]
    fused = rrf(rankings)
    candidates = sorted(fused, key=fused.get, reverse=True)[:40]
    debug["fused"] = [(c, round(fused[c], 4)) for c in candidates[:15]]

    index = store.get_vectors(candidates)
    candidates = [c for c in candidates if c in index]
    picked = mmr(candidates, fused, index, top_n=max_items * 2)
    debug["mmr"] = picked

    # pinned: claims sitting on pages that fired rules cite
    pinned: list[int] = store.claims_on_pages(sorted(set(pinned_pages))) if pinned_pages else []
    debug["pinned"] = pinned
    debug["backend"] = "supabase" if store.kb_online() else "local"

    rows = store.get_chunks(list(dict.fromkeys(pinned + picked)))
    evidence: list[Evidence] = []
    used = 0
    for cid in dict.fromkeys(pinned[:8] + picked):
        r = rows.get(cid)
        if not r:
            continue
        text = r["text"] if r["kind"] == "chunk" else r["text"].split(" Topics:")[0]
        cost = _tokens(text)
        if used + cost > budget and evidence:
            continue
        used += cost
        evidence.append(Evidence(ref=f"E{len(evidence) + 1}", kind=r["kind"], source=r["source"],
                                 page=r["page"], text=text, quote=r["quote"], scope=r["scope"],
                                 highlight=best_sentence(text, queries) if r["kind"] == "chunk" else None,
                                 score=round(fused.get(cid, 0.0), 4)))
        if len(evidence) >= max_items:
            break
    debug["used_tokens"] = used
    return evidence, debug