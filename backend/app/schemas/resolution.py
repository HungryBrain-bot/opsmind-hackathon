from enum import StrEnum

from pydantic import BaseModel, Field


class ResolutionStage(StrEnum):
    CONTAINMENT = "containment"
    RECOVERY = "recovery"
    VERIFICATION = "verification"
    ROLLBACK = "rollback"
    PREVENTION = "prevention"


class ActionRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResolutionAction(BaseModel):
    id: str
    stage: ResolutionStage
    action: str
    rationale: str
    expected_outcome: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    risk: ActionRisk = ActionRisk.MEDIUM
    approval_required: bool = True
    rollback_action: str | None = None


class VerificationCriterion(BaseModel):
    id: str
    metric: str
    condition: str
    expected_value: str
    evidence_source: str
    status: str = "pending"


class ResolutionPlan(BaseModel):
    root_cause: str
    root_cause_hypothesis_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)
    actions: list[ResolutionAction] = Field(default_factory=list)
    verification_criteria: list[VerificationCriterion] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    human_approval_required: bool = True
    status: str = "recommended"
