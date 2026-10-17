"""Citation exists, quote on page, numbers, client facts, evidence scope.

Fully deterministic. Statuses:
  verified      - quote found verbatim (after normalisation) on the cited page
  fuzzy         - near-verbatim (>= 90 partial ratio): shown, but flagged
  unverified    - quote not on the cited page, or page does not exist
  no_citation   - a "sourced" statement without any citation
  scope_warning - an in-vitro / lab / business source used for a readiness-type claim
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from rapidfuzz import fuzz

from ..config import settings
from ..kb.pages import normalize, normalized_pages, quote_on_page
from ..schemas import ClaimCheck, Evidence, NumberCheck, Report, Statement, Verification

READINESS = re.compile(r"\b(ready|proven|validated|clinical(ly)?|in vivo|surgery|surgical|guarantee[sd]?|"
                       r"production[- ]ready|approved)\b", re.I)
NEGATION = re.compile(r"\b(not|no|cannot|can't|never|without|outside|insufficient|does not|is not)\b", re.I)
LIMITED_SCOPE = {"S03": "in-vitro proof of concept", "S04": "lab demonstration on model tissue",
                 "S05": "business flyer", "S06": "business link"}
NUM = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)?)(?:\s*(?:-|–|to)\s*(\d+(?:[.,]\d+)?))?\s*"
                 r"(%|nm|µm|μm|um|cm-1|cm⁻¹|cm\^-1|mm|m\b|°c|ppm|ppb|mm\b|nM|µM|mM|s\b|ms\b|min\b|h\b|bar|w\b|mw)",
                 re.I)


def _statements(report: Report) -> list[tuple[str, Statement]]:
    out: list[tuple[str, Statement]] = []
    for i, r in enumerate(report.recommendations):
        out += [(f"recommendations[{i}].rationale[{j}]", s) for j, s in enumerate(r.rationale)]
    for name in ("measurement_concept", "spectral_range", "risks"):
        out += [(f"{name}[{j}]", s) for j, s in enumerate(getattr(report, name))]
    return out


@lru_cache(maxsize=1)
def _kb_number_text() -> str:
    parts = []
    for name in ("methods.json", "fibers.json", "bands.json"):
        try:
            parts.append(json.dumps(json.loads((settings.kb_dir / name).read_text(encoding="utf-8"))))
        except Exception:
            pass
    return normalize(" ".join(parts))


def all_text(report: Report) -> list[tuple[str, str]]:
    """(location, text) for every free-text field of the report."""
    items = [("headline", report.headline)]
    items += [(f"clarification_questions[{i}]", q.question + " " + q.why) for i, q in enumerate(report.clarification_questions)]
    for i, r in enumerate(report.recommendations):
        items.append((f"recommendations[{i}]", r.method + " " + r.conditions))
    items += [(loc, s.text) for loc, s in _statements(report)]
    fp = report.feasibility_plan
    for name in ("samples", "reference", "comparison", "decision_basis", "steps"):
        items += [(f"feasibility_plan.{name}[{i}]", t) for i, t in enumerate(getattr(fp, name))]
    items.append(("pathway", report.pathway.next_step + " " + report.pathway.why))
    items += [(f"assumptions[{i}]", a) for i, a in enumerate(report.assumptions)]
    return items


def _num_variants(n: str) -> set[str]:
    n = n.replace(",", ".")
    out = {n}
    if n.endswith(".0"):
        out.add(n[:-2])
    try:
        f = float(n)
        out.add(f"{f:g}")
        if f >= 1000:
            out.add(f"{f / 1000:g}")   # 2400 nm <-> 2.4 um
        else:
            out.add(f"{f * 1000:g}")
    except ValueError:
        pass
    return out


def check_numbers(report: Report, allowed_corpus: str) -> list[NumberCheck]:
    corpus = allowed_corpus
    checks = []
    for loc, text in all_text(report):
        for m in NUM.finditer(text):
            nums = [x for x in (m.group(1), m.group(2)) if x]
            ok = all(any(re.search(rf"(?<![\d.]){re.escape(v)}(?![\d])", corpus) for v in _num_variants(x)) for x in nums)
            checks.append(NumberCheck(location=loc, number=m.group(0).strip(), status="supported" if ok else "unsupported",
                                      detail="" if ok else "not found in the enquiry, the evidence or the cited pages"))
    return checks


def _content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z0-9-]{3,}", text.lower())} - {
        "that", "this", "with", "from", "have", "they", "their", "which", "would", "should", "client", "customer",
        "states", "stated", "says", "wants", "their", "process", "there", "been", "into", "only"}


def check_statement(loc: str, s: Statement) -> ClaimCheck:
    if s.kind != "sourced":
        return ClaimCheck(location=loc, text=s.text, kind=s.kind, status="verified" if s.kind != "sourced" else "no_citation",
                          detail="not a sourced claim", citations=s.citations)
    if not s.citations:
        return ClaimCheck(location=loc, text=s.text, kind=s.kind, status="no_citation", detail="sourced claim without citation")
    pages = normalized_pages()
    statuses, details = [], []
    for c in s.citations:
        if (c.source, c.page) not in pages:
            statuses.append("unverified")
            details.append(f"{c.source} p.{c.page} does not exist")
        elif quote_on_page(c.quote, c.source, c.page):
            statuses.append("verified")
        else:
            score = fuzz.partial_ratio(normalize(c.quote), pages[(c.source, c.page)])
            if score >= 90:
                statuses.append("fuzzy")
                details.append(f"{c.source} p.{c.page}: near-verbatim ({score:.0f})")
            else:
                statuses.append("unverified")
                details.append(f"{c.source} p.{c.page}: quote not on page ({score:.0f})")
    status = "verified" if "verified" in statuses else "fuzzy" if "fuzzy" in statuses else "unverified"
    limited = [c for c in s.citations if c.source in LIMITED_SCOPE]
    if status != "unverified" and limited and READINESS.search(s.text) and not NEGATION.search(s.text):
        status = "scope_warning"
        details.append(f"{limited[0].source} is {LIMITED_SCOPE[limited[0].source]}; it cannot support a readiness claim")
    return ClaimCheck(location=loc, text=s.text, kind=s.kind, status=status, detail="; ".join(details), citations=s.citations)


def _sentences(text: str) -> list[str]:
    out = []
    for block in re.split(r"\n\s*-\s+|\n\s*\n", text):          # bullets and paragraphs first
        block = re.sub(r"\s+", " ", block)
        block = re.sub(r"(\w)- (\w)", r"\1-\2", block)
        for p in re.split(r"(?<=[.!?;])\s+(?=[A-Z\"(])|\"\s+\"", block):
            p = p.strip(' "')
            if 25 <= len(p) <= 400:
                out.append(p)
    return out


def _best_sentence(quote: str, source: str, pages: list[int]) -> tuple[int, str, float]:
    from ..kb.pages import load_pages
    best = (0, "", 0.0)
    nq = normalize(quote)
    for p in pages:
        raw = load_pages().get((source, p))
        if not raw:
            continue
        for sent in _sentences(raw):
            score = fuzz.token_set_ratio(nq, normalize(sent))
            if score > best[2]:
                best = (p, sent, score)
    return best


def align_citations(report: Report) -> set[str]:
    """Quote alignment. Models often paraphrase a quote slightly. If a sentence on the cited page
    (or, failing that, another page of the same source) clearly matches, the quote is replaced by
    the page's exact wording, so the reader sees real source text. Weak matches are left alone and
    stay unverified. Returns the corrected quotes (shown as "aligned" in the verifier)."""
    from ..kb.pages import load_pages
    fixed: set[str] = set()
    all_pages: dict[str, list[int]] = {}
    for (src, pg) in load_pages():
        all_pages.setdefault(src, []).append(pg)
    for _, s in _statements(report):
        for c in s.citations:
            if quote_on_page(c.quote, c.source, c.page):
                continue
            page, sent, score = _best_sentence(c.quote, c.source, [c.page])
            if score >= 75 and sent:
                c.quote = sent
                fixed.add(sent)
                continue
            page, sent, score = _best_sentence(c.quote, c.source, all_pages.get(c.source, []))
            if score >= 90 and sent:
                c.page, c.quote = page, sent
                fixed.add(sent)
    return fixed


def verify(report: Report, enquiry: str, answers: dict[str, str], evidence: list[Evidence]) -> Verification:
    aligned = align_citations(report)
    claims = [check_statement(loc, s) for loc, s in _statements(report)]
    for c in claims:
        if any(cit.quote in aligned for cit in c.citations) and c.status == "verified":
            c.detail = (c.detail + "; " if c.detail else "") + "quote aligned to the exact page wording"
    sourced = [c for c in claims if c.kind == "sourced"]

    cited_pages = {(c.source, c.page) for s in sourced for c in s.citations}
    pages = normalized_pages()
    corpus = " ".join([normalize(enquiry), normalize(" ".join(answers.values())),
                       *(normalize(e.text + " " + (e.quote or "")) for e in evidence),
                       *(pages.get(p, "") for p in cited_pages), _kb_number_text()])
    numbers = check_numbers(report, corpus)

    client_text = enquiry + " " + " ".join(f"{k} {v}" for k, v in answers.items())
    cw = _content_words(client_text)
    client = []
    for loc, s in _statements(report):
        if s.kind != "client_fact":
            continue
        words = _content_words(s.text)
        overlap = len(words & cw) / max(1, len(words))
        ok = overlap >= 0.5 or fuzz.partial_ratio(normalize(s.text), normalize(client_text)) >= 80
        client.append(ClaimCheck(location=loc, text=s.text, kind="client_fact", status="verified" if ok else "unverified",
                                 detail="" if ok else f"only {overlap:.0%} of its words appear in the enquiry"))
    return Verification(
        claims=claims, numbers=numbers, client_facts=client, n_sourced=len(sourced),
        n_verified=sum(1 for c in sourced if c.status in ("verified", "fuzzy")),
        n_unsupported_numbers=sum(1 for n in numbers if n.status == "unsupported"),
        n_bad_client_facts=sum(1 for c in client if c.status != "verified"))