"""
Pydantic contracts shared across ingestion, retrieval, generation, verification,
and the FastAPI routes. See docs/ai-service.md and docs/DECISIONS.md (decisions
1.4-1.7) for the reasoning behind the fields marked below.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

CompatibilityStatus = Literal["compatible", "incompatible", "unknown"]
ClaimStatus = Literal["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]
DecisionStatus = Literal["ANSWER", "QUALIFY", "ABSTAIN"]
RetrievalMethod = Literal["bm25", "dense", "hybrid"]


class Environment(BaseModel):
    runtime: str
    runtime_version: Optional[str] = None


class DebugRequest(BaseModel):
    error_message: str
    code_snippet: Optional[str] = None
    language: str
    package: str
    target_version: str
    environment: Optional[Environment] = None
    expected_behavior: Optional[str] = None


class EvidencePassage(BaseModel):
    doc_id: str
    source_url: Optional[str] = None
    title: str
    package: str
    version_range: Optional[str] = None
    doc_type: str
    section_heading: Optional[str] = None
    text: str
    published_at: Optional[str] = None
    retrieval_score: float
    retrieval_method: RetrievalMethod
    # Never defaulted to "compatible" when unknown - see DECISIONS.md 1.6.
    compatibility: CompatibilityStatus = "unknown"


class GeneratedClaim(BaseModel):
    """
    Raw claim as returned by the generator. `evidence_ids` are checked against
    what retrieval actually returned before verification runs - an id the
    generator invents is never accepted (DECISIONS.md 1.5). Any self-reported
    status here is discarded; it is never read as ground truth (DECISIONS.md 1.4).
    """

    claim: str
    evidence_ids: list[str] = Field(default_factory=list)


class GenerationResult(BaseModel):
    diagnosis: str
    proposed_fix: str
    claims: list[GeneratedClaim] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class VerifiedClaim(BaseModel):
    claim: str
    evidence_ids: list[str]
    status: ClaimStatus
    reason: str


class DebugResponse(BaseModel):
    request_id: str
    diagnosis: str
    proposed_fix: str
    decision: DecisionStatus
    claims: list[VerifiedClaim]
    evidence: list[EvidencePassage]
    limitations: list[str] = Field(default_factory=list)
    model_metadata: dict = Field(default_factory=dict, alias="model_config")
    latency_ms: float

    model_config = ConfigDict(populate_by_name=True)
