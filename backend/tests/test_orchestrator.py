from app.core.settings import Settings
from app.investigation.demo_engine import DemoInvestigationEngine
from app.investigation.orchestrator import InvestigationOrchestrator
from app.investigation.store import InvestigationStore
from app.schemas.investigation import InvestigationRequest, InvestigationStatus


async def test_orchestrator_preserves_demo_engine_behavior() -> None:
    store = InvestigationStore()
    engine = DemoInvestigationEngine(
        Settings(demo_stage_delay_seconds=0, sufficiency_threshold=0.8),
        store,
    )
    orchestrator = InvestigationOrchestrator(engine)

    created = await orchestrator.create(
        InvestigationRequest(
            problem="Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?"
        )
    )
    await orchestrator.run(created.investigation_id)

    result = await store.get(created.investigation_id)
    assert result.status == InvestigationStatus.COMPLETED
    assert result.verdict
    assert result.hypotheses
    assert result.evidence
