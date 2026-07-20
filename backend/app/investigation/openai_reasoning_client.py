from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.schemas.reasoning import ReasoningResult


@dataclass(frozen=True, slots=True)
class ReasoningModelResponse:
    result: ReasoningResult
    input_tokens: int = 0
    output_tokens: int = 0


class ReasoningModelClient(Protocol):
    async def evaluate(
        self, *, model: str, system_prompt: str, user_prompt: str
    ) -> ReasoningModelResponse: ...


class OpenAIResponsesReasoningClient:
    def __init__(self, api_key: str) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=api_key)

    async def evaluate(
        self, *, model: str, system_prompt: str, user_prompt: str
    ) -> ReasoningModelResponse:
        response = await self._client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=ReasoningResult,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("Model returned no parsed reasoning result")
        usage = getattr(response, "usage", None)
        return ReasoningModelResponse(
            result=parsed,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
        )
