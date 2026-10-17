"""All Pydantic models: Requirements, Premise, Report, Quality, Confidence, Run.

Models marked (LLM) are the JSON contracts the language model must return.
Everything else is produced by deterministic code.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

YNU = Literal["yes", "no", "unknown"]
MethodId = Literal["NIR", "MIR", "RAMAN", "UVVIS", "FLUO"]
METHOD_IDS: list[str] = ["NIR", "MIR", "RAMAN", "UVVIS", "FLUO"]
METHOD_NAMES = {
    "NIR": "NIR spectroscopy",
    "MIR": "MIR spectroscopy (ATR)",
    "RAMAN": "Raman spectroscopy",
    "UVVIS": "UV/Vis spectroscopy",
    "FLUO": "Fluorescence spectroscopy",
}
DecisionStatus = Literal["provisional_assessment", "insufficient_information", "outside_supported_scope"]
Impact = Literal["high", "medium", "low"]
ConfidenceLevel = Literal["high", "medium", "low", "insufficient"]


# ------------------------------------------------------------------ shared pieces
class Citation(BaseModel):
    source: str = Field(description="Source id, e.g. S01")
    page: int = Field(description="1-based PDF page / slide number")
    quote: str = Field(description="Short verbatim passage from that page that supports the claim")


class Statement(BaseModel):
    text: str
    kind: Literal["client_fact", "sourced", "assumption", "proposal"] = Field(
        description="client_fact = said in the enquiry; sourced = backed by citations; "
                    "assumption = not stated, labelled as assumption; proposal = our suggestion")
    citations: list[Citation] = Field(default_factory=list)


# ------------------------------------------------------------------ stage 1: extraction (LLM)
class Fact(BaseModel):
    field: str
    value: str
    status: Literal["stated", "inferred"]
    quote: str = Field(description="Words from the enquiry this fact is based on")


class Unknown(BaseModel):
    item: str
    why_it_matters: str
    impact: Impact


class Premise(BaseModel):
    id: str = Field(description="P1, P2, ...")
    statement: str = Field(description="A claim, assumption or demand made by the client")
    kind: Literal["method_claim", "reuse_claim", "evidence_claim", "certainty_request", "other"]


class Requirements(BaseModel):
    """(LLM) Structured reading of the enquiry. Unknown means the client did not say it."""
    summary: str
    target_variables: list[str] = Field(default_factory=list)
    target_defined: Literal["yes", "partial", "no"] = "partial"
    matrix: str = "unknown"
    phase: Literal["liquid", "powder", "solid", "paste", "slurry", "melt", "tissue", "gas", "mixed", "unknown"] = "unknown"
    optical_behavior: Literal["clear", "turbid", "opaque", "scattering", "variable", "unknown"] = "unknown"
    aqueous: YNU = "unknown"
    fluorescent_target: YNU = "unknown"
    heterogeneous: YNU = "unknown"
    temperature: Literal["hot", "ambient", "cold", "unknown"] = "unknown"
    fouling_risk: YNU = "unknown"
    process_context: Literal["lab_research", "pilot", "production", "clinical", "unknown"] = "unknown"
    analyzer_remote: YNU = "unknown"
    link_length_known: Literal["yes", "no"] = "no"
    existing_assets: list[str] = Field(default_factory=list)
    requested_methods: list[MethodId] = Field(default_factory=list)
    reference_method: YNU = "unknown"
    concentration_level: Literal["major", "minor", "trace", "unknown"] = "unknown"
    measurement_points: str = "unknown"
    preferred_paths: list[Literal["A", "B", "C"]] = Field(
        default_factory=list, description="AFS paths the client asks for: A = chemometric model for an analyzer / "
        "process automation, B = multi-spectral lab system for R&D, C = low-cost spectral sensor(s)")
    facts: list[Fact] = Field(default_factory=list)
    unknowns: list[Unknown] = Field(default_factory=list)
    premises: list[Premise] = Field(default_factory=list)


# ------------------------------------------------------------------ stage 2: rules (deterministic)
class SourceRef(BaseModel):
    source: str
    page: int


class RuleQuestion(BaseModel):
    text: str
    impact: Impact = "medium"
    why: str = ""


class PathHint(BaseModel):
    path: Literal["A", "B", "C"]
    effect: Literal["supports", "premature", "conflicts"]
    reason: str


class RuleHit(BaseModel):
    rule_id: str
    title: str
    severity: Literal["block", "warn", "info"] = "info"
    text: str = ""
    scores: dict[str, int] = Field(default_factory=dict)
    question: Optional[RuleQuestion] = None
    cap_confidence: Optional[ConfidenceLevel] = None
    status_hint: Optional[DecisionStatus] = None
    plan: list[str] = Field(default_factory=list)
    paths: list[PathHint] = Field(default_factory=list)
    sources: list[SourceRef] = Field(default_factory=list)


# ------------------------------------------------------------------ AFS pathway (deterministic)
class PathFit(BaseModel):
    path: Literal["A", "B", "C"]
    requested_by: Literal["expert", "enquiry", "both"]
    verdict: Literal["fits", "premature", "conflicts", "open"]
    reason: str
    sources: list[SourceRef] = Field(default_factory=list)


class ProceedPlan(BaseModel):
    path: Literal["A", "B", "C"]
    caveat: str
    steps: list[str]
    sources: list[SourceRef] = Field(default_factory=list)


class PathAnalysis(BaseModel):
    suggested: Literal["A", "B", "C", "undecided"] = "undecided"
    reasons: list[str] = Field(default_factory=list)
    sources: list[SourceRef] = Field(default_factory=list)
    requested: list[PathFit] = Field(default_factory=list)
    proceed_anyway: list[ProceedPlan] = Field(default_factory=list)


# ------------------------------------------------------------------ coverage + screening (deterministic)
class FiberFit(BaseModel):
    fiber_id: str
    name: str
    range_um: tuple[float, float]
    overlap_um: Optional[tuple[float, float]] = None
    covers: Literal["full", "partial", "none"]


class MethodCoverage(BaseModel):
    method_id: str
    method_range_um: tuple[float, float]
    fibers: list[FiberFit]
    asset_check: Optional[str] = None  # message when a client asset is incompatible


class Contribution(BaseModel):
    rule_id: str
    delta: int
    reason: str


class MethodScore(BaseModel):
    method_id: str
    name: str
    score: int
    contributions: list[Contribution] = Field(default_factory=list)
    verdict: Literal["lead", "candidate", "weak", "not_supported"] = "candidate"
    requested_by_client: bool = False


# ------------------------------------------------------------------ retrieval
class Evidence(BaseModel):
    ref: str              # E1, E2 ... id used inside prompts
    kind: Literal["claim", "chunk"]
    source: str
    page: int
    text: str
    quote: Optional[str] = None
    scope: Optional[str] = None
    highlight: Optional[str] = None   # chunks: the sentence that best matches the queries
    score: float = 0.0


# ------------------------------------------------------------------ stage 4: premise check (LLM)
class PremiseVerdict(BaseModel):
    premise_id: str
    statement: str
    verdict: Literal["supported", "partly_supported", "contradicted", "unverifiable"]
    explanation: str
    citations: list[Citation] = Field(default_factory=list)


class PremiseCheckOut(BaseModel):
    """(LLM)"""
    verdicts: list[PremiseVerdict] = Field(default_factory=list)


# ------------------------------------------------------------------ stage 6: report (LLM)
class Question(BaseModel):
    question: str
    why: str = Field(description="What the answer would change in the recommendation")
    impact: Impact


class Recommendation(BaseModel):
    method: str = Field(description="Method and geometry, e.g. 'NIR (diffuse reflection)'")
    method_ids: list[MethodId] = Field(default_factory=list)
    role: Literal["primary", "comparison", "conditional", "not_recommended"]
    rationale: list[Statement]
    conditions: str = Field(default="", description="When this applies / what must be true")


class FeasibilityPlan(BaseModel):
    samples: list[str] = Field(description="Representative samples or process states")
    reference: list[str] = Field(description="Independent reference measurements")
    comparison: list[str] = Field(description="What is compared (methods, geometries, models)")
    decision_basis: list[str] = Field(description="Go / no-go basis; targets come from the client")
    steps: list[str] = Field(default_factory=list)


class Pathway(BaseModel):
    next_step: str
    likely_path: Literal["A", "B", "C", "undecided"] = "undecided"
    why: str = ""


class Report(BaseModel):
    """(LLM) The structured first technical assessment."""
    decision_status: DecisionStatus
    headline: str = Field(description="One or two sentences: the direct answer to the client")
    requirements_stated: list[str]
    key_unknowns: list[str]
    clarification_questions: list[Question]
    recommendations: list[Recommendation]
    measurement_concept: list[Statement]
    spectral_range: list[Statement]
    risks: list[Statement]
    feasibility_plan: FeasibilityPlan
    pathway: Pathway
    assumptions: list[str] = Field(default_factory=list)


# ------------------------------------------------------------------ verification / quality / confidence
class ClaimCheck(BaseModel):
    location: str            # e.g. "risks[2]"
    text: str
    kind: str
    status: Literal["verified", "fuzzy", "unverified", "no_citation", "scope_warning"]
    detail: str = ""
    citations: list[Citation] = Field(default_factory=list)


class NumberCheck(BaseModel):
    location: str
    number: str
    status: Literal["supported", "unsupported"]
    detail: str = ""


class Verification(BaseModel):
    claims: list[ClaimCheck] = Field(default_factory=list)
    numbers: list[NumberCheck] = Field(default_factory=list)
    client_facts: list[ClaimCheck] = Field(default_factory=list)
    n_sourced: int = 0
    n_verified: int = 0
    n_unsupported_numbers: int = 0
    n_bad_client_facts: int = 0


class QualityItem(BaseModel):
    id: str
    category: Literal["structure", "grounding", "honesty", "usefulness"]
    name: str
    status: Literal["pass", "warn", "fail"]
    detail: str = ""


class Quality(BaseModel):
    items: list[QualityItem] = Field(default_factory=list)
    passed: int = 0
    total: int = 0
    repaired: bool = False
    repair_notes: list[str] = Field(default_factory=list)


class Signal(BaseModel):
    name: str
    level: ConfidenceLevel
    value: float
    detail: str


class MethodConfidence(BaseModel):
    method_id: str
    level: ConfidenceLevel
    detail: str


class Confidence(BaseModel):
    level: ConfidenceLevel
    signals: list[Signal]
    caps: list[str] = Field(default_factory=list)
    per_method: list[MethodConfidence] = Field(default_factory=list)
    raise_with: list[str] = Field(default_factory=list)


# ------------------------------------------------------------------ council (LLM judge)
class DraftScore(BaseModel):
    draft: str = Field(description="Draft letter, e.g. A")
    technical: int = Field(ge=1, le=5)
    grounding: int = Field(ge=1, le=5)
    plan: int = Field(ge=1, le=5)
    clarification: int = Field(ge=1, le=5)
    explainability: int = Field(ge=1, le=5)
    honesty: int = Field(ge=1, le=5)
    comment: str = ""


class JudgeOut(BaseModel):
    """(LLM)"""
    scores: list[DraftScore]
    best: str
    best_questions_from: str = ""
    best_plan_from: str = ""


class CouncilDraft(BaseModel):
    letter: str
    model: str
    ok: bool = True
    error: str = ""
    gate_failures: list[str] = Field(default_factory=list)
    lead_methods: list[str] = Field(default_factory=list)
    status: str = ""
    judge_total: float = 0.0


class Council(BaseModel):
    drafts: list[CouncilDraft] = Field(default_factory=list)
    judgements: list[dict] = Field(default_factory=list)  # {judge_model, scores, best}
    winner: str = ""
    merged_from: dict[str, str] = Field(default_factory=dict)
    agreement: float = 0.0
    agreement_detail: str = ""
    families: int = 0


# ------------------------------------------------------------------ coach / what-if
class CoachField(BaseModel):
    name: str
    label: str
    status: Literal["stated", "inferred", "unknown"]
    impact: Impact
    question: str = ""


class CoachTemplateOut(BaseModel):
    """(LLM)"""
    template: str = Field(description="Client's enquiry rewritten with [blanks] for every missing fact")


class Coach(BaseModel):
    completeness: int
    total: int
    fields: list[CoachField]
    template: str = ""


class WhatIfDiff(BaseModel):
    field: str
    before: str
    after: str


# ------------------------------------------------------------------ run
class TraceItem(BaseModel):
    stage: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    cached: bool = False
    ok: bool = True
    error: str = ""


class AssessRequest(BaseModel):
    enquiry: str
    answers: dict[str, str] = Field(default_factory=dict, description="Clarifications added by the expert")
    mode: Literal["fast", "council"] = "fast"
    preferred_paths: list[Literal["A", "B", "C"]] = Field(default_factory=list, description="Paths chosen by the expert")
    rejected: list[str] = Field(default_factory=list, description="Requirement fields the user marked as misread (reset to unknown)")
    parent_run_id: Optional[str] = None


class RunResult(BaseModel):
    id: str
    created: str
    mode: str
    enquiry: str
    answers: dict[str, str] = Field(default_factory=dict)
    preferred_paths: list[str] = Field(default_factory=list)
    rejected: list[str] = Field(default_factory=list)
    parent_run_id: Optional[str] = None
    requirements: Optional[Requirements] = None
    paths: Optional[PathAnalysis] = None
    rule_hits: list[RuleHit] = Field(default_factory=list)
    coverage: list[MethodCoverage] = Field(default_factory=list)
    matrix: list[MethodScore] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    retrieval: dict = Field(default_factory=dict)
    spectral: dict = Field(default_factory=dict)
    premises: list[PremiseVerdict] = Field(default_factory=list)
    report: Optional[Report] = None
    verification: Optional[Verification] = None
    quality: Optional[Quality] = None
    confidence: Optional[Confidence] = None
    council: Optional[Council] = None
    coach: Optional[Coach] = None
    diff: list[WhatIfDiff] = Field(default_factory=list)
    trace: list[TraceItem] = Field(default_factory=list)
    timings_ms: dict[str, int] = Field(default_factory=dict)
    error: str = ""