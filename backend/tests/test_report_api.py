import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _id():
    r = client.post(
        "/api/v1/investigations",
        json={
            "problem": "Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?",
            "environment": "Production",
            "priority": "High",
        },
    )
    i = r.json()["investigation_id"]
    for _ in range(100):
        if client.get(f"/api/v1/investigations/{i}").json()["status"] in {
            "completed",
            "inconclusive",
            "failed",
        }:
            return i
        time.sleep(0.05)
    raise AssertionError("not completed")


def test_report_endpoints():
    i = _id()
    r = client.get(f"/api/v1/investigations/{i}/report")
    assert r.status_code == 200
    assert r.json()["decision_trace"]["selected_hypothesis_id"] == "H-001"
    md = client.get(f"/api/v1/investigations/{i}/report.md")
    assert md.status_code == 200
    assert md.headers["content-type"].startswith("text/markdown")
    assert "# OpsMind Investigation Report" in md.text
