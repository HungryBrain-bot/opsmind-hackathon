from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.explainability import InvestigationDecisionTrace
from app.schemas.knowledge import KnowledgePattern
from app.schemas.lifecycle import InvestigationRound
from app.schemas.resolution import ResolutionPlan


class InvestigationReportEvidence(BaseModel):
    id: str
    title: str
    source: str
    category: str
    reliability: str
    content: str


class InvestigationReport(BaseModel):
    report_version: str = "1.0"
    generated_at: datetime
    investigation_id: str
    problem: str
    environment: str | None = None
    priority: str | None = None
    status: str
    verdict: str | None = None
    confidence: float = 0.0
    evidence_strength: float = 0.0
    investigation_completeness: float = 0.0
    stop_reason: str
    decision_trace: InvestigationDecisionTrace
    evidence: list[InvestigationReportEvidence] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    rounds: list[InvestigationRound] = Field(default_factory=list)
    confidence_history: list[float] = Field(default_factory=list)
    resolution_plan: ResolutionPlan | None = None
    knowledge_pattern: KnowledgePattern | None = None
