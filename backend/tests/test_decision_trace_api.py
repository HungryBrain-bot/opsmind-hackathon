import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_decision_trace_endpoint() -> None:
    response = client.post(
        "/api/v1/investigations",
        json={
            "problem": "Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?",
            "environment": "Production",
            "priority": "High",
        },
    )
    investigation_id = response.json()["investigation_id"]

    for _ in range(80):
        result = client.get(f"/api/v1/investigations/{investigation_id}").json()
        if result["status"] in {"completed", "inconclusive", "failed"}:
            break
        time.sleep(0.05)

    trace = client.get(f"/api/v1/investigations/{investigation_id}/decision-trace")
    assert trace.status_code == 200
    payload = trace.json()
    assert payload["selected_hypothesis_id"] == "H-001"
    assert any(item["selected"] for item in payload["explanations"])
