"""The 11-section output format: same sections and order everywhere, nothing lost, nothing invented."""
import re
from pathlib import Path

from backend.app.engine import pipeline
from backend.app.render import markdown, outline
from backend.app.schemas import AssessRequest

ROOT = Path(__file__).resolve().parents[1]
ENQUIRY = ("We want to measure moisture in a powder blend after the dryer at 12 points. We already have a silica "
           "fiber from our NIR setup and want to use MIR ATR. Lab reference is oven drying.")


def _run():
    return pipeline.run(AssessRequest(enquiry=ENQUIRY, preferred_paths=["A", "C"]))


def test_backend_sections_match_the_page():
    js = (ROOT / "frontend/js/components/assessment-outline.js").read_text(encoding="utf-8")
    page = re.findall(r'^\s*\["(\w+)", "([^"]+)"', js[js.index("const SECTIONS"):js.index("];")], re.M)
    assert page == list(outline.SECTIONS)


def test_outline_keeps_every_statement_and_citation():
    run = _run()
    sections = {s["key"]: s for s in run.outline["sections"]}
    assert [s["key"] for s in run.outline["sections"]] == [k for k, _ in outline.SECTIONS]
    r = run.report
    assert sections["requirements_stated"]["items"] == r.requirements_stated
    assert len(sections["recommendation"]["items"]) == len(r.recommendations)
    for name, key in (("measurement_concept", "measurement_concept"), ("spectral_range", "spectral_range"),
                      ("risks", "risks_and_uncertainty")):
        got = sections[key]["statements"]
        assert [s["text"] for s in got] == [s.text for s in getattr(r, name)]
        assert sum(len(s["citations"]) for s in got) == sum(len(s.citations) for s in getattr(r, name))
    cited = {(c.source, c.page) for rec in r.recommendations for s in rec.rationale for c in s.citations}
    listed = {(s["source"], s["page"]) for s in sections["sources"]["items"]}
    assert cited <= listed
    plan = sections["first_feasibility_experiment_prototype"]["plan"]
    assert plan["samples"] == r.feasibility_plan.samples and plan["steps"] == r.feasibility_plan.steps
    assert sections["decision_basis"]["items"] == r.feasibility_plan.decision_basis


def test_markdown_follows_the_same_order():
    md = markdown.render(_run(), "T")
    heads = re.findall(r"^## \d\d\. (.+)$", md, re.M)
    assert heads == [t for _, t in outline.SECTIONS]
