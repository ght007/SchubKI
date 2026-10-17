# Architecture and use of AFS materials

## Design principle

The language model writes and explains; it does not decide alone. Everything an expert
needs to trust (which methods are physically possible, which premises the sources contradict,
which claims are really on the cited page, how confident the result is) is computed by
deterministic code from the supplied AFS materials. The model's text is then checked against
those materials before it is shown.

```
 enquiry ──► 1 Extract ─────────► Requirements: stated / inferred / unknown / client premises      (LLM, keyword fallback)
             2 Rules + coverage ─► 35 sourced rules, fiber↔band↔method overlap, method matrix     (deterministic)
             3 Retrieve ─────────► BM25 + dense → RRF → MMR, pinned claims, token budget          (deterministic)
             4 Premise check ────► supported / partly / contradicted / unverifiable + citations   (LLM, rule fallback)
             5 Report ───────────► Fast: one model · Council: drafts → gates → blind judges       (LLM, rule-only fallback)
             6 Verify ───────────► quote on page? numbers supported? client facts real? scope?    (deterministic)
             7 Quality gate ─────► 16 checks, one auto-repair round                                 (deterministic + LLM repair)
             8 Coach + confidence► completeness, ranked unknowns, template; computed confidence    (deterministic + LLM template)
```

## Knowledge base (data/kb)

| File | Built from | Used for |
|---|---|---|
| `claims.jsonl` | 95 evidence cards hand-curated from S01-S05; each has claim, source, page, **verbatim quote**, evidence scope | Retrieval, citations, rule fallbacks. Ingest refuses to run if any quote is not on its page. |
| `rules.yaml` | 30 general rules, each with source pages | Premise flags, method scores, questions, confidence caps, status hints |
| `methods.json` | `AFS_method_comparison_table.xlsx` (S01 Table 1, p.6) + method profiles from S01 p.5-18 | Matrix, nominal ranges, compatible fibers |
| `fibers.json` | S02 p.6-10 | Spectral coverage, silica/IR fiber checks |
| `bands.json` | S02 p.18, p.13, p.17; S04 p.3; S01 Fig. 7 (p.17) | Analyte bands on the spectral map |
| `sources.json` | All sources | Evidence scope (overview / company slides / in-vitro proof of concept / lab demo / business) |
| `s02_notes.md` | Visual reading of all 20 S02 slides | S02 is image-only; this transcription is its searchable, quotable text (marked as transcribed in the UI) |

No rule or claim is written for a specific scenario. H01-H06 were never used to tune anything.

## Retrieval

Every source page is split into overlapping windows (~180 words) and indexed together with the
evidence cards in one SQLite file: FTS5 for BM25, float32 embeddings (fastembed, bge-small-en-v1.5;
a hashing embedder is the offline fallback) for dense search. Four to six queries are built from the
extracted requirements; each is ranked by both rankers, all rankings are fused with Reciprocal Rank
Fusion (k = 60), and Maximal Marginal Relevance (λ = 0.7) picks diverse passages inside a token budget
(Groq free tier). Claims on pages cited by blocking or warning rules are always included.

Why SQLite and not a vector database: ~275 records. Brute-force cosine takes microseconds, and the
whole system runs from one file with one command.

## Grounding and verification

The report schema forces every statement to declare its kind: `client_fact`, `sourced`, `assumption`
or `proposal`. Sourced statements carry `{source, page, quote}`. The verifier then checks, without an LLM:

- the cited page exists and the quote is on it (normalised exact match; ≥90 fuzzy = flagged);
- in-vitro, lab-demo or business sources are not used for readiness claims (scope warning);
- every number with a unit appears in the enquiry, the evidence or the cited pages;
- every "client fact" is traceable to the enquiry text.

The quality gate (16 checks: structure, grounding, honesty, usefulness) sends failures back to the
model once with the exact problems. Remaining issues are shown, never hidden.

## Confidence

Confidence is the minimum of observable signals (information completeness, direct application evidence,
scope fit), capped by rules (e.g. undefined target → insufficient, clinical use → insufficient) and lowered
by weak verification or council disagreement. The model never rates itself.

## Council (multi-model)

Each configured model (gpt-oss-120b, qwen3.8-27b, gpt-oss-20b) writes a draft from the same inputs.
Deterministic gates run first; then every model judges the other drafts blind, anonymised and shuffled,
on a rubric copied from the jury criteria with an explicit "shorter and well-founded beats long". The best
gate-passing draft wins; its questions and plan may be replaced by the best-voted sections. Agreement on
the lead method and status is reported as a confidence signal. With two model families available, the UI
says that agreement is weaker evidence than with independent families.

## Robustness

Every LLM stage has a deterministic fallback, so the app never fails during a demo: with no key or a
Groq outage it produces a complete, cited, rule-only assessment and says so. LLM replies are validated
with Pydantic (one repair round), cached by prompt hash, and 429 responses wait for Groq's retry-after.

## Mapping to the AFS pathway

Each report ends with the AFS pathway (S02 p.20): the next step is normally a multi-method lab trial, and
the likely Path A (chemometric model), B (customised multi-spectral system) or C (spectral IoT sensor) is
named only when the facts allow it.