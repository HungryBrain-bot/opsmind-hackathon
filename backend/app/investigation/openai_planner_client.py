from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.schemas.plan import InvestigationPlan


@dataclass(frozen=True, slots=True)
class PlannerModelResponse:
    plan: InvestigationPlan
    input_tokens: int = 0
    output_tokens: int = 0


class PlannerModelClient(Protocol):
    async def create_plan(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> PlannerModelResponse: ...


class OpenAIResponsesPlannerClient:
    """Small adapter around the OpenAI Responses API structured-output helper."""

    def __init__(self, api_key: str) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=api_key)

    async def create_plan(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> PlannerModelResponse:
        response = await self._client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=InvestigationPlan,
        )
        plan = response.output_parsed
        if plan is None:
            raise ValueError("Model returned no parsed investigation plan")

        usage = getattr(response, "usage", None)
        return PlannerModelResponse(
            plan=plan,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
        )
