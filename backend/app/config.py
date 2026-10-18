"""Settings from .env: key, model roles, paths, budgets."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]  # repo root (afs-assistant/)
load_dotenv(ROOT / ".env")


def _path(env: str, default: str) -> Path:
    p = Path(os.getenv(env, default))
    return p if p.is_absolute() else ROOT / p


def _list(env: str, default: str) -> list[str]:
    return [x.strip() for x in os.getenv(env, default).split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    model_fast: str = os.getenv("MODEL_FAST", "openai/gpt-oss-20b")
    model_main: str = os.getenv("MODEL_MAIN", "openai/gpt-oss-120b")
    council_models: list[str] = field(default_factory=lambda: _list(
        "COUNCIL_MODELS", "openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b"))
    model_guard: str = os.getenv("MODEL_GUARD", "")

    llm_mock: bool = os.getenv("LLM_MOCK", "0") == "1"
    llm_cache: bool = os.getenv("LLM_CACHE", "1") == "1"
    llm_timeout_s: float = float(os.getenv("LLM_TIMEOUT_S", "90"))
    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "4"))
    max_evidence_tokens: int = int(os.getenv("MAX_EVIDENCE_TOKENS", "2500"))

    embed_model: str = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
    db_path: Path = _path("DB_PATH", "data/cache/afs.db")
    raw_dir: Path = _path("RAW_DIR", "data/raw")
    kb_dir: Path = _path("KB_DIR", "data/kb")
    cache_dir: Path = _path("CACHE_DIR", "data/cache")
    outputs_dir: Path = _path("OUTPUTS_DIR", "outputs")
    frontend_dir: Path = ROOT / "frontend"
    prompts_dir: Path = ROOT / "backend" / "app" / "llm" / "prompts"

    # Accounts (optional login). Only the public client id is needed for Google sign-in, not the secret.
    google_client_ids: list[str] = field(default_factory=lambda: _list("GOOGLE_CLIENT_ID", ""))
    session_days: int = int(os.getenv("SESSION_DAYS", "30"))
    # 1 = the assistant (/app) needs a login and / opens the login page; 0 = open guest app (demo fallback)
    auth_required: bool = os.getenv("AUTH_REQUIRED", "1") == "1"
    # demo = plan buttons switch the plan at once without payment; off = refuse until payments are connected
    billing_mode: str = os.getenv("BILLING_MODE", "demo").strip().lower()
    # Knowledge-base editor: pro = logged-in Pro users (default), open = anyone (local demo), off = nobody
    kb_edit: str = os.getenv("KB_EDIT", "pro").strip().lower()


settings = Settings()

# Source id -> raw file name. S02 text comes from the transcription notes.
# Document types the page loader can read (kb/pages.py). Spreadsheets (the method table T1) are curated
# into methods.json by hand and are not searched as pages.
READABLE_SOURCE_TYPES = (".pdf", ".txt", ".md", ".docx")


def source_files() -> dict[str, str]:
    """{source id: file name in data/raw} for every readable document registered in data/kb/sources.json.
    Read on every call (small file), so a document registered in the knowledge-base editor is used at once."""
    import json
    try:
        reg = json.loads((settings.kb_dir / "sources.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {s["id"]: s["file"] for s in reg.get("sources", [])
            if s.get("file", "").lower().endswith(READABLE_SOURCE_TYPES)}