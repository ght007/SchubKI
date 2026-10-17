"""Stage 1: requirement extraction.

LLM first; if the LLM is unavailable a keyword-based extractor produces a usable,
clearly-marked record so the rest of the pipeline still runs.
"""
from __future__ import annotations

import re

from ..config import settings
from ..llm.client import complete_json
from ..llm.models import model_for
from ..schemas import Fact, Premise, Requirements, TraceItem, Unknown


def _prompt(name: str) -> str:
    return (settings.prompts_dir / f"{name}.md").read_text(encoding="utf-8")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]


TARGET_WORDS = ["api concentration", "api", "blend potency", "fat", "protein", "glucose", "lactate", "biomass",
                "viable biomass", "water content", "water", "moisture", "contamination", "contaminant",
                "composition", "tumor", "tumour", "concentration", "growth", "metabolic"]
METHOD_WORDS = {"NIR": [r"\bnir\b", "near-infrared", "near infrared"], "MIR": [r"\bmir\b", "mid-infrared", "mid infrared", r"\bftir\b"],
                "RAMAN": ["raman"], "FLUO": ["fluorescen", "fluorim"], "UVVIS": [r"\buv\b", "uv/vis", "uv-vis", "visible spectro"]}


def heuristic(enquiry: str, answers: dict[str, str] | None = None) -> Requirements:
    from .glossary import expand
    from .paths import general_answers
    answers = general_answers(answers)   # path-question answers are handled by paths.py
    text = expand(enquiry + " " + " ".join(f"{k}: {v}" for k, v in (answers or {}).items())).lower()
    sents = _sentences(enquiry)
    has = lambda *ws: any(w in text for w in ws)  # noqa: E731

    targets = [w for w in TARGET_WORDS if w in text]
    targets = [t for t in targets if not any(t != o and t in o for o in targets)][:5]
    undefined = has("cannot yet name", "cannot name", "not been defined", "not yet defined", "suspect contamination",
                    "unknown contaminant") and not answers
    requested = [m for m, pats in METHOD_WORDS.items() if any(re.search(p, text) for p in pats)]

    if has("powder", "blend", "granul"):
        phase = "powder"
    elif has("melt", "extrusion"):
        phase = "melt"
    elif has("tissue", "surgery"):
        phase = "tissue"
    elif has("liquid", "stream", "medium", "broth", "milk", "whey", "petroleum", "oil"):
        phase = "liquid"
    else:
        phase = "unknown"

    clear = bool(re.search(r"(?<![\w-])(clear|transparent)\b", text))      # not "non-transparent"
    opaque = has("opaque", "concentrate", "optically dense", "turbid")
    optics = "variable" if clear and opaque else "clear" if clear else "opaque" if has("opaque") else \
        "turbid" if has("turbid", "optically dense") else "unknown"

    assets = [expand(s) for s in sents
              if re.search(r"already have|existing|reuse|we have|our existing|bereits|schon|vorhanden|wiederverwend", s, re.I)]
    premises: list[Premise] = []
    for s in sents:
        low = s.lower()
        kind = None
        if re.search(r"reuse|remain valid|same concept|re-use|wiederverwend|weiter nutzen", low):
            kind = "reuse_claim"
        elif re.search(r"quote|proof|as evidence|findings", low):
            kind = "evidence_claim"
        elif re.search(r"immediately|exact|approve|ready for|sofort|genaue|freigeb", low):
            kind = "certainty_request"
        elif re.search(r"can be very sensitive|suggests adding|will remain|justification", low):
            kind = "method_claim"
        if kind:
            premises.append(Premise(id=f"P{len(premises) + 1}", statement=s, kind=kind))

    paths = []
    if re.search(r"(cheap|low[- ]cost|simple|small|iot|led) sensor|sensor at each|sensors? at (many|several|all)", text):
        paths.append("C")
    if re.search(r"(existing|our|have an?|process) analy[sz]er|calibration model|chemometric model", text):
        paths.append("A")
    if re.search(r"r&d lab|research lab|own lab\b|lab(oratory)? (system|kit|equipment)|spectrometers for (our|the) lab", text):
        paths.append("B")
    m_points = re.search(r"\b(\d{1,4})\s+(?:measuring |measurement |sampling )?(points|lines|streams|dryers|reactors|tanks|"
                         r"locations|sites|machines|presses|messstellen|linien)\b", text)
    context = "clinical" if has("surgery", "in vivo", "patient", "clinical") else \
        "lab_research" if has("laboratory classification", "research group", "laboratory study") else \
        "pilot" if has("pilot") else "unknown"
    facts = [Fact(field="enquiry", value=s[:160], status="stated", quote=s[:160]) for s in sents[:6]]
    unknowns = [
        Unknown(item="Concentration range and acceptance limits", why_it_matters="Decides sensitivity needed", impact="high"),
        Unknown(item="Process conditions at the measuring point", why_it_matters="Decides probe and interface", impact="high"),
        Unknown(item="Reference method and its uncertainty", why_it_matters="Needed for calibration", impact="medium"),
    ]
    return Requirements(
        summary=(sents[0] if sents else enquiry)[:200] + " [keyword extraction - LLM unavailable]",
        target_variables=targets, target_defined="no" if undefined else ("partial" if targets else "no"),
        matrix=phase, phase=phase, optical_behavior=optics,
        aqueous="yes" if has("aqueous", "cell culture", "ferment", "whey", "milk", "broth") else "unknown",
        fluorescent_target="no" if has("not identified a fluorescent", "no fluorescent") else "unknown",
        heterogeneous="yes" if has("heterogeneous", "inhomogeneous") else "unknown",
        temperature="hot" if has("hot", "melt") else "unknown",
        fouling_risk="yes" if has("foul", "build up", "build-up") else "unknown",
        process_context=context,
        analyzer_remote="yes" if has("another building", "outside the process area", "remote") else "unknown",
        link_length_known="no", existing_assets=assets, requested_methods=requested,
        reference_method="yes" if has("laboratory", "lab ", "reference", "assay", "measured from samples") else "unknown",
        concentration_level="trace" if has("trace", "ppm") else "unknown", preferred_paths=paths,
        measurement_points=f"{m_points.group(1)} {m_points.group(2)}" if m_points else "unknown",
        facts=facts, unknowns=unknowns, premises=premises)


def extract(enquiry: str, answers: dict[str, str], trace: list[TraceItem]) -> Requirements:
    user = f"ENQUIRY:\n{enquiry.strip()}"
    from .glossary import find
    hints = list(dict.fromkeys(f"{h['matched']} = {h['term']}" for h in find(enquiry) if h["category"] != "vague"))
    if hints:
        user += "\n\nRECOGNISED TERMS (glossary; aliases resolved, not new facts):\n" + "; ".join(hints)
    from .paths import general_answers
    gen = general_answers(answers)   # path answers go to paths.py and the report, not into extraction
    if gen:
        user += "\n\nADDITIONAL ANSWERS FROM THE CLIENT (treat as stated facts):\n" + \
                "\n".join(f"- {k}: {v}" for k, v in gen.items())
    req = complete_json("extract", model_for("extract"), _prompt("extract"), user, Requirements, trace,
                        fallback=lambda: heuristic(enquiry, answers), max_tokens=2200, temperature=0.0)
    # Guard: a model reply that is valid JSON but almost empty (no facts, no unknowns) is not
    # an extraction. Fill the empty parts from the keyword extractor and say so in the trace.
    if req is None or (not req.facts and not req.unknowns):
        backup = heuristic(enquiry, answers)
        if req is None:
            return backup
        for name in ("facts", "unknowns", "premises", "target_variables", "existing_assets", "requested_methods"):
            if not getattr(req, name):
                setattr(req, name, getattr(backup, name))
        for name in ("phase", "optical_behavior", "process_context", "analyzer_remote", "reference_method",
                     "temperature", "fouling_risk", "aqueous", "fluorescent_target", "heterogeneous"):
            if getattr(req, name) == "unknown" and getattr(backup, name) != "unknown":
                setattr(req, name, getattr(backup, name))
        if req.target_defined == "partial" and backup.target_defined == "no":
            req.target_defined = "no"
        if trace:
            trace[-1].error = (trace[-1].error + " | near-empty extraction completed by keyword extractor").strip(" |")
    return req


def apply_rejected(req: Requirements, rejected: list[str]) -> Requirements:
    """Reset requirement fields the user marked as misread ("Is this what you mean?" card) to their default,
    so no rule fires on a wrong reading. The enquiry text itself is never changed."""
    if not rejected:
        return req
    data = req.model_dump()
    for name in rejected:
        field = Requirements.model_fields.get(name)
        if field is None or name in ("summary", "facts", "unknowns", "premises"):
            continue
        data[name] = field.get_default(call_default_factory=True)
    return Requirements.model_validate(data)