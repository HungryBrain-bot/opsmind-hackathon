from app.core.settings import Settings
from app.investigation.engine import InvestigationEngine
from app.investigation.explainability import DecisionTraceBuilder
from app.investigation.store import InvestigationStore
from app.schemas.investigation import InvestigationRequest


async def _result():
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


async def test_decision_trace_explains_selected_and_alternatives() -> None:
    result = await _result()
    trace = DecisionTraceBuilder().build(result)

    assert trace.selected_hypothesis_id == "H-001"
    assert len(trace.explanations) == len(result.hypotheses)

    selected = next(item for item in trace.explanations if item.selected)
    alternatives = [item for item in trace.explanations if not item.selected]

    assert selected.why_selected
    assert selected.supporting_evidence
    assert all(item.why_not_selected for item in alternatives)


async def test_decision_trace_evidence_references_are_valid() -> None:
    result = await _result()
    trace = DecisionTraceBuilder().build(result)
    evidence_ids = {item.id for item in result.evidence}

    for explanation in trace.explanations:
        referenced = {
            item.id
            for item in explanation.supporting_evidence + explanation.contradicting_evidence
        }
        assert referenced.issubset(evidence_ids)
