from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class InvestigationLifecyclePhase(StrEnum):
    INTAKE = "intake"
    PLANNING = "planning"
    EVIDENCE_COLLECTION = "evidence_collection"
    REASONING = "reasoning"
    RESOLUTION = "resolution"
    VERIFICATION = "verification"
    KNOWLEDGE_CAPTURE = "knowledge_capture"
    COMPLETE = "complete"
    INCONCLUSIVE = "inconclusive"


class RoundDecision(StrEnum):
    CONTINUE = "continue"
    RESOLVE = "resolve"
    STOP_INCONCLUSIVE = "stop_inconclusive"


class InvestigationRound(BaseModel):
    number: int = Field(ge=1)
    started_at: datetime
    completed_at: datetime | None = None
    objective: str
    requirement_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    leading_hypothesis_id: str | None = None
    leading_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    missing_evidence: list[str] = Field(default_factory=list)
    decision: RoundDecision = RoundDecision.CONTINUE
    decision_reason: str = ""


class HypothesisEvolution(BaseModel):
    round_number: int = Field(ge=1)
    hypothesis_id: str
    previous_status: str
    current_status: str
    previous_confidence: float = Field(ge=0.0, le=1.0)
    current_confidence: float = Field(ge=0.0, le=1.0)
    reason: str
