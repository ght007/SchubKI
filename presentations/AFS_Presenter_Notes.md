# AFS Assessment Assistant — Presenter Notes

Main presentation: slides 1–10, planned 4 minutes 50 seconds including a 60-second demo. Slides 11–14 are appendices.

## Slide 1

PRESENTATION TIMING: 15 seconds

SPEAKER NOTES
Introduce the project as an assistant for an AFS expert’s first customer discussion. Name the five contributors; do not imply individual roles that have not been supplied. The assistant supports technical screening and experiment design, rather than replacing expert judgment.

SOURCES AND EVIDENCE
User-provided contributor names; README introduction; challenge brief p.1. The organiser is SchubKI; no separate formal team name was supplied.

## Slide 2

PRESENTATION TIMING: 20 seconds

SPEAKER NOTES
Start with the challenge’s industrial customer: the desired process variable is known, but the measurement concept is not. Explain the three outputs: clarify, propose, and design a useful first test. The displayed customer sentence is an illustrative condensation of the challenge, not a logged customer quote.

SOURCES AND EVIDENCE
Challenge brief pp.1–2: six requested outputs and minimal requirements. README §§1–2.

## Slide 3

PRESENTATION TIMING: 35 seconds

SPEAKER NOTES
Walk through the fixed stages without reading every box. The pipeline deliberately does not depend on an agent choosing whether to verify. Explain that Council is optional: multiple models draft and cross-judge, but deterministic gates still run. Supabase is the main database only when configured; SQLite is local storage and offline fallback. Source files and a built index remain prerequisites for a functional run.

SOURCES AND EVIDENCE
README §§3–8 and 21. docs/frontend-integration.md: processing, data retention, accounts. Current engine and database implementation. Older architecture.md describes a SQLite-only baseline; this slide reflects the newer conditional Supabase implementation.

## Slide 4

PRESENTATION TIMING: 25 seconds

SPEAKER NOTES
Use the three counts as implementation counts, not performance claims. The repository contains 95 evidence cards and 35 rules; the quality gate defines 16 checks. Explain the hierarchy of evidence scopes. The S02 slide deck is image-based and has a curated transcription. Raw source documents must be available for ingestion and quote verification.

SOURCES AND EVIDENCE
Counts checked directly in current claims.jsonl and rules.yaml. README §§5–7, 21; quality.py. Source descriptions cross-checked against the supplied original presentation, pp.3–4. Original S01–S05 PDFs are not present in this cloud checkout, so source quotations were not independently reverified for this slide.

## Slide 5

PRESENTATION TIMING: 65 seconds, including a 60-second live demo

SPEAKER NOTES
Live demo script (Fast mode): 0–10s enter or load H04; 10–25s show the reading dialog, the silica/MIR warning, and one follow-up question; 25–45s select Yes, assess and open the resulting recommendation; 45–60s click a citation, inspect verification and show the feasibility plan. Close/Escape returns to editing; there is no skip button. If remote model latency prevents a five-minute presentation, open the stored run and clearly identify it as a replay. Expert view adds Process Information and Coach; General has three tabs. The screenshot is a current-frontend replay using rule-based reading and the archived H04 result, not evidence of a fresh model run or of currently configured external services.

SOURCES AND EVIDENCE
docs/frontend-integration.md and current frontend code, feature_dialog @18e4f84. UI screenshots captured from real frontend code with fixture API responses; result data taken from outputs/H04.json.

## Slide 6

PRESENTATION TIMING: 30 seconds

SPEAKER NOTES
Read the concept, then the refusal: the customer’s existing asset does not match the requested spectral region, and critical installation data is missing. This is a recommendation to investigate, not approval of an engineered system. The reference to silica and MIR is drawn from the curated AFS evidence; do not present the old model report as fully verified. Its verification defects are intentionally shown on slide 8.

SOURCES AND EVIDENCE
H04 exact scenario in eval/cases/final_cases.yaml. Stored outputs/H04.json, report headline and feasibility plan. S02 pp.6/9 fiber references and p.13 water-in-petroleum reference as represented in repository evidence cards; original S02 PDF was not available for a fresh page check.

## Slide 7

PRESENTATION TIMING: 30 seconds

SPEAKER NOTES
Show that the output is an experiment plan rather than a product catalog answer. Use representative samples, independent references, same-sample comparisons and success criteria agreed with the customer. The H04 archive specifically proposes water-spiked petroleum, Karl Fischer references and increasing link length. The AFS pathways are options after evidence from the lab trial; this slide does not claim that all three are already suitable for H04.

SOURCES AND EVIDENCE
Stored H04 report feasibility_plan and pathway. README §§5, 7, 21; S02 p.20 path descriptions in curated materials. Challenge brief requires a simple practical feasibility-study plan. No sample counts, detection limits or accuracy targets have been invented.

## Slide 8

PRESENTATION TIMING: 30 seconds

SPEAKER NOTES
Make the limitations visible rather than overstating performance. The archive has an H01 run with 10/10 sourced statements counted verified and an H04 run with 2/7; both score 14/16 on the quality gate. H04 includes a nonexistent S12 citation and one unsupported number. The overall confidence is insufficient. These are stored runs dated 17 October 2026, not results of a new evaluation. The app metric counts verified/fuzzy statements. A citation check is not an expert validation of the scientific claim. Do not repeat the old deck’s claims that 60 tests passed or all 21 cases passed; those claims were not established by the available artifacts.

SOURCES AND EVIDENCE
Exact metrics and flag read from outputs/H01.json and outputs/H04.json. README §§7,21 explains metric definitions. Supplied old presentation p.7 provides context, but the archive values are the primary evidence.

## Slide 9

PRESENTATION TIMING: 25 seconds

SPEAKER NOTES
Name the scientific and system boundaries in plain language. No laboratory spectra were supplied, so there is no defensible predictive accuracy claim. More documents do not automatically mean approved rules; experts curate them. LLM citations can still fail and runtime quotas affect latency. Near-term work is to use measured spectra and expert feedback, not to claim production or clinical readiness from a prototype.

SOURCES AND EVIDENCE
README §§19–21. Original presentation p.8. Current knowledge-base editor supports registered readable documents with validation/versioning; it does not remove the need for expert review.

## Slide 10

PRESENTATION TIMING: 15 seconds

SPEAKER NOTES
Thank the jury and credit every contributor exactly as supplied: Eisa Atif, Marie Habermann, Atfan Deshmukh, Akshdeep Singh, and Naumanurrahman Shaikmujeeburrahman. Do not assign roles or hierarchy. End the main presentation here. Slides 11–14 are backup slides and submission handoff material; they are not part of the five-minute talk.

SOURCES AND EVIDENCE
User-provided contributor names. Main-slide timings total 290 seconds, including the demo.

## Slide 11

PRESENTATION TIMING: Backup slide; omit from the timed talk

SPEAKER NOTES
Use this only for questions about alignment to the challenge. This is an evidence mapping, not a scoring result. It covers all six criteria, summing to 100%. The presentation and demo are planned to fit in the five-minute requirement.

SOURCES AND EVIDENCE
Official challenge brief p.2: criterion weights 30/20/15/15/10/10. Submission form pp.3–4 requires architecture, examples, feasibility plans, limitations and a prototype demonstration.

## Slide 12

PRESENTATION TIMING: Backup slide; omit from the timed talk

SPEAKER NOTES
This is the current shared frontend/backend section contract. The final heading is First feasibility experiment; Setup Overview appears separately after the 11 sections in the current frontend. Feasibility lists are numbered once; pre-existing numeric markers are stripped only for display/export, without modifying stored steps.

SOURCES AND EVIDENCE
docs/frontend-integration.md: Result Assessment outline. backend/app/render/outline.py SECTIONS. frontend/js/components/assessment-outline.js. These supersede older README preview and prototype wording.

## Slide 13

PRESENTATION TIMING: Submission handoff only; omit from the timed talk

SPEAKER NOTES
The supplied submission form says the final deadline is 18 October 2026 at 23:59 CEST. It requires unrestricted public access to source code, the six assistant-generated H01–H06 answers, slide PDF and a maximum-five-minute video, plus every participant’s registered name/email in matching order. Missing repository access leads to disqualification; missing slides/video access scores zero for the relevant criterion. These are requirements stated in the attached form, not actions taken by this assistant. This checkout has H01/H04 JSON and Markdown outputs only; H02/H03/H05/H06 must be produced by the assistant and published. No video, public access check or form submission has been performed. Source PDFs must also be supplied to reproduce ingest; adding the three uploaded PDFs to this presentation work does not populate the application’s required S01–S05 corpus.

SOURCES AND EVIDENCE
Submission form pp.1–4. Filesystem inventory of outputs/ at feature_dialog @18e4f84. No output files were edited or fabricated for the submission.

## Slide 14

PRESENTATION TIMING: Backup / reference slide

SPEAKER NOTES
Review methodology: all three attached PDFs were text-extracted and reviewed; the original deck was visually inspected. Repository documentation was checked against current frontend and rendering code, KB counts and stored H01/H04 results. Stale README top-level preview/four-tab wording and unsubstantiated old-deck aggregate test claims were not carried forward. UI screenshots run the actual frontend with mocked API responses: rule-only reading plus archived H04 result. Original raw S01–S05 PDFs were absent, so technical source-page statements here are attributed to the repository’s curated evidence, not a new independent page verification. The PowerPoint uses editable text/shapes with image screenshots, and includes sources and timing notes. No contributors’ emails or roles were supplied or invented.

SOURCES AND EVIDENCE
All sources listed on this slide. Repository URL: https://github.com/ght007/SchubKI. Source branch current at deck creation: feature_dialog @18e4f84. Main talk timings: 15+20+35+25+65+30+30+30+25+15 = 290 seconds.
