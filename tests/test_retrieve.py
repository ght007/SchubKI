"""RRF / MMR sanity tests."""
import numpy as np

from backend.app.kb.retrieve import mmr, rrf


def test_rrf_rewards_agreement():
    scores = rrf([[1, 2, 3], [2, 1, 4], [2, 5, 6]])
    assert max(scores, key=scores.get) == 2          # ranked high by all lists
    assert scores[1] > scores[3]


def test_mmr_prefers_diverse_items():
    v = {1: np.array([1.0, 0.0]), 2: np.array([0.999, 0.045]), 3: np.array([0.0, 1.0])}
    v = {k: x / np.linalg.norm(x) for k, x in v.items()}
    picked = mmr([1, 2, 3], {1: 1.0, 2: 0.95, 3: 0.6}, v, lam=0.5, top_n=2)
    assert picked == [1, 3]                           # near-duplicate 2 is skipped
