"""
Creates the afs-assistant repo skeleton. Run once, from the folder where you want the repo:

    python scaffold.py

Works on Windows, macOS and Linux. Existing files are never overwritten.
"""
from pathlib import Path

ROOT = Path("afs-assistant")

# path -> one-line purpose (written as a header comment into each stub)
FILES = {
    # ---------- root ----------
    "README.md": "How to install, ingest, run, evaluate. Written at the end.",
    # ---------- data ----------
    "data/raw/.gitkeep": "Put S01-S05 PDFs, S06 txt, xlsx, docx and scenarios txt here.",
    "data/kb/methods.json": "S01 Table 1 (p.6) as JSON, from the xlsx.",
    "data/kb/fibers.json": "Fiber families + transmission ranges (S02 p.6).",
    "data/kb/bands.json": "Spectral band -> typical analytes (S02 band slide).",
    "data/kb/sources.json": "S01-S06 metadata: file, title, type, evidence scope.",
    "data/kb/rules.yaml": "Premise/screening rules, every rule with a source.",
    "data/kb/claims.jsonl": "Curated evidence cards {claim, source, page, quote, scope}.",
    "data/kb/s02_notes.md": "Hand-written notes for the image-only S02 slides.",
    "data/cache/.gitkeep": "Generated: afs.db (SQLite) + rendered page images.",
    # ---------- backend ----------
    "backend/__init__.py": "",
    "backend/app/__init__.py": "",
    "backend/app/main.py": "FastAPI app: routers, static frontend, startup checks.",
    "backend/app/config.py": "Settings from .env: key, model roles, paths, budgets.",
    "backend/app/schemas.py": "All Pydantic models: Requirements, Premise, Report, Quality...",
    "backend/app/api/__init__.py": "",
    "backend/app/api/assess.py": "POST /api/assess (SSE stream), /api/coach, /api/whatif.",
    "backend/app/api/sources.py": "GET page text and highlighted page PNG.",
    "backend/app/api/runs.py": "Runs list/detail, markdown export, feedback, trace.",
    "backend/app/llm/__init__.py": "",
    "backend/app/llm/client.py": "Groq client: JSON schema, validation+retry, 429 backoff, cache, mock.",
    "backend/app/llm/models.py": "Model roles + council list; checks availability at startup.",
    "backend/app/llm/prompts/extract.md": "Prompt: enquiry -> stated / inferred / unknown / premises.",
    "backend/app/llm/prompts/premise.md": "Prompt: judge each client premise against evidence.",
    "backend/app/llm/prompts/report.md": "Prompt: write the structured report with typed claims.",
    "backend/app/llm/prompts/judge.md": "Prompt: blind rubric judging of anonymised drafts.",
    "backend/app/llm/prompts/merge.md": "Prompt: merge best sections into the winning draft.",
    "backend/app/llm/prompts/repair.md": "Prompt: fix the exact quality-check failures.",
    "backend/app/llm/prompts/coach.md": "Prompt: improved enquiry template with blanks.",
    "backend/app/kb/__init__.py": "",
    "backend/app/kb/store.py": "SQLite: chunks, FTS5, vectors, runs, llm_cache, feedback.",
    "backend/app/kb/embed.py": "fastembed wrapper (bge-small-en-v1.5).",
    "backend/app/kb/ingest.py": "PDF/txt -> page chunks -> SQLite (FTS5 + embeddings).",
    "backend/app/kb/retrieve.py": "Multi-query BM25 + dense -> RRF -> MMR -> evidence pack.",
    "backend/app/engine/__init__.py": "",
    "backend/app/engine/extract.py": "Stage 1: requirement extraction.",
    "backend/app/engine/rules.py": "Stage 2: deterministic rules from rules.yaml.",
    "backend/app/engine/coverage.py": "Band <-> method <-> fiber overlap (spectral map data).",
    "backend/app/engine/premise.py": "Stage 4: premise check (rules + LLM).",
    "backend/app/engine/screen.py": "Stage 5: method screening matrix (scored, explained).",
    "backend/app/engine/report.py": "Stage 6: single-model report draft.",
    "backend/app/engine/council.py": "Multi-model drafts -> gates -> blind cross-judge -> merge.",
    "backend/app/engine/verify.py": "Citation exists, quote on page, numbers, client facts.",
    "backend/app/engine/quality.py": "Quality scorecard + one auto-repair round.",
    "backend/app/engine/confidence.py": "Computed confidence level + breakdown + caps.",
    "backend/app/engine/coach.py": "Completeness score, impact-ranked unknowns, template.",
    "backend/app/engine/whatif.py": "Re-run with answers, diff old vs new.",
    "backend/app/engine/pipeline.py": "Orchestrates stages, emits SSE events, saves run.",
    "backend/app/render/__init__.py": "",
    "backend/app/render/markdown.py": "Report JSON -> Markdown (outputs/ and export).",
    # ---------- frontend ----------
    "frontend/index.html": "Single page: header, enquiry/coach, tabs, evidence drawer.",
    "frontend/css/styles.css": "Custom styles on top of Tailwind CDN.",
    "frontend/js/api.js": "fetch + SSE helpers.",
    "frontend/js/state.js": "App state (Alpine store).",
    "frontend/js/app.js": "Boot, wiring, tab switching.",
    "frontend/js/components/header.js": "Status badge, confidence, quality, verified counter.",
    "frontend/js/components/enquiry.js": "Enquiry box, mode toggle, stage progress.",
    "frontend/js/components/coach.js": "Completeness, ranked unknowns, answer + re-run.",
    "frontend/js/components/report.js": "Report sections with typed, clickable claims.",
    "frontend/js/components/matrix.js": "Method screening matrix.",
    "frontend/js/components/spectral-map.js": "SVG band/method/fiber coverage map.",
    "frontend/js/components/evidence.js": "Source drawer: page image with highlight.",
    "frontend/js/components/council.js": "Judge x draft scores, gates, agreement.",
    "frontend/js/components/quality.js": "Quality scorecard.",
    "frontend/js/components/whatif.js": "Decision tree + diff view.",
    "frontend/js/components/trace.js": "LLM calls: model, tokens, latency.",
    # ---------- eval ----------
    "eval/cases/dev_cases.yaml": "D01-D08 enquiries (+ reference answers D01, D02).",
    "eval/cases/final_cases.yaml": "H01-H06 enquiries, exact text.",
    "eval/cases/adversarial_cases.yaml": "Our own trap cases (not H-specific).",
    "eval/run_cases.py": "Run a case set -> outputs/*.md + *.json.",
    "eval/judge.py": "Score outputs against the jury criteria.",
    "eval/summary.py": "Regression table across all cases.",
    # ---------- tests / scripts / docs ----------
    "tests/test_retrieve.py": "RRF / MMR sanity tests.",
    "tests/test_verify.py": "Quote matching, number checks.",
    "tests/test_rules.py": "Fiber coverage + scope rules.",
    "scripts/check_groq.py": "Lists the Groq models your key can use.",
    "docs/architecture.md": "Architecture description for submission.",
    "outputs/.gitkeep": "Generated H01-H06 outputs (do not edit by hand).",
}

CONTENT = {
    ".gitignore": """\
.env
__pycache__/
*.pyc
.venv/
data/cache/*
!data/cache/.gitkeep
.DS_Store
""",
    ".env.example": """\
# Copy to .env and fill in
GROQ_API_KEY=
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Model roles (confirm names with: python scripts/check_groq.py)
MODEL_FAST=openai/gpt-oss-20b
MODEL_MAIN=openai/gpt-oss-120b
COUNCIL_MODELS=openai/gpt-oss-120b,llama-3.3-70b-versatile,moonshotai/kimi-k2-instruct-0905
MODEL_VISION=meta-llama/llama-4-scout-17b-16e-instruct

# 1 = use canned responses, no API calls (offline development)
LLM_MOCK=0
# Free tier: keep each call small
MAX_EVIDENCE_TOKENS=2500

EMBED_MODEL=BAAI/bge-small-en-v1.5
DB_PATH=data/cache/afs.db
RAW_DIR=data/raw
KB_DIR=data/kb
""",
    "requirements.txt": """\
fastapi>=0.115
uvicorn[standard]>=0.30
sse-starlette>=2.1
pydantic>=2.7
python-dotenv>=1.0
openai>=1.50
httpx>=0.27
pymupdf>=1.24
fastembed>=0.4
numpy>=1.26
rapidfuzz>=3.9
pyyaml>=6.0
openpyxl>=3.1
python-docx>=1.1
pytest>=8.0
""",
    "scripts/check_groq.py": '''\
"""Lists the Groq models available to your key.  Run: python scripts/check_groq.py"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["GROQ_API_KEY"],
                base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"))
for m in sorted(client.models.list().data, key=lambda m: m.id):
    print(m.id)
''',
}


def header(path: str, purpose: str) -> str:
    if not purpose:
        return ""
    if path.endswith((".py",)):
        return f'"""{purpose}"""\n'
    if path.endswith((".yaml", ".jsonl")):
        return f"# {purpose}\n" if path.endswith(".yaml") else ""
    if path.endswith((".md",)):
        return f"<!-- {purpose} -->\n"
    if path.endswith(".js"):
        return f"// {purpose}\n"
    if path.endswith(".css"):
        return f"/* {purpose} */\n"
    if path.endswith(".html"):
        return f"<!-- {purpose} -->\n"
    return ""  # .json, .gitkeep: leave empty


def main() -> None:
    made = 0
    for rel, purpose in FILES.items():
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.write_text(CONTENT.get(rel, header(rel, purpose)), encoding="utf-8")
            made += 1
    for rel, text in CONTENT.items():
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.write_text(text, encoding="utf-8")
            made += 1
    print(f"Done: {ROOT.resolve()}  ({made} files written)")


if __name__ == "__main__":
    main()