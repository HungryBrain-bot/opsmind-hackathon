from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.hypothesis import Hypothesis


class EvidenceRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    description: str
    category: str
    preferred_tool: str
    hypothesis_ids: list[str] = Field(default_factory=list)
    priority: int = Field(ge=1, le=5, default=3)


class InvestigationPlan(BaseModel):
    """Strict planner output shared by fixture and model-backed planners."""

    model_config = ConfigDict(extra="forbid")

    goal: str = Field(min_length=10)
    hypotheses: list[Hypothesis] = Field(min_length=2, max_length=8)
    evidence_requirements: list[EvidenceRequirement] = Field(min_length=1, max_length=20)
    stop_confidence: float = Field(ge=0.5, le=1.0, default=0.8)
    minimum_categories: int = Field(ge=1, le=5, default=2)
    maximum_rounds: int = Field(ge=1, le=6, default=3)

    @model_validator(mode="after")
    def validate_references(self) -> "InvestigationPlan":
        hypothesis_ids = {item.id for item in self.hypotheses}
        if len(hypothesis_ids) != len(self.hypotheses):
            raise ValueError("Hypothesis IDs must be unique")
        requirement_ids = {item.id for item in self.evidence_requirements}
        if len(requirement_ids) != len(self.evidence_requirements):
            raise ValueError("Evidence requirement IDs must be unique")
        for requirement in self.evidence_requirements:
            unknown = set(requirement.hypothesis_ids) - hypothesis_ids
            if unknown:
                raise ValueError(f"Unknown hypothesis references: {sorted(unknown)}")
        return self
