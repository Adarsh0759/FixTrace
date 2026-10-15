from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_config_has_no_secrets():
    response = client.get("/config")
    assert response.status_code == 200
    body = response.json()
    assert "anthropic_api_key" not in body
    assert "llm_model" in body
