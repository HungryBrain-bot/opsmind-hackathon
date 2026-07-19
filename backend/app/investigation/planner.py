from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from typing import Callable

from app.core.settings import Settings
from app.investigation.fixtures import heavy_forwarder_hypotheses
from app.investigation.openai_planner_client import (
    OpenAIResponsesPlannerClient,
    PlannerModelClient,
)
from app.investigation.planner_prompt import build_planner_prompt
from app.observability.telemetry import ModelUsage, Timer
from app.schemas.hypothesis import HypothesisStatus
from app.schemas.investigation import InvestigationRequest
from app.schemas.plan import EvidenceRequirement, InvestigationPlan

logger = logging.getLogger(__name__)

PlannerClientFactory = Callable[[str], PlannerModelClient]


class InvestigationPlanner(ABC):
    last_usage: ModelUsage

    @abstractmethod
    async def create_plan(self, request: InvestigationRequest) -> InvestigationPlan:
        raise NotImplementedError


class FixtureInvestigationPlanner(InvestigationPlanner):
    def __init__(self, *, fallback_used: bool = False, validation_attempts: int = 1) -> None:
        self.last_usage = ModelUsage(
            fallback_used=fallback_used,
            validation_attempts=validation_attempts,
        )

    async def create_plan(self, request: InvestigationRequest) -> InvestigationPlan:
        hypotheses = heavy_forwarder_hypotheses()
        initial_confidence = {"H-001": 0.41, "H-002": 0.29, "H-003": 0.24, "H-004": 0.16}
        planned_hypotheses = []
        for hypothesis in hypotheses:
            item = hypothesis.model_copy(deep=True)
            item.confidence = initial_confidence[hypothesis.id]
            item.status = HypothesisStatus.ACTIVE
            item.supporting_evidence_ids = []
            item.contradicting_evidence_ids = []
            planned_hypotheses.append(item)

        return InvestigationPlan(
            goal=f"Determine a defensible root cause for: {request.problem}",
            hypotheses=planned_hypotheses,
            evidence_requirements=_golden_path_requirements(),
            stop_confidence=0.80,
            minimum_categories=2,
            maximum_rounds=3,
        )


class OpenAIInvestigationPlanner(InvestigationPlanner):
    """Structured-output planner with validation, bounded retries and fixture fallback."""

    def __init__(
        self,
        settings: Settings,
        available_tools: list[str],
        *,
        client_factory: PlannerClientFactory | None = None,
    ) -> None:
        self.settings = settings
        self.available_tools = sorted(set(available_tools))
        self._client_factory = client_factory or OpenAIResponsesPlannerClient
        self.last_usage = ModelUsage(
            provider="openai",
            model=settings.openai_model,
            prompt_version=settings.planner_prompt_version,
        )

    async def create_plan(self, request: InvestigationRequest) -> InvestigationPlan:
        prompt = build_planner_prompt(
            version=self.settings.planner_prompt_version,
            request=request,
            available_tools=self.available_tools,
        )
        if not self.settings.openai_api_key:
            return await self._fallback(request, "OPENAI_API_KEY is not configured", 0)

        client = self._client_factory(self.settings.openai_api_key)
        timer = Timer.start()
        last_error: Exception | None = None
        attempts = max(1, self.settings.planner_max_validation_attempts)

        for attempt in range(1, attempts + 1):
            try:
                response = await client.create_plan(
                    model=self.settings.openai_model,
                    system_prompt=prompt.system,
                    user_prompt=prompt.user,
                )
                self._validate_plan(response.plan)
                self.last_usage = ModelUsage(
                    provider="openai",
                    model=self.settings.openai_model,
                    prompt_version=prompt.version,
                    request_count=attempt,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    total_tokens=response.input_tokens + response.output_tokens,
                    estimated_cost_usd=self._estimate_cost(
                        response.input_tokens, response.output_tokens
                    ),
                    latency_ms=timer.elapsed_ms(),
                    validation_attempts=attempt,
                )
                return response.plan
            except Exception as exc:
                # The adapter contains the vendor boundary. Any API, parsing or semantic
                # validation failure is safe to retry within the configured bound.
                last_error = exc
                logger.warning(
                    "planner.validation_or_api_failure attempt=%s error=%s", attempt, exc
                )

        return await self._fallback(request, str(last_error or "Planner failed"), attempts, timer)

    def _validate_plan(self, plan: InvestigationPlan) -> None:
        unknown_tools = {
            item.preferred_tool
            for item in plan.evidence_requirements
            if item.preferred_tool not in self.available_tools
        }
        if unknown_tools:
            raise ValueError(f"Planner selected unavailable tools: {sorted(unknown_tools)}")

        hypothesis_ids = [item.id for item in plan.hypotheses]
        expected_hypothesis_ids = [f"H-{index:03d}" for index in range(1, len(hypothesis_ids) + 1)]
        if hypothesis_ids != expected_hypothesis_ids:
            raise ValueError(
                "Hypothesis IDs must be sequential and ordered from H-001; "
                f"received {hypothesis_ids}"
            )

        requirement_ids = [item.id for item in plan.evidence_requirements]
        expected_requirement_ids = [
            f"R-{index:03d}" for index in range(1, len(requirement_ids) + 1)
        ]
        if requirement_ids != expected_requirement_ids:
            raise ValueError(
                "Evidence requirement IDs must be sequential and ordered from R-001; "
                f"received {requirement_ids}"
            )

        untested = set(hypothesis_ids) - {
            hypothesis_id
            for requirement in plan.evidence_requirements
            for hypothesis_id in requirement.hypothesis_ids
        }
        if untested:
            raise ValueError(f"Every hypothesis must have planned evidence: {sorted(untested)}")

        if plan.maximum_rounds > self.settings.max_investigation_rounds:
            raise ValueError(
                "Planner maximum_rounds exceeds the runtime safety limit: "
                f"{plan.maximum_rounds} > {self.settings.max_investigation_rounds}"
            )

    async def _fallback(
        self, request: InvestigationRequest, reason: str, attempts: int, timer: Timer | None = None
    ) -> InvestigationPlan:
        if not self.settings.planner_fallback_to_fixture:
            raise RuntimeError(f"Model-backed planner failed: {reason}")
        logger.warning("planner.fallback reason=%s", reason)
        fixture = FixtureInvestigationPlanner(
            fallback_used=True,
            validation_attempts=max(1, attempts),
        )
        plan = await fixture.create_plan(request)
        self.last_usage = ModelUsage(
            provider="openai",
            model=self.settings.openai_model,
            prompt_version=self.settings.planner_prompt_version,
            request_count=attempts,
            latency_ms=timer.elapsed_ms() if timer else 0,
            fallback_used=True,
            validation_attempts=max(1, attempts),
        )
        return plan

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return round(
            input_tokens / 1_000_000 * self.settings.model_input_cost_per_million
            + output_tokens / 1_000_000 * self.settings.model_output_cost_per_million,
            6,
        )


def create_planner(settings: Settings, available_tools: list[str]) -> InvestigationPlanner:
    provider = settings.planner_provider.strip().lower()
    if provider == "openai":
        return OpenAIInvestigationPlanner(settings, available_tools)
    if provider == "fixture":
        return FixtureInvestigationPlanner()
    raise ValueError(
        f"Unsupported planner provider {settings.planner_provider!r}. "
        "Expected 'fixture' or 'openai'."
    )

def _golden_path_requirements() -> list[EvidenceRequirement]:
    return [
        EvidenceRequirement(
            id="R-001",
            description="Confirm current forwarding and TLS symptoms",
            category="operational",
            preferred_tool="query_splunk_internal_logs",
            hypothesis_ids=["H-001"],
            priority=1,
        ),
        EvidenceRequirement(
            id="R-002",
            description="Validate the Heavy Forwarder client certificate",
            category="configuration",
            preferred_tool="get_certificate_status",
            hypothesis_ids=["H-001"],
            priority=1,
        ),
        EvidenceRequirement(
            id="R-003",
            description="Search for matching prior incidents",
            category="historical",
            preferred_tool="search_historical_incidents",
            hypothesis_ids=["H-001"],
            priority=2,
        ),
        EvidenceRequirement(
            id="R-004",
            description="Validate the configured indexer destination",
            category="configuration",
            preferred_tool="get_component_relationships",
            hypothesis_ids=["H-002"],
            priority=2,
        ),
        EvidenceRequirement(
            id="R-005",
            description="Validate indexer reachability",
            category="operational",
            preferred_tool="get_heavy_forwarder_health",
            hypothesis_ids=["H-003"],
            priority=2,
        ),
        EvidenceRequirement(
            id="R-006",
            description="Check local resources and forwarding queues",
            category="operational",
            preferred_tool="get_heavy_forwarder_health",
            hypothesis_ids=["H-004"],
            priority=2,
        ),
    ]
