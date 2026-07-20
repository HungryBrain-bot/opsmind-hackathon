from __future__ import annotations

import logging
from typing import Callable

from app.core.settings import Settings
from app.investigation.contradictions import ContradictionDetector
from app.investigation.evidence_summary import EvidenceSummaryService
from app.investigation.openai_reasoning_client import (
    OpenAIResponsesReasoningClient,
    ReasoningModelClient,
)
from app.investigation.reasoning_prompt import build_reasoning_prompt
from app.observability.telemetry import ModelUsage, Timer
from app.schemas.evidence import Evidence
from app.schemas.hypothesis import Hypothesis
from app.schemas.reasoning import (
    EvidenceAssessment,
    EvidenceDisposition,
    EvidenceGap,
    ReasoningDecision,
    ReasoningResult,
)

logger = logging.getLogger(__name__)
ReasoningClientFactory = Callable[[str], ReasoningModelClient]


class EvidenceReasoner:
    """Hybrid reasoner: structured model judgment plus deterministic policy validation."""

    def __init__(
        self,
        settings: Settings,
        available_tools: list[str],
        *,
        client_factory: ReasoningClientFactory | None = None,
    ) -> None:
        self.settings = settings
        self.available_tools = sorted(set(available_tools))
        self._client_factory = client_factory or OpenAIResponsesReasoningClient
        self._contradictions = ContradictionDetector()
        self._summary = EvidenceSummaryService()
        self.last_usage = ModelUsage(prompt_version=settings.reasoning_prompt_version)

    async def evaluate(
        self,
        *,
        round_number: int,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
        deterministic_sufficient: bool,
    ) -> ReasoningResult:
        provider = self.settings.reasoning_provider.strip().lower()
        if provider == "openai" and self.settings.openai_api_key:
            try:
                return await self._openai(
                    round_number, hypotheses, evidence, deterministic_sufficient
                )
            except Exception as exc:
                if not self.settings.reasoning_fallback_to_fixture:
                    raise
                logger.warning("reasoning.fallback error=%s", exc)
        return self._fixture(round_number, hypotheses, evidence, deterministic_sufficient)

    async def _openai(
        self,
        round_number: int,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
        deterministic_sufficient: bool,
    ) -> ReasoningResult:
        prompt = build_reasoning_prompt(
            version=self.settings.reasoning_prompt_version,
            round_number=round_number,
            hypotheses=hypotheses,
            evidence=evidence,
            available_tools=self.available_tools,
        )
        timer = Timer.start()
        client = self._client_factory(self.settings.openai_api_key or "")
        response = await client.evaluate(
            model=self.settings.openai_model,
            system_prompt=prompt.system,
            user_prompt=prompt.user,
        )
        self._validate(response.result, hypotheses, evidence)
        # Deterministic policy owns the final stop decision.
        response.result.decision.evidence_sufficient = deterministic_sufficient
        response.result.decision.continue_investigation = not deterministic_sufficient
        self.last_usage = ModelUsage(
            provider="openai",
            model=self.settings.openai_model,
            prompt_version=prompt.version,
            request_count=1,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.input_tokens + response.output_tokens,
            estimated_cost_usd=self._estimate_cost(response.input_tokens, response.output_tokens),
            latency_ms=timer.elapsed_ms(),
            validation_attempts=1,
        )
        return response.result

    def _fixture(
        self,
        round_number: int,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
        deterministic_sufficient: bool,
    ) -> ReasoningResult:
        assessments: list[EvidenceAssessment] = []
        for item in evidence:
            if item.supports:
                disposition = EvidenceDisposition.SUPPORTING
                hypothesis_ids = item.supports
            elif item.contradicts:
                disposition = EvidenceDisposition.CONTRADICTING
                hypothesis_ids = item.contradicts
            else:
                disposition = EvidenceDisposition.NEUTRAL
                hypothesis_ids = []
            assessments.append(
                EvidenceAssessment(
                    evidence_id=item.id,
                    hypothesis_ids=hypothesis_ids,
                    disposition=disposition,
                    quality=item.reliability.value,
                    observation=item.content,
                    rationale=f"Classification derived from normalized {item.source} evidence relationships.",
                )
            )
        contradictions = self._contradictions.detect(hypotheses, evidence)
        findings = self._summary.build(hypotheses, evidence)
        leading = max(hypotheses, key=lambda item: item.confidence)
        gaps: list[EvidenceGap] = []
        if not deterministic_sufficient:
            gaps.append(
                EvidenceGap(
                    description="Additional independent corroboration is required",
                    reason="Deterministic sufficiency rules have not all passed.",
                    priority="high",
                    expected_impact="May confirm or disprove the leading hypothesis and enable a defensible stop decision.",
                )
            )
        decision = ReasoningDecision(
            round_number=round_number,
            leading_hypothesis_id=leading.id,
            evidence_sufficient=deterministic_sufficient,
            continue_investigation=not deterministic_sufficient,
            summary=(
                "Evidence satisfies the deterministic stopping policy."
                if deterministic_sufficient
                else "Evidence remains insufficient under the deterministic stopping policy."
            ),
            next_actions=[] if deterministic_sufficient else [gap.description for gap in gaps],
        )
        self.last_usage = ModelUsage(
            provider="fixture",
            prompt_version=self.settings.reasoning_prompt_version,
            request_count=0,
            validation_attempts=1,
        )
        return ReasoningResult(
            assessments=assessments,
            findings=findings,
            contradictions=contradictions,
            gaps=gaps,
            decision=decision,
        )

    @staticmethod
    def _validate(
        result: ReasoningResult, hypotheses: list[Hypothesis], evidence: list[Evidence]
    ) -> None:
        hypothesis_ids = {item.id for item in hypotheses}
        evidence_ids = {item.id for item in evidence}
        if result.decision.leading_hypothesis_id not in hypothesis_ids:
            raise ValueError("Reasoner selected an unknown leading hypothesis")
        referenced = {
            evidence_id for finding in result.findings for evidence_id in finding.evidence_ids
        }
        referenced.update(item.evidence_id for item in result.assessments)
        unknown = referenced - evidence_ids
        if unknown:
            raise ValueError(f"Reasoner referenced unknown evidence IDs: {sorted(unknown)}")

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return round(
            input_tokens / 1_000_000 * self.settings.model_input_cost_per_million
            + output_tokens / 1_000_000 * self.settings.model_output_cost_per_million,
            6,
        )
