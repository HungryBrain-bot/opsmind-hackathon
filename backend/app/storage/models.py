from datetime import datetime

from pydantic import BaseModel

from app.schemas.investigation import InvestigationStatus


class InvestigationHistoryItem(BaseModel):
    investigation_id: str
    problem: str
    status: InvestigationStatus
    environment: str
    priority: str
    root_cause: str | None = None
    confidence: float = 0.0
    evidence_count: int = 0
    created_at: datetime
    updated_at: datetime
