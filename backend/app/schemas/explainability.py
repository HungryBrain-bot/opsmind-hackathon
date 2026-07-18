from pydantic import BaseModel, Field


class EvidenceReference(BaseModel):
    id: str
    title: str
    source: str
    reliability: str
    current: bool


class HypothesisDecisionExplanation(BaseModel):
    hypothesis_id: str
    title: str
    selected: bool
    status: str
    confidence: float
    summary: str
    supporting_evidence: list[EvidenceReference] = Field(default_factory=list)
    contradicting_evidence: list[EvidenceReference] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    why_selected: str | None = None
    why_not_selected: str | None = None


class InvestigationDecisionTrace(BaseModel):
    investigation_id: str
    selected_hypothesis_id: str | None = None
    verdict: str | None = None
    stop_summary: str
    explanations: list[HypothesisDecisionExplanation] = Field(default_factory=list)
