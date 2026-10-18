# AFS Assessment Assistant — presenter notes

Main talk: **4 minutes 20 seconds**, plus transition allowance. Slides 12–13 are backup material.

**Team:** Eisa Atif, Marie Habermann, Atfan Deshmukh, Akshdeep Singh, Naumanurrahman Shaikmujeeburrahman.

All demo screenshots come from the current unmodified application with an isolated local SQLite database, rule-only mode and hashing embeddings. Saved Council results are a separate evidence set.

## Slide 1 — 10 seconds

Our assistant turns enquiries into reviewable spectroscopy experiments. Here are six final-case results and four working features: clarification, evidence review, the Coach, and knowledge expansion.

**Sources:** README; current code at 40dd40b; official challenge brief pp.1–3; user-supplied team names.

**Limits / demo detail:** All five names are credited equally; no individual roles have been invented. The deck updates both supplied drafts. Main talk totals 260 seconds, leaving 40 seconds for transitions within five minutes.

## Slide 2 — 20 seconds

The evaluation uses all six official final scenarios. They test calibration transfer, optical geometry, selectivity, fiber physics, an undefined target, and the scope of research evidence. These are decision tests, not a presentation of measurement accuracy. The feature demos connect directly to the weighted judging criteria shown here.

**Sources:** customer_scenarios_for_final_evaluation.txt from materials.zip; challenge brief p.3; six archived H01–H06 Council answers.

**Limits / demo detail:** H01–H04 archived runs include extra path answers. H05 still receives a provisional status despite an undefined target; this is a reported evaluation gap, not a pass.

## Slide 3 — 35 seconds

Here are the actual saved Council results, before showing the demos. Thirty-five of forty-four counted source checks verify. Four unsupported-number flags remain, and none of the six reports claims high confidence. The check totals range from twelve to fifteen out of sixteen. H06 is outside scope, as it should be. H05 still says provisional despite the undefined target. We treat these as inspectable results and remaining defects, rather than claiming a perfect score.

**Sources:** evaluation/council_archive_audit.json; archived Markdown from origin/presentation@807609d. Ratios are from each report’s own verification totals; 35/44 = 79.5%.

**Limits / demo detail:** These are stored Council outputs, not fresh paid LLM runs. Some include expert path answers, so they cannot be compared as controlled paired trials with the unanswered offline baseline. Quality checks include heuristic rules, can produce false positives, and do not cover every sentence or prove semantic correctness. There is no jury score or spectral prediction benchmark.

## Slide 4 — 20 seconds

The model interprets the enquiry and drafts an assessment. Code applies sourced rules, retrieves evidence, checks claims and numbers, and computes confidence. Council adds multiple drafts and review. The starting knowledge base has ninety-five claim cards and thirty-five rules; the report has sixteen quality checks.

**Sources:** README; docs/frontend-integration.md; backend/app modules pipeline, understand, rules, retrieve, report, verify, quality, confidence, coach, whatif; data/kb. Snapshot 40dd40b.

**Limits / demo detail:** Source inventory: six supplied AFS sources, 65 PDF pages, 275 index records; a separately registered three-page business brief brings the complete initial test index to 68 pages / 281 records. Cards and rules are curated, not all automatically learned. Council uses three model endpoints from two model families; agreement is not three independent experiments.

## Slide 5 — 25 seconds

Start with the enquiry review. The assistant exposes its reading and the customer’s own claims, including the silica-to-MIR conflict. The user can correct facts and answer the questions that matter before selecting Yes, assess. The original enquiry stays visible; answers are recorded separately. This makes clarification part of the workflow instead of burying it after a confident recommendation.

**Sources:** assets/clarification-review.png and clarification-questions.png; real browser and unmodified local API. Run 990e8459a5, generated from official H04 input, LLM_MOCK=1, hashing embeddings, SQLite.

**Limits / demo detail:** Screenshots are actual local rule-only behavior, not the saved Council run on slide 3. Optional answers do not imply that missing information has been supplied. The dialog has Yes, assess and return/close behavior; no skip button or every-run checkbox is advertised.

## Slide 6 — 30 seconds

Click a citation to open the PDF alongside the report. Here, S02 page six gives the fiber transmission ranges. The central result is physical: the existing silica cable cannot simply carry the requested MIR signal. A new infrared fiber and the actual route require confirmation. S02 page thirteen supports investigating water in petroleum in the lab; it does not establish a validated remote process installation.

**Sources:** Actual screenshot assets/evidence-split.png, cropped to enlarge the unchanged PDF pane. Supplied S02_Process_Control_Slides, pp.6,9,13; manual image transcription in data/kb/s02_notes.md and curated claim cards.

**Limits / demo detail:** The UI supports a draggable split and starts at 50/50; the app header hides while the PDF is open. The source page is image-based, so curated transcription is an additional verification dependency. The saved Council H04 output cites S11 p.13 in some sections; S11 is not in the committed source registry. That gap is disclosed on slide 10. Wavelength ranges describe source specifications, not a promised installation distance or detection limit.

## Slide 7 — 25 seconds

Use representative samples and an independent water reference such as Karl Fischer. Compare NIR on the existing silica link with MIR ATR only if an infrared link is confirmed. Validate on held-out samples against customer-agreed error, robustness and installation constraints. The acceptance limits must come from the customer, rather than an arbitrary R-squared threshold.

**Sources:** Archived H04 Council report §11, compressed and edited as a presentation example; supplied S02 p.13 shows lab petroleum spectra, not process accuracy. The complete saved Council answer remains unedited in its original archive.

**Limits / demo detail:** This is a proposed feasibility plan; no experiment has been performed here. The Council plan uses the illustrative source range 0.1–2.0% and its decision basis includes R² > 0.95; neither is an established client requirement. The fresh keyword fallback also introduces irrelevant formulation-reuse steps in H04. Those are limitations rather than examples to reproduce in the recommended plan.

## Slide 8 — 25 seconds

In this real Coach re-run, we add illustrative customer answers about optical behavior, a reference method, operating conditions and acceptance criteria. Completeness moves from two to nine of ten. Confidence stays low because answering questions does not repair the silica-to-MIR incompatibility. The re-run retains its parent and shows a comparison, so the expert can see what changed.

**Sources:** evaluation/coach_after.json; evaluation/demo_evidence.json; actual screenshot coach-after.png. Before run 990e8459a5; after c36bf79f5c. Diff: completeness 2/10→9/10; MIR and NIR screening scores change; low confidence remains.

**Limits / demo detail:** The seven entered answers are explicitly illustrative and are not final evaluation-case ground truth. Rule-only, hashing, SQLite. Completeness is a ten-field information checklist, not measured scientific correctness. The checker marks some information as stated based on answer text; customer confirmation remains necessary.

## Slide 9 — 30 seconds

The knowledge base can grow through the actual editor. We upload a short excerpt from supplied S01, register its source and evidence scope, and try an invented quotation. Validation rejects it. An exact quotation passes, and saving creates a version with a human comment before rebuilding the index. The isolated index grows from two hundred eighty-one to two hundred eighty-three records: one document chunk and one claim card.

**Sources:** assets/kb-register.png, kb-rejected-quote.png, kb-validated-diff.png and kb-version-history.png; evaluation/demo_evidence.json; backend/app/kb/files.py, api/kb_admin.py and kb/ingest.py. Source S07 is a demonstration excerpt of S01 p.8. claims.jsonl version 2.

**Limits / demo detail:** This demonstrates controlled expansion, not autonomous science or automatic rule learning. The card keeps S01’s overview scope. Rejected quotation is absent from the uploaded page. Local KB_EDIT=open and guest attribution are demo-only; the project includes authenticated owner/admin controls for deployed settings. The demo changed only scratch files outside the repository and did not write to Supabase.

## Slide 10 — 30 seconds

Three priorities remain. Verify every report section: an R-squared threshold escapes the number checker, and H04 cites S11, absent from the committed registry. Tighten the undefined-target gate and reduce heuristic false warnings. Validate usefulness with experts and samples. Separately, fresh offline checks completed twenty-one runs, met seven adversarial expectations, and passed eighty-one tests. Those establish regression coverage; model quality still needs expert evaluation.

**Sources:** Council audit: H02 one number flag, H05 three; H04 S11 and R² >0.95; H05 provisional. Fresh baseline: 6 final + 8 dev + 7 adversarial; pytest 81 passed, 20 skipped, 2 warnings. Current snapshot 40dd40b.

**Limits / demo detail:** Saved Council trace durations 72.289–188.733 seconds, median 141.4535 s; includes cached calls/failures/fallbacks, not a controlled latency benchmark. Some H06 flags arise around negated readiness language; do not treat every heuristic flag as a confirmed scientific error. The rule-only fallback’s quote checks can pass even when its plan includes irrelevant formulation steps in H04. No spectra, reference labels or expert ratings were supplied for quantitative sensor-performance validation.

## Slide 11 — 10 seconds

Clarify the request, inspect the evidence, and agree the next experiment. Our working prototype makes both its recommendations and its remaining validation gaps visible. Thank you.

**Sources:** Repository ght007/SchubKI; current code, captured demos and archived final outputs. Team names supplied by the user.

**Limits / demo detail:** End the main talk here at approximately 4 minutes 20 seconds. The following two slides are backup material for questions.

## Slide 12 — backup

If asked about evaluation rigor, use this slide to explain which claim each evidence set supports. The Council archive shows actual model-generated final answers. The fresh deterministic baseline checks the current pipeline and guard behavior without spending LLM calls. Tests cover software behavior; the UI captures prove workflows. None is a measured spectral prediction result.

**Sources:** evaluation/run_baseline.py calls the unchanged application pipeline with official H01–H06, eval/cases/dev_cases.yaml and eval/cases/adversarial_cases.yaml, using the existing check_expect helper. pytest.xml records full-suite outcome. See accompanying Evaluation_Audit.md for commands, per-case metrics and limitations.

**Limits / demo detail:** The full source registry is needed for the suite. Supplied challenge brief was restored in the isolated raw corpus under its already-registered name, resolving a source-missing setup failure before the final suite run. 20 account/database variants require AUTH_TEST_PG_URL and were skipped. Two pre-existing deprecation warnings remain. The 179/179 count is exact-quote checking of selected typed fields, not all assertions or independent fact validation.

## Slide 13 — backup

Use this source map when asked about AFS knowledge. Overview material supports screening; company slides show the relevant fiber and application examples; the kidney and combined-method papers remain within their laboratory scope. Flyers and links are business context, not a detection-limit or readiness claim.

**Sources:** Reviewed current repository snapshot 40dd40b, including README.md and docs/frontend-integration.md; AST inventory of 126 source/doc/config files (14,820 lines); all core pipeline, UI, KB and evaluation paths. Both supplied presentation drafts and the submission/challenge documents were read. Sources are the materials.zip versions and supplied PDFs.

**Limits / demo detail:** Document instructions were treated as challenge context; no hackathon form was submitted and no third-party messages were sent. Source PDFs are not redistributed in the presentation package. Embedded slide notes retain precise context, demo conditions and limits. Old draft claims of perfect tests or missing final answers have been replaced with the current auditable findings.
