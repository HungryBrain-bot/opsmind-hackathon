import asyncio
import logging
from datetime import datetime, timezone
from uuid import uuid4

from app.core.settings import Settings
from app.investigation.confidence import ConfidenceEvolutionService
from app.investigation.evaluator import HypothesisEvaluator
from app.investigation.planner import InvestigationPlanner, create_planner
from app.investigation.store import InvestigationStore
from app.investigation.sufficiency import EvidenceSufficiencyEngine
from app.investigation.tools import ToolRegistry
from app.schemas.hypothesis import HypothesisStatus
from app.schemas.investigation import (
    InvestigationEvent,
    InvestigationEventType,
    InvestigationRequest,
    InvestigationResult,
    InvestigationStatus,
    StopReason,
    TimelineEvent,
)

logger = logging.getLogger(__name__)


class InvestigationEngine:
    """Bounded investigation loop driven by a plan, read-only tools and stop rules."""

    def __init__(
        self,
        settings: Settings,
        store: InvestigationStore,
        planner: InvestigationPlanner | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self.settings = settings
        self.store = store
        self.tools = tools or ToolRegistry(settings)
        self.planner = planner or create_planner(settings, self.tools.names())
        self.evaluator = HypothesisEvaluator()
        self.confidence_evolution = ConfidenceEvolutionService()
        self.sufficiency = EvidenceSufficiencyEngine(settings.sufficiency_threshold)

    async def create(self, request: InvestigationRequest) -> InvestigationResult:
        investigation_id = f"INV-{uuid4().hex[:8].upper()}"
        result = InvestigationResult(
            investigation_id=investigation_id,
            problem=request.problem,
            status=InvestigationStatus.NEW,
            environment=request.environment,
            priority=request.priority,
            scenario_id=request.scenario_id,
            current_phase="Queued",
            progress_percent=0,
            missing_evidence=["Investigation plan"],
            next_action="Interpret the submitted operational symptom",
        )
        await self.store.create(result)
        await self._emit(
            result,
            InvestigationEventType.INVESTIGATION_CREATED,
            "Investigation created",
            {"problem": request.problem},
        )
        return result

    async def run(self, investigation_id: str) -> None:
        result = await self.store.get(investigation_id)
        try:
            await self._transition(
                result,
                InvestigationStatus.UNDERSTANDING,
                "Understanding problem",
                8,
                "Problem interpreted",
                "Identified the affected component, symptom and operational impact.",
            )

            request = InvestigationRequest(
                problem=result.problem,
                environment=result.environment,
                priority=result.priority,
                scenario_id=result.scenario_id,
            )
            plan = await self.planner.create_plan(request)
            result.planner_usage = self.planner.last_usage.model_copy(deep=True)
            await self._emit(
                result,
                InvestigationEventType.PLANNER_COMPLETED,
                "Investigation plan generated",
                {"usage": result.planner_usage.model_dump(mode="json")},
            )
            result.investigation_goal = plan.goal
            result.hypotheses = [item.model_copy(deep=True) for item in plan.hypotheses]
            for hypothesis in result.hypotheses:
                self.confidence_evolution.initialize(hypothesis)
            result.planned_evidence = [
                requirement.model_dump(mode="json") for requirement in plan.evidence_requirements
            ]
            result.missing_evidence = [item.description for item in plan.evidence_requirements]
            result.next_action = "Collect the highest-value available evidence"
            await self._transition(
                result,
                InvestigationStatus.PLANNING,
                "Planning investigation",
                20,
                f"{len(result.hypotheses)} hypotheses and {len(plan.evidence_requirements)} evidence requirements generated",
                plan.goal,
                InvestigationEventType.HYPOTHESES_GENERATED,
                {
                    "goal": plan.goal,
                    "hypotheses": [item.model_dump(mode="json") for item in result.hypotheses],
                    "evidence_plan": result.planned_evidence,
                },
            )
            await self._emit(
                result,
                InvestigationEventType.EVIDENCE_PLANNED,
                "Evidence plan created",
                {"requirements": result.planned_evidence},
            )

            requirements = sorted(plan.evidence_requirements, key=lambda item: item.priority)
            max_rounds = min(plan.maximum_rounds, self.settings.max_investigation_rounds)
            batches = self._partition(requirements, max_rounds)
            sufficient = False

            for round_number, batch in enumerate(batches, start=1):
                await self._start_round(result, round_number, batch)
                for requirement in batch:
                    await self._collect_requirement(result, requirement)

                previous = {item.id: item.confidence for item in result.hypotheses}
                previous_supporting = {
                    item.id: set(item.supporting_evidence_ids) for item in result.hypotheses
                }
                previous_contradicting = {
                    item.id: set(item.contradicting_evidence_ids) for item in result.hypotheses
                }
                self.evaluator.evaluate(result.hypotheses, result.evidence)
                evidence_by_id = {item.id: item for item in result.evidence}
                confidence_changes = [
                    self.confidence_evolution.record(
                        item,
                        previous[item.id],
                        previous_supporting[item.id],
                        previous_contradicting[item.id],
                        evidence_by_id,
                    )
                    for item in result.hypotheses
                ]
                result.missing_evidence = [
                    item.description
                    for item in requirements
                    if item.preferred_tool not in result.tools_used
                ]
                leading = max(result.hypotheses, key=lambda item: item.confidence)
                result.next_action = (
                    "Evaluate evidence sufficiency"
                    if not result.missing_evidence
                    else f"Collect: {result.missing_evidence[0]}"
                )
                await self.store.update(result)
                await self._emit(
                    result,
                    InvestigationEventType.HYPOTHESIS_UPDATED,
                    "Hypotheses re-evaluated",
                    {
                        "changes": [
                            {
                                **change.model_dump(mode="json"),
                                "status": next(
                                    item.status.value
                                    for item in result.hypotheses
                                    if item.id == change.hypothesis_id
                                ),
                            }
                            for change in confidence_changes
                        ],
                        "leading_hypothesis": leading.id,
                    },
                )
                await self._pause()

                stop_reason, strength, completeness = self.sufficiency.evaluate(
                    leading, result.evidence
                )
                result.stop_reason = stop_reason
                result.evidence_strength = strength
                result.investigation_completeness = completeness
                await self._emit(
                    result,
                    InvestigationEventType.SUFFICIENCY_EVALUATED,
                    "Evidence sufficiency evaluated",
                    {
                        "round": round_number,
                        "sufficient": stop_reason.sufficient,
                        "summary": stop_reason.summary,
                        "rules_passed": stop_reason.rules_passed,
                        "rules_failed": stop_reason.rules_failed,
                    },
                )
                if stop_reason.sufficient:
                    sufficient = True
                    break

            await self._finalize(result, sufficient)
        except Exception as exc:  # pragma: no cover
            logger.exception("investigation.failed", extra={"investigation_id": investigation_id})
            result.status = InvestigationStatus.FAILED
            result.current_phase = "Failed"
            result.next_action = "Review server logs and retry"
            result.stop_reason = StopReason(sufficient=False, summary=str(exc))
            await self.store.update(result)
            await self._emit(
                result,
                InvestigationEventType.INVESTIGATION_FAILED,
                "Investigation failed",
                {"error": str(exc)},
            )

    async def _start_round(self, result: InvestigationResult, number: int, batch: list) -> None:
        result.round_number = number
        result.status = InvestigationStatus.COLLECTING
        result.current_phase = f"Evidence round {number}"
        result.progress_percent = min(85, 25 + number * 20)
        objective = "; ".join(item.description for item in batch)
        self._timeline(result, result.current_phase, f"Round {number} started", objective)
        await self.store.update(result)
        await self._emit(
            result,
            InvestigationEventType.ROUND_STARTED,
            f"Evidence round {number} started",
            {"round": number, "requirements": [item.id for item in batch]},
        )
        await self._pause()

    async def _collect_requirement(self, result: InvestigationResult, requirement) -> None:
        result.next_action = f"Run read-only tool: {requirement.preferred_tool}"
        await self.store.update(result)
        await self._emit(
            result,
            InvestigationEventType.TOOL_SELECTED,
            f"Selected {requirement.preferred_tool}",
            {
                "requirement_id": requirement.id,
                "tool": requirement.preferred_tool,
                "reason": requirement.description,
            },
        )
        await self._pause()

        items = await self.tools.execute(
            requirement.preferred_tool,
            {"environment": result.environment, "problem": result.problem, "scenario_id": result.scenario_id},
        )
        if requirement.preferred_tool not in result.tools_used:
            result.tools_used.append(requirement.preferred_tool)
        await self._emit(
            result,
            InvestigationEventType.TOOL_COMPLETED,
            f"{requirement.preferred_tool} completed",
            {"tool": requirement.preferred_tool, "evidence_count": len(items)},
        )

        for item in items:
            if any(existing.id == item.id for existing in result.evidence):
                continue
            result.evidence.append(item)
            self._timeline(result, result.current_phase, item.title, item.content)
            await self.store.update(result)
            await self._emit(
                result,
                InvestigationEventType.EVIDENCE_COLLECTED,
                item.title,
                {"evidence": item.model_dump(mode="json")},
            )
            await self._pause()

    async def _finalize(self, result: InvestigationResult, sufficient: bool) -> None:
        result.status = InvestigationStatus.EVALUATING
        result.current_phase = "Final evaluation"
        result.progress_percent = 94
        await self.store.update(result)
        await self._pause()

        leading = max(result.hypotheses, key=lambda item: item.confidence)
        if sufficient:
            leading.status = HypothesisStatus.SUPPORTED
            result.verdict_evidence_ids = sorted(set(leading.supporting_evidence_ids))
            from app.investigation.scenarios import SCENARIOS
            scenario = SCENARIOS.get(result.scenario_id, SCENARIOS["certificate_expiry"])
            result.verdict = scenario.verdict
            result.recommended_actions = scenario.recommended_actions
            result.status = InvestigationStatus.COMPLETED
            result.current_phase = "Verdict ready"
            result.next_action = "Human review and approved remediation"
            message = "Evidence-backed verdict generated"
        else:
            result.status = InvestigationStatus.INCONCLUSIVE
            result.current_phase = "Inconclusive"
            result.next_action = "Request additional evidence or human analysis"
            result.verdict = None
            message = "Investigation ended without sufficient evidence"

        result.progress_percent = 100
        self._timeline(
            result,
            result.current_phase,
            "Investigation stopped",
            result.stop_reason.summary,
        )
        await self.store.update(result)
        if result.verdict:
            await self._emit(
                result,
                InvestigationEventType.VERDICT_GENERATED,
                message,
                {
                    "verdict": result.verdict,
                    "leading_hypothesis": leading.id,
                    "evidence_ids": result.verdict_evidence_ids,
                },
            )
        await self._emit(
            result,
            InvestigationEventType.INVESTIGATION_COMPLETED,
            "Investigation completed",
            {"stop_reason": result.stop_reason.summary, "sufficient": sufficient},
        )

    @staticmethod
    def _partition(items: list, rounds: int) -> list[list]:
        if not items:
            return []
        rounds = max(1, min(rounds, len(items)))
        base, remainder = divmod(len(items), rounds)
        batches = []
        cursor = 0
        for index in range(rounds):
            size = base + (1 if index < remainder else 0)
            batches.append(items[cursor : cursor + size])
            cursor += size
        return batches

    async def _transition(
        self,
        result: InvestigationResult,
        status: InvestigationStatus,
        phase: str,
        progress: int,
        title: str,
        detail: str,
        event_type: InvestigationEventType = InvestigationEventType.PHASE_CHANGED,
        data: dict | None = None,
    ) -> None:
        result.status = status
        result.current_phase = phase
        result.progress_percent = progress
        self._timeline(result, phase, title, detail)
        await self.store.update(result)
        await self._emit(result, event_type, title, data or {"detail": detail})
        await self._pause()

    async def _pause(self) -> None:
        delay = max(0.0, self.settings.demo_stage_delay_seconds)
        if delay:
            await asyncio.sleep(delay)

    @staticmethod
    def _timeline(result: InvestigationResult, phase: str, title: str, detail: str) -> None:
        result.timeline.append(
            TimelineEvent(timestamp=datetime.now(timezone.utc), phase=phase, title=title, detail=detail)
        )

    async def _emit(
        self,
        result: InvestigationResult,
        event_type: InvestigationEventType,
        message: str,
        data: dict,
    ) -> None:
        existing = await self.store.events_from(result.investigation_id, 0)
        event = InvestigationEvent(
            sequence=len(existing) + 1,
            investigation_id=result.investigation_id,
            type=event_type,
            timestamp=datetime.now(timezone.utc),
            phase=result.current_phase,
            message=message,
            data=data,
            snapshot=result,
        )
        await self.store.append_event(event)
