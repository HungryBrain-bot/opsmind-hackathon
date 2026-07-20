from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_pack_list():
    response = client.get("/api/v1/investigation-packs")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "splunk-heavy-forwarder"


def test_unknown_pack():
    assert client.get("/api/v1/investigation-packs/missing").status_code == 404
