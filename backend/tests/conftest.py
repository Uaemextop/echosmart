"""Fixtures compartidos para tests del backend."""

import pytest


@pytest.fixture
def app():
    """Crear instancia de la app FastAPI para testing."""
    from src.main import app
    return app
