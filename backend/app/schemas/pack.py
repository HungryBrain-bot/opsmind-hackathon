from pydantic import BaseModel, Field


class InvestigationPack(BaseModel):
    id: str
    name: str
    version: str
    domain: str
    description: str
    supported_problem_types: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    stop_confidence: float = Field(ge=0.5, le=1.0)
    minimum_categories: int = Field(ge=1, le=5)
    maximum_rounds: int = Field(ge=1, le=6)
