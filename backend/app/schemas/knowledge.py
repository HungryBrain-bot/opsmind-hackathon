from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgePattern(BaseModel):
    id: str
    created_at: datetime
    source_investigation_id: str
    title: str
    symptoms: list[str] = Field(default_factory=list)
    root_cause: str
    resolution_summary: list[str] = Field(default_factory=list)
    verification_summary: list[str] = Field(default_factory=list)
    evidence_categories: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    reusable: bool = True
