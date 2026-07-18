from app.core.settings import Settings
from app.investigation.engine import InvestigationEngine
from app.investigation.store import InvestigationStore
from app.schemas.investigation import InvestigationRequest


async def _run_golden_path():
    store = InvestigationStore()
    engine = InvestigationEngine(
        Settings(demo_stage_delay_seconds=0, sufficiency_threshold=0.8),
        store,
    )
    created = await engine.create(
        InvestigationRequest(
            problem="Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?"
        )
    )
    await engine.run(created.investigation_id)
    return await store.get(created.investigation_id)


async def test_confidence_history_is_ordered_and_bounded() -> None:
    result = await _run_golden_path()

    evidence_ids = {item.id for item in result.evidence}
    hypothesis_ids = {item.id for item in result.hypotheses}

    for hypothesis in result.hypotheses:
        assert hypothesis.confidence_history
        assert [item.sequence for item in hypothesis.confidence_history] == list(
            range(1, len(hypothesis.confidence_history) + 1)
        )
        assert all(item.hypothesis_id in hypothesis_ids for item in hypothesis.confidence_history)
        assert all(0 <= item.previous_confidence <= 1 for item in hypothesis.confidence_history)
        assert all(0 <= item.new_confidence <= 1 for item in hypothesis.confidence_history)
        for change in hypothesis.confidence_history[1:]:
            assert set(change.evidence_ids).issubset(evidence_ids)
            assert change.reason


async def test_tls_hypothesis_finishes_as_leader_with_increases() -> None:
    result = await _run_golden_path()
    leader = max(result.hypotheses, key=lambda item: item.confidence)

    assert leader.id == "H-001"
    assert leader.confidence >= 0.9
    assert any(
        change.direction.value == "increased"
        for change in leader.confidence_history
    )


async def test_rejected_hypotheses_have_explanations_when_present() -> None:
    result = await _run_golden_path()
    rejected = [item for item in result.hypotheses if item.status.value == "rejected"]

    for hypothesis in rejected:
        assert hypothesis.rejection_reason
        assert hypothesis.contradicting_evidence_ids
