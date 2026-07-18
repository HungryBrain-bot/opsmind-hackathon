from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ConfidenceDirection(StrEnum):
    INITIAL = "initial"
    INCREASED = "increased"
    DECREASED = "decreased"
    UNCHANGED = "unchanged"


class ConfidenceChange(BaseModel):
    sequence: int = Field(ge=1)
    hypothesis_id: str
    evidence_ids: list[str] = Field(default_factory=list)
    previous_confidence: float = Field(ge=0.0, le=1.0)
    new_confidence: float = Field(ge=0.0, le=1.0)
    direction: ConfidenceDirection
    reason: str
    timestamp: datetime
