"""Schemas para health checks del backend."""

from pydantic import BaseModel


class RootStatusResponse(BaseModel):
    """Payload del endpoint raíz del backend."""

    status: str
    service: str
    version: str


class HealthCheckResponse(BaseModel):
    """Payload de health check básico."""

    status: str
