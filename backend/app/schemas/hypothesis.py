from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.confidence import ConfidenceChange


class HypothesisStatus(StrEnum):
    ACTIVE = "active"
    SUPPORTED = "supported"
    REJECTED = "rejected"
    WAITING = "waiting"


class Hypothesis(BaseModel):
    id: str
    title: str
    rationale: str
    status: HypothesisStatus = HypothesisStatus.ACTIVE
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    confidence_history: list[ConfidenceChange] = Field(default_factory=list)
    rejection_reason: str | None = None
