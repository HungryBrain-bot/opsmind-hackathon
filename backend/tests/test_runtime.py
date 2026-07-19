from fastapi.testclient import TestClient

from app.main import app


def test_runtime_defaults_to_offline_fixture() -> None:
    response = TestClient(app).get("/api/v1/runtime")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "offline"
    assert payload["planner_provider"] == "fixture"
    assert payload["api_key_configured"] is False
    assert payload["version"] == "1.3.0"
