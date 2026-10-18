"""Keep selected paths and their answers consistent across a what-if run."""
import asyncio

from backend.app.api import assess


def test_whatif_drops_answers_for_removed_paths_and_keeps_detected_paths(monkeypatch):
    parent = {
        "enquiry": "Measure moisture with sensors.", "preferred_paths": ["A"],
        "requirements": {"preferred_paths": ["C"]}, "rejected": ["phase"],
        "answers": {"Path A - Reference values": "No", "Path C - Key wavelengths known": "Yes",
                    "Sample": "Powder"},
    }
    monkeypatch.setattr(assess.store, "get_run", lambda _: parent)
    monkeypatch.setattr(assess, "_stream", lambda request: request)

    request = asyncio.run(assess.whatif(assess.WhatIfRequest(
        run_id="parent", preferred_paths=["B"], answers={"Path B - Where it is used": "Our R&D lab"})))

    assert request.preferred_paths == ["B"]
    assert request.rejected == ["phase"]
    assert request.answers == {"Path C - Key wavelengths known": "Yes", "Sample": "Powder",
                               "Path B - Where it is used": "Our R&D lab"}
