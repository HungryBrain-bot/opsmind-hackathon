from fastapi.testclient import TestClient

from app.api import investigations as investigations_api
from app.core.settings import Settings
from app.investigation.engine import InvestigationEngine
from app.investigation.reporting import InvestigationReportBuilder
from app.investigation.store import InvestigationStore
from app.main import app
from app.schemas.investigation import InvestigationRequest
from app.storage.file_repository import FileInvestigationRepository


async def test_history_api_lists_opens_downloads_and_deletes(tmp_path, monkeypatch) -> None:
    repository = FileInvestigationRepository(tmp_path / "history")
    store = InvestigationStore()
    engine = InvestigationEngine(Settings(demo_stage_delay_seconds=0), store)
    created = await engine.create(
        InvestigationRequest(
            problem="Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?"
        )
    )
    await engine.run(created.investigation_id)
    result = await store.get(created.investigation_id)
    repository.save(result, InvestigationReportBuilder().to_markdown(result))
    monkeypatch.setattr(investigations_api, "_repository", repository)

    client = TestClient(app)
    response = client.get("/api/v1/investigations/history", params={"query": "certificate"})
    assert response.status_code == 200
    assert response.json()[0]["investigation_id"] == result.investigation_id

    response = client.get(f"/api/v1/investigations/history/{result.investigation_id}")
    assert response.status_code == 200
    assert response.json()["verdict"] == result.verdict

    response = client.get(f"/api/v1/investigations/history/{result.investigation_id}/report.md")
    assert response.status_code == 200
    assert "OpsMind Investigation Report" in response.text

    response = client.delete(f"/api/v1/investigations/history/{result.investigation_id}")
    assert response.status_code == 204
    assert repository.list() == []
