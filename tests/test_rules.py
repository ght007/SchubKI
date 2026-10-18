"""Fiber coverage + scope rules (deterministic, no LLM)."""
from backend.app.engine import coverage, rules, screen
from backend.app.schemas import Premise, Requirements


def _req(**kw) -> Requirements:
    return Requirements(summary="test", **kw)


def test_silica_asset_blocks_mir_and_coverage_flags_it():
    r = _req(requested_methods=["MIR"], existing_assets=["silica fiber cable from a NIR setup"])
    hits = {h.rule_id: h for h in rules.evaluate(r, "water in oil with MIR ATR")}
    assert hits["R_FIBER_SILICA_MIR"].severity == "block"
    mir = next(c for c in coverage.compute(r) if c.method_id == "MIR")
    assert mir.asset_check and "2.4" in mir.asset_check
    assert next(f for f in mir.fibers if f.fiber_id == "PIR").covers != "none"


def test_fluorescence_without_target_is_not_supported():
    r = _req(requested_methods=["FLUO"], fluorescent_target="no", target_variables=["glucose"])
    m = {x.method_id: x for x in screen.screen(r, rules.evaluate(r, "fluorescence for glucose"))}
    assert m["FLUO"].verdict == "not_supported"
    assert m["RAMAN"].score > m["FLUO"].score


def test_clinical_use_is_outside_scope():
    r = _req(process_context="clinical", premises=[Premise(id="P1", statement="quote study as proof", kind="evidence_claim")])
    hints = {h.status_hint for h in rules.evaluate(r, "use in live surgery")}
    assert "outside_supported_scope" in hints


def test_undefined_target_is_insufficient_information():
    hits = rules.evaluate(_req(target_defined="no"), "something goes wrong")
    assert any(h.status_hint == "insufficient_information" for h in hits)


def test_every_rule_has_sources():
    assert all(r.get("sources") for r in rules.load_rules())


def test_glossary_resolves_german_and_triggers_fiber_rule():
    from backend.app.engine import glossary, precheck
    text = "Wir haben schon eine Glasfaser vom NIR-Aufbau und wollen MIR ATR für die Feuchte nutzen."
    assert {"silica fiber", "MIR spectroscopy", "moisture"} <= set(glossary.canonical_terms(text))
    assert any(w["rule_id"] == "R_FIBER_SILICA_MIR" for w in precheck.run(text)["warnings"])


def test_path_answers_set_verdicts_and_stay_out_of_keyword_heuristics():
    from backend.app.engine import coach, extract, paths
    ans = {"Path C - Key wavelengths known": "No", "Path B - Where it is used": "In production; for the plant",
           "Path A - Reference values": "Yes"}
    text = "We want cheap sensors at many points to measure moisture in powder."
    req = extract.heuristic(text, ans)
    a = paths.analyse(rules.evaluate(req, text, ans), req, ["B", "C"], ans)
    verdicts = {f.path: f.verdict for f in a.requested}
    assert verdicts == {"B": "conflicts", "C": "premature"}
    # "Reference values: Yes" must not be read as a stated reference method by the keyword coach
    assert next(f for f in coach.fields(req, ans) if f.name == "reference").status == "unknown"


def test_understand_merges_questions_prefills_and_rejects():
    from backend.app.engine import extract, understand
    text = "We want cheap sensors at 40 points to measure moisture in a powder dryer. Lab reference is oven drying."
    u = understand.run(text, {}, ["A"])
    keys = [q["key"] for q in u["questions"]]
    assert "Reference method" not in keys                       # covered by Path A's one-click question
    pre = {q["key"]: q["prefill"] for q in u["questions"]}
    assert pre["Path A - Reference values"] == "Yes"
    assert pre["Path C - Measuring points"] == "More than 10"   # C detected in the text, 40 points read
    req = extract.apply_rejected(extract.heuristic(text), ["phase", "target_variables"])
    assert req.phase == "unknown" and req.target_variables == []