"""Run a case set -> outputs/*.md + *.json, and print a regression table.

Examples:
  python -m eval.run_cases --set final --mode council      # H01-H06 -> outputs/ (submission)
  python -m eval.run_cases --set dev                        # D01-D08 -> outputs/dev/
  python -m eval.run_cases --set adversarial                # A01-A07, checks expectations
  python -m eval.run_cases --set dev --ids D04 D06
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.engine import pipeline  # noqa: E402
from backend.app.render.markdown import render  # noqa: E402
from backend.app.schemas import AssessRequest, RunResult  # noqa: E402

SETS = {"final": ("final_cases.yaml", ROOT / "outputs"), "dev": ("dev_cases.yaml", ROOT / "outputs" / "dev"),
        "adversarial": ("adversarial_cases.yaml", ROOT / "outputs" / "adversarial")}
LEVELS = ["insufficient", "low", "medium", "high"]


def check_expect(run: RunResult, exp: dict) -> list[str]:
    problems = []
    fired = {h.rule_id for h in run.rule_hits}
    for r in exp.get("rules", []):
        if r not in fired:
            problems.append(f"rule {r} did not fire")
    if "status" in exp and run.report and run.report.decision_status != exp["status"]:
        problems.append(f"status {run.report.decision_status} != {exp['status']}")
    if "confidence_max" in exp and run.confidence and LEVELS.index(run.confidence.level) > LEVELS.index(exp["confidence_max"]):
        problems.append(f"confidence {run.confidence.level} > {exp['confidence_max']}")
    leads = {m.method_id for m in run.matrix if m.verdict == "lead"}
    for m in exp.get("method_not_lead", []):
        if m in leads:
            problems.append(f"{m} is lead")
    if exp.get("lead_any") and not leads & set(exp["lead_any"]):
        problems.append(f"lead {sorted(leads)} not in {exp['lead_any']}")
    if "max_unsupported_numbers" in exp and run.verification and \
            run.verification.n_unsupported_numbers > exp["max_unsupported_numbers"]:
        problems.append(f"{run.verification.n_unsupported_numbers} unsupported numbers")
    if exp.get("no_guarantee") and run.quality:
        h1 = next((i for i in run.quality.items if i.id == "H1"), None)
        if h1 and h1.status != "pass":
            problems.append("guarantee wording")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=list(SETS) + ["all"], default="dev")
    ap.add_argument("--mode", choices=["fast", "council"], default="fast")
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--pause", type=float, default=0.0, help="seconds between cases (free-tier rate limits)")
    args = ap.parse_args()

    sets = list(SETS) if args.set == "all" else [args.set]
    rows = []
    for s in sets:
        fname, outdir = SETS[s]
        outdir.mkdir(parents=True, exist_ok=True)
        cases = yaml.safe_load((ROOT / "eval" / "cases" / fname).read_text(encoding="utf-8"))["cases"]
        for case in cases:
            if args.ids and case["id"] not in args.ids:
                continue
            enquiry = " ".join(case["enquiry"].split())
            print(f"--> {case['id']} {case['title']} ({args.mode})", flush=True)
            t0 = time.time()
            run = pipeline.run(AssessRequest(enquiry=enquiry, mode=args.mode),
                               emit=lambda e: print(f"    {e.get('stage', '')} {e.get('status', '')} {e.get('detail', '')}"[:150])
                               if e.get("type") in ("stage", "detail") and e.get("status") != "start" else None)
            md = render(run, title=f"{case['id']} | {case['title']}")
            (outdir / f"{case['id']}.md").write_text(md, encoding="utf-8")
            (outdir / f"{case['id']}.json").write_text(json.dumps(run.model_dump(mode="json"), indent=1), encoding="utf-8")
            problems = check_expect(run, case.get("expect", {})) if case.get("expect") else []
            v, q = run.verification, run.quality
            rows.append({
                "id": case["id"], "status": run.report.decision_status if run.report else "ERROR",
                "confidence": run.confidence.level if run.confidence else "-",
                "quality": f"{q.passed}/{q.total}" if q else "-",
                "verified": f"{v.n_verified}/{v.n_sourced}" if v else "-",
                "bad_numbers": v.n_unsupported_numbers if v else "-",
                "leads": "+".join(m.method_id for m in run.matrix if m.verdict == "lead") or "-",
                "llm_calls": sum(1 for t in run.trace if not t.cached),
                "fallbacks": sum(1 for t in run.trace if not t.ok),
                "secs": round(time.time() - t0, 1),
                "expect": "OK" if not problems else "; ".join(problems) if case.get("expect") else "",
                "error": run.error,
            })
            if args.pause:
                time.sleep(args.pause)

    cols = ["id", "status", "confidence", "quality", "verified", "bad_numbers", "leads", "llm_calls", "fallbacks", "secs", "expect"]
    print("\n" + " | ".join(cols))
    for r in rows:
        print(" | ".join(str(r[c]) for c in cols) + (f"  ERROR {r['error']}" if r["error"] else ""))
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / f"summary_{args.set}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
