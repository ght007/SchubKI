# AFS Assessment Assistant

**An AI assistant for the first technical assessment of in-line spectroscopy enquiries.**
Built for the Art Fiber Systems (AFS) challenge, *National AI Hackathon 2026 by SchubKI*.

An industrial customer writes a few sentences: what they want to monitor, where, and what they
already have. The assistant turns that into a structured, **reviewable** starting point for an AFS
expert:

1. what the customer actually said, and what is still unknown;
2. whether the customer's own assumptions hold up against the AFS material;
3. the clarification questions that would change the decision, highest impact first;
4. which spectroscopy methods (or combinations) are worth testing, and why, with **verified citations**;
5. a probe / measurement concept and the relevant spectral range;
6. risks, uncertainty, and a **computed** confidence level;
7. a practical first feasibility experiment, mapped onto the AFS pathway (lab trial → Path A / B / C).

The assistant does not replace the expert. It structures the first customer discussion and makes every
step easy to check.

It also offers:
- **Two views**: a compact *General* view for internal non-experts (default) and the full *Expert* workbench.
- **A pre-check with a glossary** (English and German): before any tokens are spent, recognised terms, vague
  words and early warnings (e.g. silica fiber for MIR) are shown; the expert's answers travel as a separate block.
- **A traceable AFS pathway**: a sourced, deterministic suggestion of Path A / B / C; the expert and the customer
  can ask for paths, each gets a fit verdict, and premature paths get an "If you proceed anyway" plan.

---

## Contents

1. [Why it is built this way](#1-why-it-is-built-this-way)
2. [How it maps to the evaluation criteria](#2-how-it-maps-to-the-evaluation-criteria)
3. [Architecture](#3-architecture)
4. [The pipeline, stage by stage](#4-the-pipeline-stage-by-stage)
5. [Knowledge base and use of the AFS materials](#5-knowledge-base-and-use-of-the-afs-materials)
6. [Retrieval: BM25 + dense, RRF, MMR](#6-retrieval-bm25--dense-rrf-mmr)
7. [Grounding: verifier, quality gate, confidence](#7-grounding-verifier-quality-gate-confidence)
8. [Council mode (multi-model)](#8-council-mode-multi-model)
9. [Enquiry coach and what-if](#9-enquiry-coach-and-what-if)
10. [The user interface](#10-the-user-interface)
11. [Installation](#11-installation)
12. [Running the app](#12-running-the-app)
13. [Evaluation and reproducing the outputs](#13-evaluation-and-reproducing-the-outputs)
14. [Configuration](#14-configuration)
15. [Groq free tier: what to expect](#15-groq-free-tier-what-to-expect)
16. [API reference](#16-api-reference)
17. [Repository layout](#17-repository-layout)
18. [Troubleshooting](#18-troubleshooting)
19. [Limitations and honest caveats](#19-limitations-and-honest-caveats)
20. [Future work](#20-future-work)
21. [How the numbers work, and how the knowledge base grows](#21-how-the-numbers-work-and-how-the-knowledge-base-grows)

---

## 1. Why it is built this way

The challenge material says it plainly: *"Some enquiries ask for more certainty than the facts allow.
A good answer notices this and says so."* and *"Insufficient information can be the right answer."*

A language model on its own is fluent, confident and occasionally wrong, which is the opposite of what
an expert needs. So the system is split:

| Job | Done by | Why |
|---|---|---|
| Physics and scope facts (which fiber carries which wavelength, which method needs which precondition, what a study can prove) | **Deterministic rules** written from the AFS sources | Cannot hallucinate; every rule cites its page |
| Method screening scores | **Deterministic** sums of sourced rule contributions | Every point in the matrix is traceable |
| Finding relevant passages | **Hybrid retrieval** (BM25 + embeddings, RRF, MMR) | Small prompts, relevant and diverse evidence |
| Reading the enquiry, judging premises, writing the report | **Language model** (Groq) | Language understanding and clear explanation |
| Checking the report | **Deterministic verifier + quality gate** | The model's text is checked against the pages before anyone sees it |
| Confidence | **Computed** from observable signals | A model rating itself is not calibrated |

If the model is unavailable, every stage has a rule-based fallback, so the app still produces a complete,
cited (and clearly labelled) assessment.

## 2. How it maps to the evaluation criteria

| Criterion (weight) | What the assistant does |
|---|---|
| **Technical quality (30%)** | Rules encode the physics (fiber transmission, sample optics → probe geometry, method preconditions). Method screening is computed, then explained. Council mode lets several models cross-check. |
| **Use of AFS knowledge (20%)** | 95 curated evidence cards with verbatim quotes from S01–S05, 35 sourced rules, the S01 Table 1 (xlsx), S02 fiber chart and band slide, and a full transcription of the image-only S02 slides. Every sourced sentence carries `[Sxx p.N]` and its quote. |
| **Feasibility-study plan (15%)** | Every report has representative samples, independent reference measurements, what is compared (methods, geometries, single vs combined models) and a client-agreed decision basis, plus the AFS pathway step. |
| **Clarification & uncertainty (15%)** | Premise check first; decision status (`provisional_assessment` / `insufficient_information` / `outside_supported_scope`); questions ranked by impact; computed confidence with caps; enquiry coach and what-if re-runs. |
| **Explainability (10%)** | Every statement is typed (client fact / sourced / assumption / proposal). Click a citation to see the highlighted passage on the original PDF page. Matrix, rules, retrieval and every LLM call are visible. |
| **Prototype & presentation (10%)** | One-command web app, live streaming of pipeline stages, Markdown export, works offline in rule-only mode. |

## 3. Architecture

```
                          ┌─────────────────────────── Browser (frontend/, no build step) ───────────────────────────┐
                          │ enquiry · numbered dots on a spectrum pipeline line · four tabs                         │
                          │ Reading · Result Assessment (grounded sources) · Confidence · Coach                      │
                          │ source drawer (PDF page with highlighted quote)                                          │
                          └──────────────────────────────────────┬───────────────────────────────────────────────────┘
                                                                 │ HTTP + SSE (stage, stage_result, result)
┌────────────────────────────────────────────────── FastAPI (backend/app) ──────────────────────────────────────────────┐
│ api/assess.py  api/sources.py  api/runs.py                                                                            │
│                                                                                                                       │
│ engine/pipeline.py ─► extract ─► rules + coverage + screen ─► retrieve ─► premise ─► report | council                 │
│                                   (deterministic)             (kb/)                    │                              │
│                       ◄─ confidence ◄─ coach ◄─ quality gate (+1 repair) ◄─ verify ◄───┘                              │
│                                                                                                                       │
│ llm/client.py: Groq (OpenAI-compatible), JSON schema output, validation + retry, 429/413 handling, cache, fallback   │
└───────────────┬───────────────────────────────────────────────┬───────────────────────────────────────────────────────┘
                │                                               │
     data/cache/afs.db (SQLite)                         data/kb/ (curated knowledge)          data/raw/ (AFS materials)
     FTS5 BM25 · embeddings · runs ·                    claims · rules · methods · fibers ·    S01–S06, xlsx, docx,
     LLM cache · expert feedback                        bands · sources · S02 transcription    scenarios
```

**Stack:** Python 3.12 · FastAPI · Pydantic · SQLite (FTS5) · fastembed (bge-small-en-v1.5, ONNX, CPU) ·
PyMuPDF · rapidfuzz · Groq via the `openai` SDK · vanilla JavaScript ES modules (no framework, no build).

`engine/pipeline.py` emits a `stage_result` after each stage with only that stage's output. The browser
merges those results into the live run. `frontend/js/pipeline-steps.js` supplies one ordered step model
for the single top navigation bar; `components/pipeline.js` renders the corresponding stage views.

**Why SQLite and not a vector database:** about 275 indexed records. Brute-force cosine similarity in
numpy takes microseconds, FTS5 gives BM25 for free, and the whole system runs from one file with one
command. A separate vector service would add setup risk and no benefit at this size.

## 4. The pipeline, stage by stage

The four browser tabs are Reading, Result Assessment, Confidence and Verification, and Coach.
A temporary loading screen shows the current model and rule tasks while the navigation line fills.
Each underlying stage emits `stage` progress
events and a `stage_result` containing its own output when done.
The numbered dots in the top navigation bar follow the active step automatically. They stay hollow
until their step completes, then fill with its visual-spectrum color; the connecting line keeps a color
gradient. Navigation is locked during calculation; the final `result` opens Result Assessment
(or Coach after a what-if re-run) and unlocks the tabs. It
contains the complete run saved in SQLite.

| # | Stage | Module | LLM? | Output |
|---|---|---|---|---|
| 0 | **Pre-check** (before the run) | `engine/precheck.py` | no | Recognised glossary terms, vague words with questions, early blocking warnings, missing facts |
| 1 | **Extract** | `engine/extract.py` | fast model | `Requirements`: stated / inferred / unknown fields, facts with the enquiry's words, unknowns with impact, **client premises** (method claims, reuse claims, evidence claims, certainty requests) |
| 2 | **Rules** | `engine/rules.py` | no | Fired rules from `rules.yaml`: severity (block / warn / info), score contributions, questions, confidence caps, status hints, plan elements, sources |
| 2 | **Coverage** | `engine/coverage.py` | no | Method range ↔ fiber transmission ↔ analyte band overlap; flags incompatible client assets (e.g. silica link for MIR) |
| 2 | **Screen** | `engine/screen.py` | no | Method matrix: score, verdict (lead / candidate / weak / not supported), every contribution with its rule and source |
| 2 | **Paths** | `engine/paths.py` | no | Suggested AFS path from sourced path hints; fit of requested paths (fits / premature / conflicts / open); "proceed anyway" plans |
| 3 | **Retrieve** | `kb/retrieve.py` | no | Evidence pack (≈10–14 passages) within a token budget; chunks carry their best-matching sentence |
| 4 | **Premise check** | `engine/premise.py` | fast model | Each client premise: supported / partly supported / contradicted / unverifiable, with citations |
| 5 | **Report** | `engine/report.py` | main model | Structured `Report` (status, headline, requirements, questions, recommendations, concept, spectral range, risks, plan, pathway) |
| 5 | *or* **Council** | `engine/council.py` | all council models | Several drafts → gates → blind cross-judging → winner + merged sections + agreement |
| 6 | **Verify** | `engine/verify.py` | no | Quote alignment and checks for every citation, number and client fact |
| 7 | **Quality gate** | `engine/quality.py` | fast model for 1 repair | 16 checks; failures sent back once with exact problems |
| 8 | **Coach** | `engine/coach.py` | fast model (template) | Completeness x/10, impact-ranked unknowns, improved enquiry template with [blanks] |
| 8 | **Confidence** | `engine/confidence.py` | no | Level + signals + caps + per-method confidence + "what would raise confidence" |

The run (all of the above, plus the LLM trace and timings) is saved in SQLite and can be reopened at
`http://localhost:8000/#run=<id>` or exported as Markdown.

## 5. Knowledge base and use of the AFS materials

All curated knowledge lives in `data/kb/`. **Nothing in it is written for a specific scenario**; H01–H06
were never used to tune anything.

| File | Content | Built from |
|---|---|---|
| `claims.jsonl` | **95 evidence cards**: `{id, claim, source, page, quote, scope, topics, methods}`. The quote is copied verbatim from the page. | S01 (p.3–19), S02 (slides 3–20), S03, S04, S05 |
| `rules.yaml` | **35 general rules**, each with source pages. Examples: silica fiber cannot carry MIR; calibrations are matrix-specific; adding a method does not keep a calibration valid; fluorescence needs a fluorescent target; optical density is not viable biomass; clinical use exceeds in-vitro evidence; undefined target → insufficient information; geometry by sample optics; application leads (dairy, pharma blends, water in petroleum, hot-melt API, bioprocess, moisture). | S01, S02, S03, S04 |
| `methods.json` | Method profiles (nominal range, geometries, compatible fibers, strengths, limitations, preconditions, each sourced) + all 19 rows of S01 Table 1 + combination notes | `AFS_method_comparison_table.xlsx`, S01 |
| `fibers.json` | UV-VIS silica 0.18–1.2 µm, VIS-NIR silica 0.35–2.4 µm, CIR 1.1–6.5 µm, PIR 3–17 µm, hollow waveguides 2–18 µm, fluoride fibers | S02 p.6–10 |
| `bands.json` | Analyte bands (0.85–1.1 µm fat/protein/moisture … 6–10.5 µm glucose, organic acids …), water in oil, gas bands, lipid/amide bands, S01 Fig. 7 bioprocess map | S02 p.13, 17, 18; S04 p.3; S01 p.17 |
| `sources.json` | Source registry with **evidence scope** (overview, company slides, in-vitro proof of concept, lab demonstration, business) | all |
| `glossary.yaml` | 65 domain terms with ~300 aliases (English and German) and 9 vague words; each term has a plain-language definition and its source page (general terms are marked as such) | S01–S04 |
| `s02_notes.md` | Transcription of all 20 S02 slides (S02 is image-only, so PDF text extraction returns almost nothing). Marked as "transcribed" wherever it is shown. | S02, read visually |

**Rules also carry AFS pathway hints** (`paths:` effect supports / premature / conflicts for Path A, B or C),
e.g. many low-cost measuring points → supports C (S02 p.18); research lab → supports B (S02 p.20); several
variables in one stream → C conflicts (S02 p.18); undefined target → A and C premature.

**Integrity guarantee:** `python -m backend.app.kb.ingest` refuses to build the index if any card's quote
is not found on its cited page (after normalising ligatures, quotes and line-break hyphens).

**Citation format:** `S01 p.10` = 1-based PDF page (title page counts); `S02 p.13` = slide 13;
`S01 Table 1 (p.6)` for the table. This follows the organisers' reference document.

**Evidence scope matters.** S03 (two LED prototypes, 14 in-vitro samples from 7 patients) and S04
(model chicken tissue) are proof-of-concept / lab work. The verifier flags any attempt to use them for a
readiness claim, and the clinical-scope rule turns such requests into `outside_supported_scope`.

## 6. Retrieval: BM25 + dense, RRF, MMR

1. **Indexing** (`kb/ingest.py`): every source page is cut into overlapping windows (~180 words, 60-word
   overlap); the 95 evidence cards are indexed too. Text goes into SQLite FTS5 (BM25, Porter stemming);
   embeddings (bge-small-en-v1.5 via fastembed; a hashing embedder as offline fallback) go in as blobs.
2. **Queries** (`engine/context.py`): 4–6 queries are built from the extracted requirements (targets +
   matrix, optics + candidate methods, fired rule titles, the enquiry itself, client assets, requested methods).
3. **Two rankers per query:** BM25 and dense cosine similarity.
4. **Reciprocal Rank Fusion** (k = 60) merges all rankings: `score(d) = Σ 1 / (60 + rank)`.
5. **Maximal Marginal Relevance** (λ = 0.7) picks relevant but non-redundant passages.
6. **Pinned evidence:** cards on pages cited by blocking or warning rules are always included.
7. **Token budget** (`MAX_EVIDENCE_TOKENS`, default 1800–2500) keeps prompts within the free tier.

The Process tab shows the queries and the budget used for each run.

## 7. Grounding: verifier, quality gate, confidence

### Typed statements
Every sentence in the recommendation, concept, spectral range and risks is one of:
`client_fact` (said in the enquiry), `sourced` (with `{source, page, quote}`), `assumption`, `proposal`.

### Verifier (`engine/verify.py`, no LLM)
- **Quote alignment:** models often paraphrase a quote slightly. If a sentence on the cited page clearly
  matches (or, with a stricter threshold, a sentence on another page of the same source), the quote is
  replaced by the page's exact wording and marked "aligned". Weak matches are left unverified.
- **Quote on page:** normalised exact match → `verified`; ≥ 90 fuzzy → `fuzzy` (flagged); else `unverified`.
- **Scope:** in-vitro / lab / business sources used for readiness words (ready, proven, validated,
  clinical, surgery, approved …) without negation → `scope_warning`.
- **Numbers:** every number with a unit (%, nm, µm, cm-1, mm, °C, ppm …) must appear in the enquiry, the
  evidence, the cited pages or the knowledge base tables; otherwise `unsupported`.
- **Client facts:** every `client_fact` must be traceable to the enquiry or the answers.

### Quality gate (`engine/quality.py`): 16 checks

| Category | Checks |
|---|---|
| Structure | S1 sections present · S2 3–6 questions, highest impact first · S3 plan has samples, reference, comparison, decision basis · S4 decision status consistent with rule findings |
| Grounding | G1 sourced claims verified · G2 no unsupported numbers · G3 no invented client facts · G4 evidence within scope · G5 each recommendation has a sourced reason |
| Honesty | H1 no guarantee / readiness wording · H2 Raman shift in cm-1, excitation in nm · H3 fiber choice consistent with coverage · H4 contradicted premises stated in the headline |
| Usefulness | U1 client-requested weak methods addressed · U2 concrete plan · U3 questions cover high-impact unknowns |

On any **fail**, the report goes back to the model **once** with the exact problems and only the evidence
it cites. The repaired version is kept only if it scores at least as well. Remaining issues are shown in
the UI, never hidden.

### Confidence (`engine/confidence.py`)
Levels: **high / medium / low / insufficient**. Computed as the minimum of:
- **Information**: coach completeness (stated = 1, inferred = 0.5 of 10 decision facts); target undefined → insufficient;
- **Evidence**: a direct application example in the sources (dairy, pharma blend, water in petroleum …) vs only general method knowledge;
- **Scope fit**: requested use vs evidence scope (clinical → insufficient);

then **capped** by rules (e.g. silica link for MIR → low; undefined target → insufficient), and lowered one
level for weak verification or council disagreement. Also shown: client-premise and model-agreement signals,
per-method confidence and the questions that would raise it.

## 8. Council mode (multi-model)

1. Each model in `COUNCIL_MODELS` (default `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`)
   writes a full draft from the same inputs.
2. **Hard gates first:** the deterministic verifier and quality checks run on every draft; grounding or
   honesty failures count against a draft regardless of how good it sounds.
3. **Blind cross-judging:** each model judges only the *other* drafts, anonymised as letters in shuffled
   order, against a rubric copied from the jury criteria, with the explicit instruction that shorter and
   well-founded beats long and assertive (LLM judges are known to favour length, their own output and
   position).
4. **Winner** = gate-passing draft with the best mean score; its questions and/or plan are replaced by the
   sections the judges voted best (deterministic merge, no extra LLM call). The result is verified again.
5. **Agreement** on lead method and decision status is reported and feeds confidence. With only two model
   families available on this key, the UI states that agreement is weaker evidence than with independent families.

Council mode makes many more calls than Fast mode. On the free tier use it for final outputs, not live demos.

## 9. Enquiry coach and what-if

- **Coach:** ten decision-relevant facts (target, matrix, optics, concentration range, reference method,
  accuracy, process conditions, installation, measuring points, response time) are marked stated /
  inferred / unknown and ranked by impact. It also writes an **improved enquiry template** to send to the
  customer, with `[blanks]` for missing facts. It never fills a blank; a template without blanks is rejected.
- **What-if:** type the customer's answers in Coach and re-run. The answers are
  added as stated facts, the whole pipeline runs again, and a before/after diff shows what changed
  (status, confidence, lead methods, ranking, completeness, AFS path, quality).

## 10. The user interface

Open `http://localhost:8000`.

**Two views** (toggle in the header; the browser remembers the choice). Both keep the same four tabs:
Reading, Result Assessment, Confidence and Verification, and Coach.

- **General (default)**, for internal non-experts such as sales or management: status and confidence in plain
  words, the answer, *problems found in the request* (always shown), what to test first with a one-line plain
  explanation of each method (sources behind "Show sources"), the top three questions, the first experiment,
  and the next step with AFS including path verdicts. Domain terms have tooltips.
- **Expert**: the full workbench described below.

**Before you run it (pre-check)**: while the enquiry is typed, an instant keyword check (no AI) shows recognised
terms (German aliases resolved, e.g. *Feuchte → moisture*, *Glasfaser → silica fiber*), vague words, early
warnings from blocking rules, and missing key facts. It is informational; the questions are asked on the next step.

**"Is this what you mean?" (in Reading, on by default)**: *Check and assess* first reads the enquiry
with the extraction model (the run's own first stage) and shows a card with:
- **We understood**: the structured readings that drive the rules (what to measure, sample form, optics, methods
  asked for, equipment they have, path they ask for, ...). Each has ✓ / ✗; a ✗ resets that reading to *unknown* for
  the run (e.g. "it is **not clear** yet" misread as *optics: clear*), so no rule fires on it. Glossary translations
  (*Restfeuchte → moisture*) and the customer claims that will be tested are listed too.
- **AFS path**: chosen paths and paths found in the enquiry, with full names.
- **Open questions, one list without repeats**: vague words, missing key facts, and the questions of every chosen
  or found path. A path question that covers a missing fact replaces it (Path A "reference values?" replaces the
  general reference question). Answers the text already gives are **pre-filled and tagged "from your text"**.
- **Yes, assess** (with the answers given) · **Skip questions and assess** · **Back**; *Show this step before
  every run* can be unticked (remembered), then *Assess enquiry* runs straight away. Path questions remain
  available in Reading when the confirmation card is disabled.

The customer's text is never rewritten: corrections travel as `rejected` fields, answers as a separate block.
Because path answers and ✗ corrections are kept out of the extraction prompt, confirming **reuses the cached
reading**; only free-text answers to missing facts trigger a fresh extraction (fast model). Eval scripts call the
API directly and never see this step.

**Preferred AFS path (multi-select, shown with full names)**: A *Chemometric model for process automation*,
B *Multi-spectral system for your R&D lab*, C *Low-cost spectral sensor(s)*; none chosen = Auto. Paths the
customer seems to ask for are marked *in the enquiry* by the pre-check. Each path has three one-click questions
(for example *Has a lab trial already shown which wavelengths matter?*), asked on the confirmation card.
**Everything is optional**: unanswered questions are not sent and the run simply proceeds without them. Some
answers carry a sourced effect on that path's verdict (e.g. C + "No" → *premature*, S01 p.9; B + "In production"
→ *conflicts*, S02 p.20); the rest is context for the report. Path answers travel as
`Path X - <question>: <answer>`, are kept after the run, and are kept out of the keyword heuristics and the
extraction prompt so they cannot be misread as other facts. Change paths in Reading and press *Re-run* in Coach
to re-assess. Answers for a removed path are excluded unless the customer asked for that path in the enquiry.

- **Header:** decision status, computed confidence, quality x/16, claims verified, unsupported numbers.
- **Top pipeline navigation:** One gradient line connects four numbered dots: Reading →
  Result Assessment → Confidence and Verification → Coach. Dots stay hollow until their tab's work
  completes, then fill with that
  step's spectrum color. The gradient line stays continuous through the brighter, gradient-backed selected step.
  Submitting an enquiry opens a temporary calculation screen. The gradient line advances as stages finish,
  and navigation stays locked until the complete result arrives. The loading screen then closes and
  Result Assessment opens automatically (Coach after a what-if re-run).
- **Right-side page navigation:** a sticky, color-tinted panel contains each page's title, short explanation,
  runtime, and vertical section links. The current section is accented automatically. Links open collapsed
  sections and preserve `#run=<id>` deep links. On smaller screens, the “On this page” button opens the panel
  from the right; selecting a section closes it. Reading omits scenario, assessment-mode, and model links
  from navigation while keeping those controls in the form.
- **Reading:** a centered customer enquiry form with a larger text field, a scenario loader beneath it,
  optional Path A/B/C selection, the instant pre-check, and the reading confirmation with follow-up questions.
  Fast / Council mode includes an explanation of the selected mode. The LLM model choice is saved in the
  browser; backend routing still uses the server configuration.
- **Saved queries:** a sidebar on Reading lists recent enquiry drafts. Save a query, start a new one, reopen
  a saved query, or remove it. Text and Reading options are saved in this browser; checking or assessing an
  enquiry also saves it. This UI has no user/chat database links. On small screens the list folds away.
- **Account controls:** Log in and Subscribe to Expert are available throughout the app. Their dialogs are
  placeholders; they collect no credentials or payments. Integration points for the separate account/chat
  work are described in [frontend integration](docs/frontend-integration.md).
- **Temporary loading screen:** the current model task, stage completion, an updating model trace,
  council activity, and timings. It appears during calculation only; detailed outputs are kept in the
  completed calculation record.
- **Result Assessment:** a shared outline preview in General and Expert, with contents links for Decision
  Status, Requirements stated, Key unknowns, Clarification questions, Recommendation, Measurement concept,
  Spectral range, Risks and uncertainty, First feasibility experiment, Decision basis, and Sources.
  These are placeholder sections for the next assessment format; current RAG fields are not mapped into them.
  Existing run data is retained, and the complete generated Markdown report (including appendices A–M)
  remains available to download. Frontend slots are described in [frontend integration](docs/frontend-integration.md).
- **Confidence and Verification:** computed confidence, citation checks, number and client-fact checks,
  and the quality gate. The complete calculation record, model trace, and council results are available
  in a collapsed details section.
- **Coach:** follow-up questions, improved enquiry template, and what-if re-runs with before/after changes.
  Completed runs can be reopened with `#run=<id>`.
- **Source drawer:** click any citation chip. Shows the source's scope, the quote, whether it was found
  verbatim, the page text with the passage marked, and the original PDF page with the passage highlighted.

## 11. Installation

**Python 3.12** is required in practice. (On Python 3.14, PyMuPDF failed to load its DLL on Windows and
the embedding runtime may not install.)

### Windows (PowerShell)
```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python --version                           # must print 3.12.x
pip install -r requirements.txt
```
If PyMuPDF reports `DLL load failed`, install the Microsoft Visual C++ Redistributable (x64):
`winget install Microsoft.VCRedist.2015+.x64` or https://aka.ms/vs/17/release/vc_redist.x64.exe, then reopen PowerShell.

### macOS / Linux
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration and data
```bash
cp .env.example .env          # Windows: copy .env.example .env   -> then add GROQ_API_KEY
```
Copy the challenge materials into `data/raw/` with exactly these names:

```
S01_Multispectral_Laboratory.pdf        S02_AFS_Process_Control_Slides.pdf
S03_LED_Kidney_Study_2017.pdf           S04_Combi_MIR_Fluorescence_2021.pdf
S05_AFS_Flyer.pdf                       S06_Laboratory_Link.txt
AFS_method_comparison_table.xlsx        AFS_Examples_and_Reference.docx
customer_scenarios_for_final_evaluation.txt
```

### Build the knowledge index
```bash
python -m backend.app.kb.ingest
```
Expected: `"pages": 65, "records": 275, "claims": 95, "embed_backend": "fastembed:BAAI/bge-small-en-v1.5"`.
The first run downloads the embedding model (~67 MB). Symlink warnings on Windows are harmless
(silence them with `HF_HUB_DISABLE_SYMLINKS_WARNING=1` in `.env`).

### Check the Groq key
```bash
python scripts/check_groq.py
```
Lists the models your key can use; the model names in `.env` must be among them.

## 12. Running the app

```bash
python -m uvicorn backend.app.main:app --port 8000
```
Open http://localhost:8000. On first start with an empty index the server runs ingest itself.

**No key, or Groq down?** Set `LLM_MOCK=1`. Every stage uses its rule-based fallback; reports are still
complete, cited and verified, and say they are rule-based.

## 13. Evaluation and reproducing the outputs

| Command | What it does |
|---|---|
| `python -m pytest -q` | 12 deterministic tests: RRF/MMR, every evidence quote on its page, wrong-page and scope detection, fiber/fluorescence/clinical/undefined-target rules |
| `python -m eval.run_cases --set final` | H01–H06 in Fast mode → `outputs/H0x.md` + `.json` |
| `python -m eval.run_cases --set final --mode council --pause 20` | H01–H06 in Council mode (submission quality; slow on the free tier) |
| `python -m eval.run_cases --set dev` | D01–D08 → `outputs/dev/` |
| `python -m eval.run_cases --set adversarial` | Development only (hidden in the UI unless `SHOW_DEV_CASES=1`). A01–A07 (our own trap cases: wrong fiber, non-fluorescent target, model-tissue paper as proof, vague request, many cheap points, demand for a detection limit, prompt injection) with automatic expectation checks |
| `python -m eval.run_cases --set dev --ids D04 D06` | Selected cases only |
| `python -m eval.summary` | Regression table across all runs |
| `python -m eval.judge --dir outputs/dev` | LLM scoring against the six jury criteria (D01/D02 also compared with the organisers' worked answers). Development aid only. |

The run table columns: decision status, confidence, quality x/16, verified claims, unsupported numbers,
lead methods, LLM calls, **fallbacks** (stages where the model failed and the rule version was used),
seconds, expectation check.

**Rules followed for H01–H06:** the outputs are generated by the assistant and committed unedited; no
rule, prompt, card or code path refers to an evaluation scenario.

## 14. Configuration

All settings are read from `.env` (`backend/app/config.py`).

| Variable | Default | Meaning |
|---|---|---|
| `GROQ_API_KEY` | – | Groq key |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | OpenAI-compatible endpoint |
| `MODEL_FAST` | `openai/gpt-oss-20b` | extraction, premise check, repair, coach, judging |
| `MODEL_MAIN` | `openai/gpt-oss-120b` | report (Fast mode) |
| `COUNCIL_MODELS` | `openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b` | council drafts and judges |
| `LLM_MOCK` | `0` | `1` = no API calls, rule-based fallbacks |
| `LLM_CACHE` | `1` | cache validated replies in SQLite by prompt hash (identical re-runs are free) |
| `LLM_MAX_RETRIES` | `4` | retries on 429 / server errors before a stage falls back |
| `LLM_TIMEOUT_S` | `90` | per-request timeout |
| `MAX_EVIDENCE_TOKENS` | `2500` | evidence budget per prompt; 1800 recommended on the free tier |
| `EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | fastembed model |
| `EMBED_BACKEND` | empty | `hashing` = skip the model download, use the offline embedder |
| `SHOW_DEV_CASES` | `0` | `1` = show our own adversarial cases A01–A07 in the UI scenario loader |
| `DB_PATH`, `RAW_DIR`, `KB_DIR` | `data/cache/afs.db`, `data/raw`, `data/kb` | paths |

## 15. Groq free tier: what to expect

The free tier limits each model separately, per minute **and per day**:

- **Tokens per minute (TPM)**, about 8,000 for `gpt-oss-120b`. Groq counts the prompt **plus the
  requested maximum output** against it. A report request is ~5–7k, so the next big request usually has to
  wait for the next minute. You see this as `429 … waiting Ns` lines: normal, the client waits and retries.
- **Request too large (413):** a single request bigger than the whole per-minute limit can never succeed;
  the client retries once with a smaller output budget.
- **Daily limits (tokens or requests per day):** after many runs in one day a model can be exhausted until
  the daily window resets. The symptom is a long series of `429 … waiting 30.0s` lines on one model with no
  progress; after the retries the stage falls back to its rule-based version.
- **Speed:** a Fast-mode case takes roughly 1–3 minutes on the free tier, mostly waiting; Council mode much
  longer. Cached prompts cost nothing, but any change to prompts, code or knowledge creates new prompts.

Spreading stages across models (only the report on `120b`) uses the separate per-model budgets in parallel.

## 16. API reference

| Method & path | Purpose |
|---|---|
| `POST /api/understand` | Reading confirmation: structured readings, glossary translations, paths, warnings, and one list of questions with pre-fills. Body: `{enquiry, answers?, preferred_paths?}` |
| `POST /api/assess` | Run the pipeline; SSE stream (`stage`, `stage_result`, `detail`, `error`, `result`). Each `stage_result` contains that stage's fields and the current trace; `result` contains the complete saved run. Body: `{enquiry, answers?, mode: fast|council, preferred_paths?: ["A","B","C"], rejected?: ["optical_behavior", ...]}` |
| `POST /api/assess/sync` | Same, returns the run JSON (scripts, curl) |
| `POST /api/whatif` | Re-run a saved run with answers; same SSE events. Body: `{run_id, answers, mode?, preferred_paths?}` |
| `GET /api/coach/{run_id}` | Coach result of a run |
| `POST /api/precheck` | Instant keyword pre-check (no LLM). Body: `{enquiry, answers?}` |
| `GET /api/glossary` | Glossary entries for tooltips |
| `GET /api/paths` | Full AFS path names and the optional questions per path |
| `GET /api/runs` · `GET /api/runs/{id}` | Saved runs |
| `GET /api/runs/{id}/export.md` | Full Markdown export (assessment + appendices A–M) |
| `GET /api/runs/{id}/trace` | LLM calls, timings, retrieval details |
| `GET /api/source` | Source registry with pages loaded |
| `GET /api/source/{doc}/{page}?q=` | Page text, metadata, whether `q` is on the page |
| `GET /api/source/{doc}/{page}/image?q=` | PNG of the PDF page with `q` highlighted |
| `GET /api/health` | Index size, embedding backend, mock flag, key present, models |
| `GET /api/kb/summary` | Claim and rule counts, rule list with sources |
| `GET /api/examples` | H, D and adversarial scenarios for the UI loader |
| `POST /api/feedback` · `GET /api/feedback` | Expert feedback on a run (stored in SQLite) |

## 17. Repository layout

```
afs-assistant/
├─ README.md                    this file
├─ requirements.txt · .env.example · .gitignore
├─ docs/architecture.md         architecture and use of AFS materials (short version)
├─ data/
│  ├─ raw/                      AFS challenge materials (not committed)
│  ├─ kb/                       curated knowledge base (see section 5)
│  └─ cache/                    afs.db, embedding model, page images (generated)
├─ backend/app/
│  ├─ main.py                   FastAPI app, static frontend, startup ingest and model check
│  ├─ config.py                 settings from .env, source file names
│  ├─ schemas.py                all Pydantic models (LLM contracts and run objects)
│  ├─ api/                      assess.py (SSE, what-if) · sources.py (page text/images) · runs.py (runs, export, health, examples, feedback)
│  ├─ llm/
│  │  ├─ client.py              Groq client: JSON schema, validation, 429/413, cache, fallback, trace
│  │  ├─ models.py              model roles, council list, availability check
│  │  └─ prompts/               extract · premise · report · repair · judge · coach (.md)
│  ├─ kb/                       pages.py (page text, normaliser) · store.py (SQLite) · embed.py · ingest.py · retrieve.py
│  ├─ engine/                   extract · understand · paths · glossary · precheck · rules · coverage · screen ·
│  │                            context · premise · report · council ·
│  │                            verify · quality · confidence · coach · whatif · pipeline (stage_result SSE)
│  └─ render/markdown.py        run → Markdown
├─ frontend/
│  ├─ index.html · css/styles.css
│  └─ js/                       api.js · state.js · app.js · glossary.js · pipeline-steps.js (shared step model)
│      └─ components/           pipeline.js (tab views and temporary loading screen) · page-navigation · header · enquiry · confirm ·
│                               pathq · precheck · coach · summary · report · matrix · spectral-map ·
│                               evidence · quality · council · whatif · trace
├─ eval/
│  ├─ cases/                    final_cases.yaml (H01–H06 verbatim) · dev_cases.yaml (D01–D08 + worked answers) · adversarial_cases.yaml
│  ├─ run_cases.py · summary.py · judge.py
├─ outputs/                     generated assessments (H01–H06 at the top level)
├─ scripts/check_groq.py
└─ tests/                       test_retrieve.py · test_verify.py · test_rules.py
```

## 18. Troubleshooting

| Symptom | Cause and remedy |
|---|---|
| `ImportError: DLL load failed while importing _extra` (PyMuPDF) | Python 3.14 and/or missing Visual C++ runtime. Use Python 3.12 (section 11) and install the VC++ Redistributable x64. Check `python -c "import sys; print(sys.version, sys.executable)"`. |
| Traceback path shows `...\Python314\...` | The venv is not active, or was created with 3.14. Activate `.venv312` before running. |
| `uvicorn` is not recognised | Use `python -m uvicorn backend.app.main:app --port 8000`. |
| Server stops at startup | Startup runs ingest when the index is empty; fix the ingest error first. |
| Ingest: "Claim quotes not found on their pages" | A source file is missing, renamed or a different version. Check the names in `data/raw/`. |
| Embedding download fails | Set `EMBED_BACKEND=hashing` (offline embedder), re-run ingest. |
| Many `429 … waiting` lines | Free-tier per-minute limit; normal (section 15). Endless 30 s waits on one model usually mean its daily limit is used up. |
| `413 Request too large` | One request exceeds the per-minute limit; lower `MAX_EVIDENCE_TOKENS`. |
| Process shows "fallback" | That stage's LLM call failed; the rule-based version was used. The error text is in Process and in `outputs/*.json` (`trace`). |
| UI shows "Rule-only mode" | `LLM_MOCK=1` or no `GROQ_API_KEY` in `.env`. |
| Citation drawer: "quote NOT found" | The model cited a passage that is not on that page; the claim is treated as unsupported and flagged by the quality gate. |

## 19. Limitations and honest caveats

- **No spectra were supplied**, so the assistant cannot predict accuracy or detection limits and is
  designed not to state any. Every performance target is "client-agreed".
- **The knowledge base is the supplied material.** New documents are not picked up automatically: they
  must be registered in `config.py` and `sources.json` and re-ingested; curated cards and rules are
  written by hand.
- **S02 is image-based.** Its text comes from our transcription (`s02_notes.md`); figure values are
  approximate readings of the slides and labelled as such.
- **Quote alignment** replaces a slightly paraphrased quote with the page's exact sentence; it can only
  fix wording, not make an unsupported claim supported. Low-similarity quotes stay unverified.
- **Council agreement** uses two model families (gpt-oss and qwen) on this key, so it is weaker evidence
  than fully independent models; the UI says so.
- **Rules are deliberately conservative** and keyword-assisted; an expert should review the fired rules
  (Process tab) for each case.
- **Free-tier latency** makes Council mode slow; Fast mode is the live-demo mode.

## 20. Future work

- **Spectral-data module:** when AFS lab-trial spectra exist, run preprocessing (SNV/MSC) and PLS, show
  the informative wavelength regions, and test whether a few-band LED / filter sensor (Path C) could reach
  the client's target, mirroring the AFS FlexiSens and LED-sensor workflow (S02 p.12, S01 p.9, S03).
- **Expert feedback loop:** turn stored expert corrections into reviewed new rules and evidence cards.
- **Automatic source onboarding** with an "unreviewed" evidence scope until an expert approves the cards.
- **Vision-assisted reading** of figures for new slide decks.

## 21. How the numbers work, and how the knowledge base grows

Every number on screen except the premise verdicts and the council judge scores is computed by
deterministic code. The thresholds below are **design choices, visible and tunable** in the named files;
they were checked against expected outcomes (dev and adversarial cases), not fitted to expert-labelled data.

### Header

| Shown | Computed in | Rule |
|---|---|---|
| **Decision status** | report model, constrained | "Target not defined" forces *insufficient information*; "clinical / in-vivo use" forces *outside supported scope*. Quality check S4 fails if the report disagrees, or says *outside scope* without such a rule (one repair round). Rule-only mode takes the status straight from these rules. |
| **Confidence** | `engine/confidence.py` | See below. |
| **Quality x/16** | `engine/quality.py` | Number of the 16 checks (section 7) that **pass**. S2, H2, H4, U1, U2, U3 (and G1 at 70–90 %) can only *warn*; only *fails* trigger the repair round. |
| **Claims verified x/y** | `engine/verify.py` | *y* = statements of kind `sourced` in recommendations, measurement concept, spectral range and risks (headline, questions, plan and premise check are not counted). *x* = those whose quote is on the cited page after alignment: exact normalised match = verified, ≥ 90 fuzzy = fuzzy (counted, flagged). Readiness wording citing S03/S04/S05/S06 = scope warning (not counted). |
| **Unsupported numbers** | `engine/verify.py` | Numbers with a unit (%, nm, µm, cm-1, mm, °C, ppm, mM …) anywhere in the report that do not appear in the enquiry, the answers, the evidence, the cited pages or the knowledge-base tables (2400 nm ↔ 2.4 µm accepted). |

### Confidence, step by step

| Signal | Computation | Level |
|---|---|---|
| Information | coach completeness = (stated + 0.5 × inferred) / 10 | ≥ 0.6 high · ≥ 0.35 medium · ≥ 0.15 low · else insufficient; target undefined → insufficient |
| Evidence | an *application rule* fired (dairy, pharma blend, water in petroleum, hot-melt API, moisture, bioprocess, heterogeneous tissue, glucose) and a lead method exists | high; lead only → medium; candidates only → low; none → insufficient |
| Scope fit | clinical-scope rule fired / production context | insufficient / medium / else high |
| Client premises (shown) | any contradicted / any unverifiable | low / medium / high |
| Verification (adjusts) | verified ÷ sourced | ≥ 0.9 high · ≥ 0.7 medium · else low |
| Model agreement (council, adjusts) | see council | ≥ 0.99 high · ≥ 0.6 medium · else low |

1. Overall = **minimum of Information, Evidence and Scope fit**.
2. **Rule caps**: silica link for MIR → low; fluorescence without target → low; demand for an exact answer → low; target undefined → insufficient; clinical use → insufficient.
3. **Minus one level** if Verification is low, and again if Model agreement is low.
4. Status *insufficient information* or *outside supported scope* → confidence insufficient.

Client premises are shown but do not lower the level: a wrong customer premise is a finding, not
uncertainty in the answer. Per method: lead = overall, candidate = one level lower, weak / not supported =
insufficient. "What would raise confidence" = the top three unknown, high-impact coach questions.

### Other numbers

| Shown | Rule |
|---|---|
| Method screening score | Sum of rule contributions (e.g. +2 "Powders favour NIR" [S01 p.6]). ≤ −2 not supported; top score ≥ 2 lead; ≥ 1 candidate; else weak. |
| Coach x/10 | Ten fixed facts (target, matrix, optics, concentration range, reference, accuracy, conditions, installation, measuring points, response time): stated 1, inferred 0.5, rounded. |
| Premise verdicts | LLM (fast model); fallback: premise type + fired rule → *contradicted* (blocking rule) or *unverifiable* (warning rule). |
| RRF score (evidence list) | Σ 1 / (60 + rank) over all BM25 and dense rankings. |
| Council judge score | Mean of six 1–5 rubric scores, averaged over the judges; no self-judging. |
| Council winner | Drafts without grounding / honesty gate failures first, then highest judge score. |
| Council agreement | Lower of: share of drafts with the most common lead method(s), share with the most common status. |
| Suggested path | The path with the most *supports* hints from fired rules, if no rule hints against it; a tie or a status rule (insufficient information / outside scope) → *undecided*. It overrides the model's guess so the pathway stays traceable. |
| Requested path verdict | premature > conflicts > fits > open (no rule decides it; the lab trial does), with the rule's reason and sources. Premature or conflicting paths get a sourced "If you proceed anyway" plan. |
| Spectral map | Nominal method ranges (`methods.json`), fiber ranges (S02 p.6). Overlap full / partial / none. Client silica link flagged when the assets mention silica and the method starts above 2.4 µm. |

### Where the data lives

One SQLite file, `data/cache/afs.db` (path from `DB_PATH`), not committed to git:
`chunks` + `chunks_fts` (275 searchable records, BM25), `vectors` (embeddings), `meta` (ingest stats),
`runs` (every assessment as JSON), `llm_cache` (validated Groq replies by prompt hash), `feedback`.
Re-running ingest rebuilds only the first three; deleting the file loses saved runs and the cache.
The embedding model is cached in `data/cache/models/`.

### How the knowledge base was built

AI-assisted curation from the supplied material only, with every quote machine-verified; intended for
review by an AFS expert.

1. Every source read: S01 page by page (text extraction); **S02 rendered slide by slide and read visually**
   because it is image-only, transcribed into `s02_notes.md`; key pages of S03 and S04; S05/S06 tagged as
   business context.
2. `methods.json`: the 19 rows of the xlsx converted by script, plus method profiles with source pages;
   `fibers.json` and `bands.json` from the S02 figures, S04 and S01 Fig. 7.
3. 95 evidence cards (`claims.jsonl`): claim, source, page, **verbatim quote**, scope tag.
4. Every quote checked against its page by code; ingest and a test refuse to run if one fails.
5. 35 general rules (`rules.yaml`) with conditions, effects and sources; none refers to a scenario.
6. Ingest: 65 pages → ~180-word overlapping windows + 95 cards = 275 records → FTS5 + embeddings.

### How it grows

| Layer | Process |
|---|---|
| **Searchable text** (automatic once registered) | Add the file to `SOURCE_FILES` (`config.py`) and to `sources.json` with an evidence scope, re-run ingest. Its pages become retrievable and citable; the verifier checks quotes from them like any other. Planned: auto-discovery of new PDFs with scope "unreviewed", which can never raise confidence. |
| **Curated cards and rules** (human-approved by design) | The model proposes candidate cards from a new document; only cards whose quote passes the on-page check are kept; an AFS expert approves them into `claims.jsonl`. Rules are written or approved by experts; expert feedback is already stored per run (`/api/feedback`) as input for new rules. |
| **Regression after every change** | `pytest` (every quote on its page, every rule sourced) and `python -m eval.run_cases --set dev` / `--set adversarial` (expectation column must read OK). The knowledge base is versioned in git. |

---

*Sources used throughout: S01 Multispectral Laboratory (art photonics / MIR Photonics), S02 AFS Process
Control slides, S03 LED kidney study (Sensors 2017), S04 combined MIR-fluorescence probe (Anal. Chem.
2021), S05 AFS flyer, S06 laboratory link, and the AFS method comparison table. All are © their respective
owners and are not redistributed in this repository.*
