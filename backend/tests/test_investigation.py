from app.core.settings import Settings
from app.investigation.engine import InvestigationEngine
from app.investigation.store import InvestigationStore
from app.schemas.investigation import InvestigationRequest, InvestigationStatus


async def test_event_driven_golden_path_completes_with_replayable_events() -> None:
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

    result = await store.get(created.investigation_id)
    events = await store.events_from(created.investigation_id, 0)

    assert result.status == InvestigationStatus.COMPLETED
    assert result.stop_reason.sufficient is True
    # The adaptive loop stops after round 2 once the stop rules are satisfied.
    assert result.round_number == 2
    assert len(result.evidence) == 4
    assert result.hypotheses[0].confidence >= 0.9
    assert result.investigation_goal
    assert result.tools_used == [
        "query_splunk_internal_logs",
        "get_certificate_status",
        "search_historical_incidents",
        "get_component_relationships",
    ]
    assert any(event.type.value == "tool_selected" for event in events)
    assert any(event.type.value == "tool_completed" for event in events)
    assert any(event.type.value == "evidence_collected" for event in events)
    assert events[-1].type.value == "investigation_completed"
    assert [event.sequence for event in events] == list(range(1, len(events) + 1))
