import pytest

from app.core.settings import Settings
from app.investigation.engine import InvestigationEngine
from app.investigation.store import InvestigationStore
from app.schemas.investigation import InvestigationRequest, InvestigationStatus


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("scenario_id", "expected"),
    [
        ("certificate_expiry", "certificate expired"),
        ("firewall_block", "firewall policy blocked"),
        ("outputs_misconfiguration", "invalid indexer destination"),
        ("disk_full", "local storage was exhausted"),
    ],
)
async def test_each_scenario_reaches_distinct_verdict(scenario_id, expected):
    settings = Settings(demo_stage_delay_seconds=0)
    store = InvestigationStore()
    engine = InvestigationEngine(settings, store)
    created = await engine.create(
        InvestigationRequest(
            problem="Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?",
            scenario_id=scenario_id,
        )
    )
    await engine.run(created.investigation_id)
    result = await store.get(created.investigation_id)
    assert result.status == InvestigationStatus.COMPLETED
    assert expected in result.verdict
    assert result.scenario_id == scenario_id
    assert len(result.evidence) >= 4
