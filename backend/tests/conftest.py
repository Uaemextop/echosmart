"""Fixtures compartidos para tests del backend."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    """Crear instancia de la app FastAPI para testing."""
    from src.main import app

    return app


@pytest.fixture
def client(app):
    """Crear cliente HTTP para pruebas de integración."""
    return TestClient(app)
