from app.investigation.engine import InvestigationEngine
from app.investigation.store import InvestigationStore
from app.core.settings import Settings
from app.schemas.investigation import InvestigationRequest
from app.storage.file_repository import FileInvestigationRepository


async def _completed_result():
    store = InvestigationStore()
    engine = InvestigationEngine(Settings(demo_stage_delay_seconds=0), store)
    created = await engine.create(
        InvestigationRequest(
            problem="Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?"
        )
    )
    await engine.run(created.investigation_id)
    return await store.get(created.investigation_id)


async def test_file_repository_save_load_search_and_delete(tmp_path) -> None:
    result = await _completed_result()
    repository = FileInvestigationRepository(tmp_path / "investigations")

    repository.save(result, "# Stored report")

    loaded = repository.get(result.investigation_id)
    assert loaded.verdict == result.verdict
    assert repository.get_report(result.investigation_id) == "# Stored report"
    assert repository.exists(result.investigation_id)
    assert repository.list(query="certificate")[0].investigation_id == result.investigation_id
    assert repository.list(environment="Production")
    assert repository.list(status="completed")
    assert repository.list(priority="High")
    assert repository.list(root_cause="expired")
    assert repository.list(query="not-present") == []

    repository.delete(result.investigation_id)
    assert not repository.exists(result.investigation_id)
