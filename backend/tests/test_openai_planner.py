from __future__ import annotations

from collections import deque

import pytest

from app.core.settings import Settings
from app.investigation.openai_planner_client import PlannerModelResponse
from app.investigation.planner import FixtureInvestigationPlanner, OpenAIInvestigationPlanner
from app.investigation.planner_prompt import build_planner_prompt
from app.schemas.investigation import InvestigationRequest


REQUEST = InvestigationRequest(
    problem="Why is HF-PROD-02 not forwarding logs to the indexer cluster?"
)
TOOLS = [
    "query_splunk_internal_logs",
    "get_certificate_status",
    "search_historical_incidents",
    "get_component_relationships",
    "get_heavy_forwarder_health",
]


class FakePlannerClient:
    def __init__(self, responses: deque[PlannerModelResponse | Exception]) -> None:
        self.responses = responses
        self.calls = 0

    async def create_plan(
        self, *, model: str, system_prompt: str, user_prompt: str
    ) -> PlannerModelResponse:
        self.calls += 1
        response = self.responses.popleft()
        if isinstance(response, Exception):
            raise response
        return response


async def _fixture_plan():
    return await FixtureInvestigationPlanner().create_plan(REQUEST)


def _settings(**overrides: object) -> Settings:
    values = {
        "planner_provider": "openai",
        "openai_api_key": "test-key",
        "planner_fallback_to_fixture": True,
        "planner_max_validation_attempts": 2,
        "demo_stage_delay_seconds": 0,
    }
    values.update(overrides)
    return Settings(**values)


async def test_openai_planner_returns_validated_structured_plan_and_usage() -> None:
    plan = await _fixture_plan()
    client = FakePlannerClient(deque([PlannerModelResponse(plan, 120, 80)]))
    planner = OpenAIInvestigationPlanner(_settings(), TOOLS, client_factory=lambda _: client)

    result = await planner.create_plan(REQUEST)

    assert result == plan
    assert client.calls == 1
    assert planner.last_usage.provider == "openai"
    assert planner.last_usage.request_count == 1
    assert planner.last_usage.total_tokens == 200
    assert planner.last_usage.fallback_used is False


async def test_openai_planner_retries_semantically_invalid_tool_then_succeeds() -> None:
    invalid = await _fixture_plan()
    invalid.evidence_requirements[0].preferred_tool = "restart_splunk"
    valid = await _fixture_plan()
    client = FakePlannerClient(deque([PlannerModelResponse(invalid), PlannerModelResponse(valid)]))
    planner = OpenAIInvestigationPlanner(_settings(), TOOLS, client_factory=lambda _: client)

    result = await planner.create_plan(REQUEST)

    assert result == valid
    assert client.calls == 2
    assert planner.last_usage.validation_attempts == 2
    assert planner.last_usage.request_count == 2


async def test_openai_planner_falls_back_after_bounded_failures() -> None:
    client = FakePlannerClient(deque([RuntimeError("timeout"), RuntimeError("bad JSON")]))
    planner = OpenAIInvestigationPlanner(_settings(), TOOLS, client_factory=lambda _: client)

    plan = await planner.create_plan(REQUEST)

    assert plan.hypotheses
    assert client.calls == 2
    assert planner.last_usage.fallback_used is True
    assert planner.last_usage.request_count == 2


async def test_openai_planner_raises_when_fallback_is_disabled() -> None:
    client = FakePlannerClient(deque([RuntimeError("API unavailable")]))
    planner = OpenAIInvestigationPlanner(
        _settings(
            planner_fallback_to_fixture=False,
            planner_max_validation_attempts=1,
        ),
        TOOLS,
        client_factory=lambda _: client,
    )

    with pytest.raises(RuntimeError, match="Model-backed planner failed"):
        await planner.create_plan(REQUEST)


def test_prompt_is_versioned_and_contains_runtime_boundaries() -> None:
    prompt = build_planner_prompt(version="planner-v1", request=REQUEST, available_tools=TOOLS)

    assert prompt.version == "planner-v1"
    assert "Do not produce a verdict" in prompt.system
    assert "Available read-only tools" in prompt.user
    assert "HF-PROD-02" in prompt.user


def test_unknown_prompt_version_is_rejected_before_api_call() -> None:
    with pytest.raises(ValueError, match="Unsupported planner prompt version"):
        build_planner_prompt(version="planner-v999", request=REQUEST, available_tools=TOOLS)
