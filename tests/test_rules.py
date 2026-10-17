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
