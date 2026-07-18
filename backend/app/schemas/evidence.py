from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class EvidenceCategory(StrEnum):
    OPERATIONAL = "operational"
    CONFIGURATION = "configuration"
    HISTORICAL = "historical"
    RUNBOOK = "runbook"
    RELATIONSHIP = "relationship"


class EvidenceReliability(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Evidence(BaseModel):
    id: str
    title: str
    content: str
    category: EvidenceCategory
    source: str
    observed_at: datetime
    reliability: EvidenceReliability = EvidenceReliability.HIGH
    supports: list[str] = Field(default_factory=list)
    contradicts: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    current: bool = True
