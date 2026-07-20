from app.core.settings import Settings
from app.investigation.engine import InvestigationEngine
from app.investigation.hypothesis_manager import HypothesisManager
from app.investigation.store import InvestigationStore
from app.schemas.hypothesis import Hypothesis, HypothesisStatus
from app.schemas.investigation import InvestigationRequest, InvestigationStatus
from app.schemas.lifecycle import InvestigationLifecyclePhase, RoundDecision


async def test_step5_builds_complete_resolution_lifecycle() -> None:
    store = InvestigationStore()
    engine = InvestigationEngine(
        Settings(demo_stage_delay_seconds=0, sufficiency_threshold=0.8), store
    )
    created = await engine.create(
        InvestigationRequest(
            problem="Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?"
        )
    )

    await engine.run(created.investigation_id)
    result = await store.get(created.investigation_id)
    events = await store.events_from(created.investigation_id, 0)

    assert result.status == InvestigationStatus.COMPLETED
    assert result.lifecycle_phase == InvestigationLifecyclePhase.COMPLETE
    assert len(result.rounds) == 2
    assert result.rounds[-1].decision == RoundDecision.RESOLVE
    assert result.rounds[-1].completed_at is not None
    assert result.confidence_history[-1] >= 0.8
    assert result.resolution_plan is not None
    assert result.resolution_plan.human_approval_required is True
    assert {action.stage.value for action in result.resolution_plan.actions} >= {
        "containment",
        "recovery",
        "verification",
        "prevention",
    }
    assert len(result.resolution_plan.verification_criteria) >= 3
    assert result.knowledge_pattern is not None
    assert result.knowledge_pattern.source_investigation_id == result.investigation_id
    assert result.knowledge_pattern.reusable is True
    event_types = {event.type.value for event in events}
    assert "round_completed" in event_types
    assert "resolution_generated" in event_types
    assert "verification_planned" in event_types
    assert "knowledge_captured" in event_types


def test_hypothesis_manager_rejects_contradicted_low_confidence_hypothesis() -> None:
    hypothesis = Hypothesis(
        id="H-001",
        title="Disk pressure",
        rationale="Disk may be full",
        confidence=0.1,
        contradicting_evidence_ids=["E-001"],
    )
    evolution = HypothesisManager().evolve(
        [hypothesis],
        round_number=2,
        previous={"H-001": (0.4, HypothesisStatus.ACTIVE)},
    )

    assert hypothesis.status == HypothesisStatus.REJECTED
    assert hypothesis.rejection_reason
    assert evolution[0].current_status == "rejected"
    assert evolution[0].current_confidence == 0.1
