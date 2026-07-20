from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class GraphNodeType(StrEnum):
    INCIDENT = "incident"
    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    ENTITY = "entity"
    RESOLUTION = "resolution"


class GraphEdgeType(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    RELATES_TO = "relates_to"
    RESOLVES = "resolves"


class WorkspaceGraphNode(BaseModel):
    id: str
    label: str
    node_type: GraphNodeType
    status: str = "neutral"
    confidence: float | None = None
    subtitle: str | None = None
    detail: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class WorkspaceGraphEdge(BaseModel):
    source: str
    target: str
    edge_type: GraphEdgeType
    label: str | None = None


class WorkspaceGraph(BaseModel):
    nodes: list[WorkspaceGraphNode] = Field(default_factory=list)
    edges: list[WorkspaceGraphEdge] = Field(default_factory=list)


class WorkspaceTimelineItem(BaseModel):
    sequence: int
    timestamp: datetime
    phase: str
    title: str
    detail: str
    kind: str = "activity"


class ConfidencePoint(BaseModel):
    round_number: int
    confidence: float = Field(ge=0.0, le=1.0)
    label: str
    reason: str


class WorkspaceHypothesis(BaseModel):
    id: str
    title: str
    rationale: str
    status: str
    confidence: float
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    rejection_reason: str | None = None


class WorkspaceResolutionStage(BaseModel):
    id: str
    stage: str
    title: str
    action: str
    rationale: str
    expected_outcome: str
    risk: str
    confidence: float
    approval_required: bool
    evidence_ids: list[str] = Field(default_factory=list)
    rollback_action: str | None = None


class WorkspaceVerificationItem(BaseModel):
    id: str
    metric: str
    condition: str
    expected_value: str
    source: str
    status: str


class InvestigationWorkspace(BaseModel):
    investigation_id: str
    problem: str
    environment: str
    priority: str
    status: str
    phase: str
    progress_percent: int
    round_number: int
    verdict: str | None = None
    leading_hypothesis_id: str | None = None
    leading_hypothesis: str | None = None
    overall_confidence: float = 0.0
    evidence_strength: float = 0.0
    completeness: float = 0.0
    next_action: str | None = None
    missing_evidence: list[str] = Field(default_factory=list)
    graph: WorkspaceGraph = Field(default_factory=WorkspaceGraph)
    timeline: list[WorkspaceTimelineItem] = Field(default_factory=list)
    confidence_evolution: list[ConfidencePoint] = Field(default_factory=list)
    hypotheses: list[WorkspaceHypothesis] = Field(default_factory=list)
    resolution: list[WorkspaceResolutionStage] = Field(default_factory=list)
    verification: list[WorkspaceVerificationItem] = Field(default_factory=list)
    knowledge_capture: dict[str, object] | None = None
    playback_events: list[dict[str, object]] = Field(default_factory=list)
