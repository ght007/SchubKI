"""Quote matching, number checks, knowledge-base integrity (needs data/raw)."""
import json

import pytest

from backend.app.config import settings
from backend.app.kb.pages import load_pages, normalize, quote_on_page
from backend.app.engine.verify import check_statement
from backend.app.schemas import Citation, Statement

needs_sources = pytest.mark.skipif(not (settings.raw_dir / "S01_Multispectral_Laboratory.pdf").exists(),
                                   reason="source PDFs not in data/raw")


def test_normalize_handles_ligatures_and_linebreak_hyphens():
    assert normalize("ﬁber  well-\nsuited µm") == "fiber well-suited um"


@needs_sources
def test_every_curated_claim_quote_is_on_its_page():
    load_pages.cache_clear()
    for line in (settings.kb_dir / "claims.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(line)
        assert quote_on_page(c["quote"], c["source"], c["page"]), c["id"]


@needs_sources
def test_wrong_page_is_unverified():
    s = Statement(text="NIR is the most common online method.", kind="sourced",
                  citations=[Citation(source="S01", page=3, quote="Near-IR vibrational spectroscopy (NIR) is the most common online analysis method")])
    assert check_statement("x", s).status == "unverified"


@needs_sources
def test_readiness_claim_from_in_vitro_source_is_flagged():
    s = Statement(text="The LED sensor is validated and ready for surgery.", kind="sourced",
                  citations=[Citation(source="S03", page=14, quote="This study provides a proof-of-concept demonstration of the LED-based sensor for tumor discrimination.")])
    assert check_statement("x", s).status == "scope_warning"


def test_sourced_without_citation():
    assert check_statement("x", Statement(text="a", kind="sourced")).status == "no_citation"
