"""Model choice: only usable chat models are offered, the choice reaches every stage of one run only."""
import pytest

from backend.app.engine import pipeline
from backend.app.llm import models
from backend.app.schemas import AssessRequest


@pytest.fixture
def key_with_models(monkeypatch):
    monkeypatch.setitem(models._status, "available", [
        "openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "allam-2-7b",
        "whisper-large-v3", "canopylabs/orpheus-v1-english", "meta-llama/llama-prompt-guard-2-22m",
        "openai/gpt-oss-safeguard-20b"])


def test_only_chat_models_are_selectable(key_with_models):
    ids = [m["id"] for m in models.selectable()]
    assert {"openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "allam-2-7b"} == set(ids)
    assert next(m for m in models.selectable() if m["id"] == "allam-2-7b")["tested"] is False
    with pytest.raises(ValueError):
        models.validate_choice("whisper-large-v3")
    assert models.validate_choice("auto") is None and models.validate_choice(None) is None


def test_choice_applies_to_every_stage_of_one_run_only(key_with_models):
    run = pipeline.run(AssessRequest(enquiry="Moisture in a powder blend, NIR preferred.", model="qwen/qwen3.8-27b"))
    used = {t.model.replace("mock (", "").rstrip(")") for t in run.trace}
    assert used == {"qwen/qwen3.8-27b"} and run.model_choice == "qwen/qwen3.8-27b"
    assert models.chosen_model() is None                      # reset after the run
    default = pipeline.run(AssessRequest(enquiry="Moisture in a powder blend, NIR preferred."))
    assert default.model_choice == "" and len({t.model for t in default.trace}) == 2   # fast + main