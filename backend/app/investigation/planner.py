from __future__ import annotations

from abc import ABC, abstractmethod
import logging

from pydantic import ValidationError

from app.core.settings import Settings
from app.investigation.fixtures import heavy_forwarder_hypotheses
from app.observability.telemetry import ModelUsage, Timer
from app.schemas.hypothesis import HypothesisStatus
from app.schemas.investigation import InvestigationRequest
from app.schemas.plan import EvidenceRequirement, InvestigationPlan

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the planning layer of OpsMind, an enterprise investigation engine.
Create a bounded, evidence-first investigation plan. Do not produce a verdict. Do not recommend
write actions. Use only the available read-only tool names. Hypotheses must be mutually useful,
prioritized through their confidence values, and falsifiable. Every evidence requirement must say
which hypothesis it helps test. Return only data conforming to the supplied schema."""


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
    """Structured-output planner with strict validation and fixture fallback."""

    def __init__(self, settings: Settings, available_tools: list[str]) -> None:
        self.settings = settings
        self.available_tools = available_tools
        self.last_usage = ModelUsage(
            provider="openai",
            model=settings.openai_model,
            prompt_version=settings.planner_prompt_version,
        )

    async def create_plan(self, request: InvestigationRequest) -> InvestigationPlan:
        if not self.settings.openai_api_key:
            return await self._fallback(request, "OPENAI_API_KEY is not configured", 0)

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        timer = Timer.start()
        last_error: Exception | None = None
        attempts = max(1, self.settings.planner_max_validation_attempts)

        for attempt in range(1, attempts + 1):
            try:
                response = await client.responses.parse(
                    model=self.settings.openai_model,
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": (
                                f"Prompt version: {self.settings.planner_prompt_version}\n"
                                f"Problem: {request.problem}\n"
                                f"Environment: {request.environment}\n"
                                f"Priority: {request.priority}\n"
                                f"Available read-only tools: {', '.join(self.available_tools)}\n"
                                "Use IDs H-001 onward and R-001 onward."
                            ),
                        },
                    ],
                    text_format=InvestigationPlan,
                )
                plan = response.output_parsed
                if plan is None:
                    raise ValueError("Model returned no parsed investigation plan")
                self._validate_tools(plan)
                usage = getattr(response, "usage", None)
                input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
                output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
                self.last_usage = ModelUsage(
                    provider="openai",
                    model=self.settings.openai_model,
                    prompt_version=self.settings.planner_prompt_version,
                    request_count=1,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                    estimated_cost_usd=self._estimate_cost(input_tokens, output_tokens),
                    latency_ms=timer.elapsed_ms(),
                    validation_attempts=attempt,
                )
                return plan
            except (ValidationError, ValueError, Exception) as exc:
                # OpenAI SDK/API exceptions are intentionally captured here so the MVP can degrade safely.
                last_error = exc
                logger.warning("planner.validation_or_api_failure attempt=%s error=%s", attempt, exc)

        return await self._fallback(request, str(last_error or "Planner failed"), attempts, timer)

    def _validate_tools(self, plan: InvestigationPlan) -> None:
        unknown = {
            item.preferred_tool
            for item in plan.evidence_requirements
            if item.preferred_tool not in self.available_tools
        }
        if unknown:
            raise ValueError(f"Planner selected unavailable tools: {sorted(unknown)}")

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
    if settings.planner_provider.lower() == "openai":
        return OpenAIInvestigationPlanner(settings, available_tools)
    return FixtureInvestigationPlanner()


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
