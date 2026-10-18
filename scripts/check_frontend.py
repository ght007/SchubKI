"""Check the frontend files: every import points to a real file and every imported name is exported.

A single missing file or missing export stops the whole UI (blank page). Run from the repo root:
    python scripts/check_frontend.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "frontend"
IMPORT = re.compile(r'^import\s+(.+?)\s+from\s+"([^"]+)"', re.M)
EXPORT_DECL = re.compile(r"^export\s+(?:async\s+)?(?:function\*?|const|let|class)\s+(\w+)", re.M)
EXPORT_LIST = re.compile(r"^export\s*\{([^}]*)\}", re.M)


def exports_of(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    names = set(EXPORT_DECL.findall(text))
    for group in EXPORT_LIST.findall(text):
        names |= {n.split(" as ")[-1].strip() for n in group.split(",") if n.strip()}
    return names


def main() -> int:
    problems: list[str] = []
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for ref in re.findall(r'(?:src|href)="/static/([^"]+)"', html):
        if not (ROOT / ref).exists():
            problems.append(f"index.html refers to frontend/{ref}, which does not exist")
    for ident in ("status", "fiber", "view", "drawer", "account-actions", "reading-review", "nav-back", "evidence-divider"):
        if f'id="{ident}"' not in html:
            problems.append(f'index.html has no element id="{ident}"')

    # The enquiry stays in the page; the reading review has a persistent dialog outside the tab content.
    enquiry = (ROOT / "js/components/enquiry.js").read_text(encoding="utf-8")
    for ident in ("precheck", "pathpick", "enq"):
        if f'id="{ident}"' not in enquiry:
            problems.append(f'Reading has no element id="{ident}"')

    files = sorted((ROOT / "js").rglob("*.js"))
    for f in files:
        for what, target in IMPORT.findall(f.read_text(encoding="utf-8")):
            dep = (f.parent / target).resolve()
            rel = f.relative_to(ROOT)
            if not dep.exists():
                problems.append(f"{rel} imports {target}, but frontend/{dep.relative_to(ROOT.resolve()) if ROOT.resolve() in dep.parents else dep} is missing")
                continue
            names = re.findall(r"\b(\w+)\b", what.split("{", 1)[1]) if "{" in what else []
            names = [n for n in names if n != "as"]
            missing = [n for n in names if n not in exports_of(dep)]
            if missing:
                problems.append(f"{rel} needs {', '.join(missing)} from {target}, but that file does not export it (old version?)")

    print(f"Checked {len(files)} JS files in {ROOT}")
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print(" -", p)
        return 1
    print("All imports and exports match. If the page is still blank: F12 -> Console, and send the red error.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
