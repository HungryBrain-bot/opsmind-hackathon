from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis
from app.observability.telemetry import ModelUsage


class InvestigationStatus(StrEnum):
    NEW = "new"
    UNDERSTANDING = "understanding"
    PLANNING = "planning"
    COLLECTING = "collecting"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    INCONCLUSIVE = "inconclusive"
    FAILED = "failed"


class InvestigationEventType(StrEnum):
    INVESTIGATION_CREATED = "investigation_created"
    PHASE_CHANGED = "phase_changed"
    HYPOTHESES_GENERATED = "hypotheses_generated"
    EVIDENCE_PLANNED = "evidence_planned"
    TOOL_SELECTED = "tool_selected"
    TOOL_COMPLETED = "tool_completed"
    ROUND_STARTED = "round_started"
    EVIDENCE_COLLECTED = "evidence_collected"
    HYPOTHESIS_UPDATED = "hypothesis_updated"
    SUFFICIENCY_EVALUATED = "sufficiency_evaluated"
    VERDICT_GENERATED = "verdict_generated"
    INVESTIGATION_COMPLETED = "investigation_completed"
    INVESTIGATION_FAILED = "investigation_failed"
    PLANNER_COMPLETED = "planner_completed"


class InvestigationRequest(BaseModel):
    problem: str = Field(min_length=10, max_length=1000)
    environment: str = "Production"
    priority: str = "High"
    scenario_id: str = "certificate_expiry"


class TimelineEvent(BaseModel):
    timestamp: datetime
    phase: str
    title: str
    detail: str


class StopReason(BaseModel):
    sufficient: bool
    summary: str
    rules_passed: list[str] = Field(default_factory=list)
    rules_failed: list[str] = Field(default_factory=list)


class InvestigationResult(BaseModel):
    investigation_id: str
    problem: str
    status: InvestigationStatus
    environment: str
    priority: str
    scenario_id: str = "certificate_expiry"
    current_phase: str
    progress_percent: int = Field(ge=0, le=100)
    round_number: int = 0
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    next_action: str | None = None
    verdict: str | None = None
    recommended_actions: list[str] = Field(default_factory=list)
    evidence_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    investigation_completeness: float = Field(default=0.0, ge=0.0, le=1.0)
    stop_reason: StopReason = Field(
        default_factory=lambda: StopReason(
            sufficient=False,
            summary="Investigation has not yet evaluated evidence sufficiency.",
        )
    )
    timeline: list[TimelineEvent] = Field(default_factory=list)
    human_review_required: bool = True
    investigation_goal: str | None = None
    planned_evidence: list[dict[str, Any]] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    planner_usage: ModelUsage = Field(default_factory=ModelUsage)
    verdict_evidence_ids: list[str] = Field(default_factory=list)


class InvestigationEvent(BaseModel):
    sequence: int
    investigation_id: str
    type: InvestigationEventType
    timestamp: datetime
    phase: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    snapshot: InvestigationResult
