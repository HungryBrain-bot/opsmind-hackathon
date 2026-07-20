from enum import StrEnum

from pydantic import BaseModel, Field


class EvidenceDisposition(StrEnum):
    SUPPORTING = "supporting"
    CONTRADICTING = "contradicting"
    NEUTRAL = "neutral"
    INCONCLUSIVE = "inconclusive"
    DUPLICATE = "duplicate"


class EvidenceAssessment(BaseModel):
    evidence_id: str
    hypothesis_ids: list[str] = Field(default_factory=list)
    disposition: EvidenceDisposition
    quality: str = Field(pattern="^(low|medium|high)$")
    observation: str
    rationale: str


class InvestigationFinding(BaseModel):
    id: str
    statement: str
    evidence_ids: list[str] = Field(default_factory=list)
    hypothesis_ids: list[str] = Field(default_factory=list)


class EvidenceContradiction(BaseModel):
    id: str
    hypothesis_id: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    summary: str
    severity: str = Field(pattern="^(low|medium|high)$")
    resolved: bool = False


class EvidenceGap(BaseModel):
    description: str
    reason: str
    priority: str = Field(pattern="^(low|medium|high)$")
    expected_impact: str
    preferred_tool: str | None = None


class ReasoningDecision(BaseModel):
    round_number: int = Field(ge=1)
    leading_hypothesis_id: str
    evidence_sufficient: bool
    continue_investigation: bool
    summary: str
    next_actions: list[str] = Field(default_factory=list)


class ReasoningResult(BaseModel):
    assessments: list[EvidenceAssessment] = Field(default_factory=list)
    findings: list[InvestigationFinding] = Field(default_factory=list)
    contradictions: list[EvidenceContradiction] = Field(default_factory=list)
    gaps: list[EvidenceGap] = Field(default_factory=list)
    decision: ReasoningDecision
