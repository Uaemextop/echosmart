"""Standard API response envelopes.

Every endpoint should return either an ``ApiResponse`` (success) or an
``ErrorResponse`` (failure).  Using a uniform envelope simplifies
client-side parsing and makes the contract explicit in OpenAPI docs.

Typical usage in a router::

    from src.shared.responses import ApiResponse

    @router.get("/sensors/{sensor_id}")
    async def read_sensor(sensor_id: UUID) -> ApiResponse:
        sensor = service.get(sensor_id)
        return ApiResponse(status="ok", data=sensor)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """Uniform success envelope returned by all endpoints.

    Attributes:
        status: ``"ok"`` for success, ``"error"`` for handled failures.
        message: Optional human-readable context about the result.
        data: The payload — may be a single object, a list, or ``None``.
    """

    status: str = "ok"
    message: str | None = None
    data: Any = None

    model_config = {"json_schema_extra": {"examples": [{"status": "ok", "message": "Sensor created", "data": {"id": "..."}}]}}


class ErrorResponse(BaseModel):
    """Structured error payload for non-2xx responses.

    Attributes:
        detail: Human-readable error message.
        code: Machine-readable error code (e.g. ``"NOT_FOUND"``).
        timestamp: UTC time when the error occurred.
    """

    detail: str
    code: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_schema_extra": {"examples": [{"detail": "Sensor with id 'abc' not found", "code": "NOT_FOUND", "timestamp": "2025-01-01T00:00:00Z"}]}}
