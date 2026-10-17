"""Re-run with answers, diff old vs new.

The expert answers one or more clarification questions; the enquiry is re-assessed
with those answers as stated facts and the changes are listed field by field.
"""
from __future__ import annotations

from ..schemas import RunResult, WhatIfDiff


def _leads(run: RunResult) -> str:
    if not run.report:
        return "-"
    lead = [x.method for x in run.report.recommendations if x.role == "primary"]
    return ", ".join(lead) or "none"


def _snapshot(run: RunResult) -> dict[str, str]:
    return {
        "Decision status": run.report.decision_status.replace("_", " ") if run.report else "-",
        "Confidence": run.confidence.level if run.confidence else "-",
        "Lead method(s)": _leads(run),
        "Method ranking": " > ".join(f"{m.method_id}({m.score})" for m in run.matrix[:4]),
        "Enquiry completeness": f"{run.coach.completeness}/{run.coach.total}" if run.coach else "-",
        "Open questions": str(len(run.report.clarification_questions)) if run.report else "-",
        "Likely AFS path": run.report.pathway.likely_path if run.report else "-",
        "Quality": f"{run.quality.passed}/{run.quality.total}" if run.quality else "-",
    }


def diff(before: RunResult, after: RunResult) -> list[WhatIfDiff]:
    a, b = _snapshot(before), _snapshot(after)
    return [WhatIfDiff(field=k, before=a[k], after=b[k]) for k in a if a[k] != b[k]]
