import asyncio
import logging
from datetime import UTC, datetime
from uuid import uuid4

from app.core.settings import Settings
from app.investigation.confidence import ConfidenceEvolutionService
from app.investigation.evaluator import HypothesisEvaluator
from app.investigation.hypothesis_manager import HypothesisManager
from app.investigation.knowledge_capture import KnowledgeCaptureService
from app.investigation.planner import InvestigationPlanner, create_planner
from app.investigation.resolution import ResolutionIntelligenceService
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
from app.schemas.lifecycle import (
    InvestigationLifecyclePhase,
    InvestigationRound,
    RoundDecision,
)

logger = logging.getLogger(__name__)


class InvestigationEngine:
    """Bounded, multi-round investigation lifecycle with evidence-backed resolution."""

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
        self.hypothesis_manager = HypothesisManager()
        self.sufficiency = EvidenceSufficiencyEngine(settings.sufficiency_threshold)
        self.resolution = ResolutionIntelligenceService()
        self.knowledge_capture = KnowledgeCaptureService()

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
            lifecycle_phase=InvestigationLifecyclePhase.INTAKE,
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
            result.lifecycle_phase = InvestigationLifecyclePhase.INTAKE
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
            result.lifecycle_phase = InvestigationLifecyclePhase.PLANNING
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
                (
                    f"{len(result.hypotheses)} hypotheses and "
                    f"{len(plan.evidence_requirements)} evidence requirements generated"
                ),
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
                investigation_round = await self._start_round(result, round_number, batch)
                for requirement in batch:
                    await self._collect_requirement(result, requirement)

                result.lifecycle_phase = InvestigationLifecyclePhase.REASONING
                previous = {
                    item.id: (item.confidence, item.status) for item in result.hypotheses
                }
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
                        previous[item.id][0],
                        previous_supporting[item.id],
                        previous_contradicting[item.id],
                        evidence_by_id,
                    )
                    for item in result.hypotheses
                ]
                evolution = self.hypothesis_manager.evolve(
                    result.hypotheses, round_number, previous
                )
                result.hypothesis_evolution.extend(evolution)
                result.missing_evidence = [
                    item.description
                    for item in requirements
                    if item.preferred_tool not in result.tools_used
                ]
                leading = max(result.hypotheses, key=lambda item: item.confidence)
                result.confidence_history.append(leading.confidence)
                result.next_action = (
                    "Evaluate evidence sufficiency"
                    if not result.missing_evidence
                    else f"Collect: {result.missing_evidence[0]}"
                )
                await self.store.update(result)
                await self._emit(
                    result,
                    InvestigationEventType.HYPOTHESIS_UPDATED,
                    "Hypotheses evolved after evidence evaluation",
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
                        "evolution": [item.model_dump(mode="json") for item in evolution],
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

                sufficient = stop_reason.sufficient
                decision = (
                    RoundDecision.RESOLVE
                    if sufficient
                    else (
                        RoundDecision.STOP_INCONCLUSIVE
                        if round_number >= len(batches)
                        else RoundDecision.CONTINUE
                    )
                )
                self._complete_round(
                    investigation_round,
                    result,
                    leading.id,
                    leading.confidence,
                    decision,
                    stop_reason.summary,
                )
                await self.store.update(result)
                await self._emit(
                    result,
                    InvestigationEventType.ROUND_COMPLETED,
                    f"Evidence round {round_number} completed",
                    {"round": investigation_round.model_dump(mode="json")},
                )
                if sufficient:
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

    async def _start_round(
        self, result: InvestigationResult, number: int, batch: list
    ) -> InvestigationRound:
        result.round_number = number
        result.status = InvestigationStatus.COLLECTING
        result.lifecycle_phase = InvestigationLifecyclePhase.EVIDENCE_COLLECTION
        result.current_phase = f"Evidence round {number}"
        result.progress_percent = min(85, 25 + number * 20)
        objective = "; ".join(item.description for item in batch)
        investigation_round = InvestigationRound(
            number=number,
            started_at=datetime.now(UTC),
            objective=objective,
            requirement_ids=[item.id for item in batch],
        )
        result.rounds.append(investigation_round)
        self._timeline(result, result.current_phase, f"Round {number} started", objective)
        await self.store.update(result)
        await self._emit(
            result,
            InvestigationEventType.ROUND_STARTED,
            f"Evidence round {number} started",
            {"round": number, "requirements": investigation_round.requirement_ids},
        )
        await self._pause()
        return investigation_round

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
            {
                "environment": result.environment,
                "problem": result.problem,
                "scenario_id": result.scenario_id,
            },
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
            if result.rounds:
                result.rounds[-1].evidence_ids.append(item.id)
            self._timeline(result, result.current_phase, item.title, item.content)
            await self.store.update(result)
            await self._emit(
                result,
                InvestigationEventType.EVIDENCE_COLLECTED,
                item.title,
                {"evidence": item.model_dump(mode="json")},
            )
            await self._pause()

    def _complete_round(
        self,
        investigation_round: InvestigationRound,
        result: InvestigationResult,
        leading_hypothesis_id: str,
        leading_confidence: float,
        decision: RoundDecision,
        reason: str,
    ) -> None:
        investigation_round.completed_at = datetime.now(UTC)
        investigation_round.leading_hypothesis_id = leading_hypothesis_id
        investigation_round.leading_confidence = leading_confidence
        investigation_round.missing_evidence = list(result.missing_evidence)
        investigation_round.decision = decision
        investigation_round.decision_reason = reason

    async def _finalize(self, result: InvestigationResult, sufficient: bool) -> None:
        result.status = InvestigationStatus.EVALUATING
        result.current_phase = "Final evaluation"
        result.progress_percent = 90
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
            await self._build_resolution_lifecycle(result, leading)
            result.status = InvestigationStatus.COMPLETED
            result.lifecycle_phase = InvestigationLifecyclePhase.COMPLETE
            result.current_phase = "Resolution ready"
            result.next_action = "Human review, approved remediation and verification"
            message = "Evidence-backed verdict and resolution plan generated"
        else:
            result.status = InvestigationStatus.INCONCLUSIVE
            result.lifecycle_phase = InvestigationLifecyclePhase.INCONCLUSIVE
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

    async def _build_resolution_lifecycle(self, result: InvestigationResult, leading) -> None:
        result.status = InvestigationStatus.RESOLVING
        result.lifecycle_phase = InvestigationLifecyclePhase.RESOLUTION
        result.current_phase = "Resolution intelligence"
        result.progress_percent = 94
        result.resolution_plan = self.resolution.build(result, leading)
        result.recommended_actions = [
            item.action for item in result.resolution_plan.actions
        ]
        self._timeline(
            result,
            result.current_phase,
            "Resolution plan generated",
            (
                f"{len(result.resolution_plan.actions)} evidence-backed actions created "
                "with approval and rollback guidance."
            ),
        )
        await self.store.update(result)
        await self._emit(
            result,
            InvestigationEventType.RESOLUTION_GENERATED,
            "Resolution intelligence generated",
            {"resolution_plan": result.resolution_plan.model_dump(mode="json")},
        )

        result.status = InvestigationStatus.VERIFYING
        result.lifecycle_phase = InvestigationLifecyclePhase.VERIFICATION
        result.current_phase = "Verification planning"
        result.progress_percent = 97
        self._timeline(
            result,
            result.current_phase,
            "Verification criteria defined",
            f"{len(result.resolution_plan.verification_criteria)} recovery checks are pending.",
        )
        await self.store.update(result)
        await self._emit(
            result,
            InvestigationEventType.VERIFICATION_PLANNED,
            "Recovery verification planned",
            {
                "criteria": [
                    item.model_dump(mode="json")
                    for item in result.resolution_plan.verification_criteria
                ]
            },
        )

        result.status = InvestigationStatus.CAPTURING_KNOWLEDGE
        result.lifecycle_phase = InvestigationLifecyclePhase.KNOWLEDGE_CAPTURE
        result.current_phase = "Knowledge capture"
        result.progress_percent = 99
        result.knowledge_pattern = self.knowledge_capture.capture(result)
        self._timeline(
            result,
            result.current_phase,
            "Reusable incident pattern captured",
            result.knowledge_pattern.title,
        )
        await self.store.update(result)
        await self._emit(
            result,
            InvestigationEventType.KNOWLEDGE_CAPTURED,
            "Investigation knowledge captured",
            {"knowledge_pattern": result.knowledge_pattern.model_dump(mode="json")},
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
            TimelineEvent(timestamp=datetime.now(UTC), phase=phase, title=title, detail=detail)
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
            timestamp=datetime.now(UTC),
            phase=result.current_phase,
            message=message,
            data=data,
            snapshot=result,
        )
        await self.store.append_event(event)
