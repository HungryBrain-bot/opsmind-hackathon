from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from pydantic import BaseModel, Field


class ModelUsage(BaseModel):
    provider: str = "fixture"
    model: str = "deterministic"
    prompt_version: str = "planner-v1"
    request_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)
    latency_ms: int = 0
    fallback_used: bool = False
    validation_attempts: int = 1


@dataclass(slots=True)
class Timer:
    started: float

    @classmethod
    def start(cls) -> "Timer":
        return cls(started=perf_counter())

    def elapsed_ms(self) -> int:
        return round((perf_counter() - self.started) * 1000)
