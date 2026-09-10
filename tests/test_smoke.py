from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_is_available() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "CeutIA"


def test_health_is_available() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_is_explicitly_not_ready_until_dependencies_are_connected() -> None:
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"


def test_configuration_does_not_expose_values() -> None:
    response = client.get("/diagnostics/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "valid"
    assert "DATABASE_URL" not in payload
    assert "REDIS_URL" not in payload
