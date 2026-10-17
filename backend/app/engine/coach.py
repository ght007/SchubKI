"""Completeness score, impact-ranked unknowns, template.

Ten decision-relevant facts are checked against the extracted requirements. The
template (LLM, with a deterministic fallback) contains [blanks]; it never fills them.
"""
from __future__ import annotations

import re

from ..config import settings
from ..llm.client import complete_json
from ..llm.models import model_for
from ..schemas import Coach, CoachField, CoachTemplateOut, Requirements, TraceItem


def _facts_mention(req: Requirements, *words: str) -> bool:
    text = " ".join(f"{f.field} {f.value}" for f in req.facts).lower()
    return any(w in text for w in words)


def fields(req: Requirements, answers: dict[str, str]) -> list[CoachField]:
    from .paths import general_answers
    ans = " ".join(f"{k} {v}" for k, v in general_answers(answers).items()).lower()
    a = lambda *w: any(x in ans for x in w)  # noqa: E731

    def st(known: bool, inferred: bool = False) -> str:
        return "stated" if known else "inferred" if inferred else "unknown"

    return [
        CoachField(name="target", label="Target variable / analyte", impact="high",
                   status="stated" if req.target_defined == "yes" else "inferred" if req.target_defined == "partial" else "unknown",
                   question="Which variable or analyte must be measured, and which changes must be distinguished?"),
        CoachField(name="matrix", label="Sample matrix and phase", impact="high",
                   status=st(req.phase != "unknown" and req.matrix not in ("", "unknown"), req.phase != "unknown"),
                   question="What is the sample (liquid, powder, melt, tissue...) and its main components?"),
        CoachField(name="optics", label="Optical behaviour (clear / turbid / opaque)", impact="high",
                   status=st(req.optical_behavior != "unknown" or a("clear", "turbid", "opaque")),
                   question="Is the sample clear, turbid or opaque, and does this change during the process?"),
        CoachField(name="range", label="Concentration range", impact="high",
                   status=st(req.concentration_level != "unknown" or _facts_mention(req, "%", "range", "ppm", "mg", "g/l") or a("range", "%")),
                   question="What concentration range must be covered, and what is the smallest change that matters?"),
        CoachField(name="reference", label="Reference method", impact="high",
                   status=st(req.reference_method == "yes" or a("reference", "assay", "lab")),
                   question="Which independent reference method (and its uncertainty) can provide calibration values?"),
        CoachField(name="accuracy", label="Accuracy / acceptance criteria", impact="medium",
                   status=st(_facts_mention(req, "accuracy", "acceptance", "limit", "tolerance") or a("accuracy", "acceptance", "tolerance")),
                   question="Which accuracy, bias or acceptance limits must the measurement meet?"),
        CoachField(name="conditions", label="Process conditions at the probe", impact="high",
                   status=st(req.temperature != "unknown" or req.fouling_risk != "unknown" or a("temperature", "pressure", "°c")),
                   question="What temperature, pressure, flow, fouling and cleaning conditions apply at the probe?"),
        CoachField(name="installation", label="Installation and fiber link", impact="medium",
                   status=st(req.link_length_known == "yes" or a("length", "distance", " m ", "metre", "meter"),
                             req.analyzer_remote != "unknown"),
                   question="Where can the probe be installed, and how far away will the analyzer be?"),
        CoachField(name="points", label="Number of measuring points", impact="low",
                   status=st(req.measurement_points not in ("", "unknown") or a("points", "streams", "lines")),
                   question="How many measuring points or streams need monitoring?"),
        CoachField(name="timing", label="Response time / update rate", impact="medium",
                   status=st(_facts_mention(req, "second", "minute", "real time", "response") or a("second", "minute", "response")),
                   question="How quickly must a change be detected (update rate, response time)?"),
    ]


def fallback_template(enquiry: str, missing: list[CoachField]) -> str:
    lines = [enquiry.strip(), ""]
    lines += [f"{f.label}: [{f.question.rstrip('?')}]" for f in missing]
    return "\n".join(lines)


def build(enquiry: str, req: Requirements, answers: dict[str, str], trace: list[TraceItem],
          with_template: bool = True) -> Coach:
    fs = fields(req, answers)
    order = {"high": 0, "medium": 1, "low": 2}
    fs.sort(key=lambda f: (f.status != "unknown", order[f.impact]))
    known = sum(1 for f in fs if f.status == "stated") + 0.5 * sum(1 for f in fs if f.status == "inferred")
    missing = [f for f in fs if f.status == "unknown"]
    template = ""
    if with_template and missing:
        system = (settings.prompts_dir / "coach.md").read_text(encoding="utf-8")
        user = f"ENQUIRY:\n{enquiry}\n\nMISSING:\n" + "\n".join(f"- {f.label}: {f.question}" for f in missing)
        out = complete_json("coach", model_for("coach"), system, user, CoachTemplateOut, trace,
                            fallback=lambda: CoachTemplateOut(template=fallback_template(enquiry, missing)),
                            max_tokens=900, temperature=0.2)
        template = out.template if out else fallback_template(enquiry, missing)
        if not re.search(r"\[[^\]]+\]", template):   # model filled the blanks: refuse it
            template = fallback_template(enquiry, missing)
    return Coach(completeness=int(round(known)), total=len(fs), fields=fs, template=template)