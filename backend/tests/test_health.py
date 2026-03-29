"""Tests de health checks del backend."""


def test_root_health_check(client):
    """Verificar el estado base del backend."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "echosmart-backend",
        "version": "1.0.0",
    }


def test_health_endpoint(client):
    """Verificar el health check principal."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_legacy_health_endpoint(client):
    """Mantener compatibilidad con el endpoint legado."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
