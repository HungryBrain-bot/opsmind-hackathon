import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _completed_investigation():
    created = client.post(
        "/api/v1/investigations",
        json={
            "problem": "Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?",
            "environment": "Production",
            "priority": "High",
        },
    )
    assert created.status_code == 202
    investigation_id = created.json()["investigation_id"]
    for _ in range(60):
        result = client.get(f"/api/v1/investigations/{investigation_id}").json()
        if result["status"] in {"completed", "inconclusive", "failed"}:
            return result
        time.sleep(0.05)
    raise AssertionError("Investigation did not finish")


def test_timeline_and_notebook():
    result = _completed_investigation()
    investigation_id = result["investigation_id"]
    timeline = client.get(f"/api/v1/investigations/{investigation_id}/timeline")
    notebook = client.get(f"/api/v1/investigations/{investigation_id}/notebook")
    assert timeline.status_code == 200
    assert notebook.status_code == 200
    assert timeline.json()
    assert notebook.json()["entries"]
    assert any(item["type"] == "verdict" for item in notebook.json()["entries"])
