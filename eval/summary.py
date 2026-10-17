"""Regression table across all case sets (reads outputs/summary_*.json written by run_cases).

  python -m eval.summary
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLS = ["id", "status", "confidence", "quality", "verified", "bad_numbers", "leads", "fallbacks", "secs", "expect"]


def main() -> None:
    files = sorted((ROOT / "outputs").glob("summary_*.json"))
    if not files:
        print("No summaries yet. Run: python -m eval.run_cases --set all")
        return
    print("| " + " | ".join(COLS) + " |")
    print("|" + "---|" * len(COLS))
    for f in files:
        for r in json.loads(f.read_text(encoding="utf-8")):
            print("| " + " | ".join(str(r.get(c, "")) for c in COLS) + " |")


if __name__ == "__main__":
    main()
