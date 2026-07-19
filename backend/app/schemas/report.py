from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.explainability import InvestigationDecisionTrace

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
