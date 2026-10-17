"""Score outputs against the jury criteria (LLM-as-judge, used for development only).

  python -m eval.judge --dir outputs/dev        # D01-D08 (D01/D02 also compared with the worked answers)
  python -m eval.judge --dir outputs            # H01-H06

Weights are the challenge brief's. The judge never edits outputs; it only scores them.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.llm.client import complete_json  # noqa: E402
from backend.app.llm.models import model_for  # noqa: E402

WEIGHTS = {"technical": 30, "afs_knowledge": 20, "feasibility_plan": 15, "clarification": 15, "explainability": 10,
           "presentation": 10}


class JuryScore(BaseModel):
    technical: int = Field(ge=1, le=5)
    afs_knowledge: int = Field(ge=1, le=5)
    feasibility_plan: int = Field(ge=1, le=5)
    clarification: int = Field(ge=1, le=5)
    explainability: int = Field(ge=1, le=5)
    presentation: int = Field(ge=1, le=5)
    biggest_weakness: str
    fix: str


SYSTEM = """You are a jury member of the AFS hackathon. Score one assistant answer (1-5 per criterion):
technical (recommendations reasonable for the case), afs_knowledge (grounded in the supplied AFS materials at the right scope),
feasibility_plan (practical, useful first experiment), clarification (good questions; knows when information is insufficient),
explainability (clear, traceable, easy to review), presentation (clear structure). Penalise invented numbers, invented client facts,
guarantees, citations beyond their scope, and length used as a substitute for quality. Name the biggest weakness and a concrete fix."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="outputs/dev")
    args = ap.parse_args()
    refs = {c["id"]: c.get("reference_answer", "") for c in
            yaml.safe_load((ROOT / "eval/cases/dev_cases.yaml").read_text(encoding="utf-8"))["cases"]}
    rows = []
    for md in sorted((ROOT / args.dir).glob("*.md")):
        cid = md.stem
        user = f"ANSWER TO SCORE:\n{md.read_text(encoding='utf-8')[:9000]}"
        if refs.get(cid):
            user += f"\n\nORGANISERS' WORKED ANSWER FOR THIS CASE (one defensible answer, not the only one):\n{refs[cid]}"
        trace: list = []
        s = complete_json("judge_eval", model_for("report"), SYSTEM, user, JuryScore, trace, max_tokens=700, temperature=0.0)
        if not s:
            print(cid, "judge failed")
            continue
        total = sum(getattr(s, k) * w for k, w in WEIGHTS.items()) / 5
        rows.append({"id": cid, "weighted_pct": round(total, 1), **s.model_dump()})
        print(f"{cid}: {total:.0f}%  weakest: {s.biggest_weakness}  fix: {s.fix}")
    (ROOT / args.dir / "jury_scores.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
