"""Pydantic v2 schemas for sensor and reading API payloads.

Each schema serves a specific role in the request/response cycle:

- ``*Create`` — validates incoming ``POST`` bodies.
- ``*Update`` — validates incoming ``PUT``/``PATCH`` bodies (all fields
  optional so partial updates work naturally).
- ``*Response`` — serialises ORM models for outgoing JSON.

All response schemas use ``from_attributes = True`` so they can be
constructed directly from SQLAlchemy model instances via
:meth:`model_validate`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ------------------------------------------------------------------
# Sensor schemas
# ------------------------------------------------------------------

class SensorCreate(BaseModel):
    """Payload for creating a new sensor.

    Attributes:
        gateway_id: The gateway this sensor is connected to.
        name: Human-readable sensor label.
        type: Sensor kind — one of ``temperature``, ``humidity``,
            ``light``, ``soil``, ``co2``.
        unit: Measurement unit (e.g. ``"°C"``, ``"%"``, ``"lux"``).
        min_value: Optional lower bound for valid readings.
        max_value: Optional upper bound for valid readings.
        location: Free-text location description.
    """

    gateway_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=50)
    unit: str = Field(..., min_length=1, max_length=20)
    min_value: float | None = None
    max_value: float | None = None
    location: str | None = Field(default=None, max_length=255)

    model_config = {"extra": "forbid"}

    @field_validator("type")
    @classmethod
    def _validate_sensor_type(cls, value: str) -> str:
        allowed = {"temperature", "humidity", "light", "soil", "co2"}
        normalised = value.strip().lower()
        if normalised not in allowed:
            raise ValueError(
                f"Sensor type must be one of: {', '.join(sorted(allowed))}"
            )
        return normalised


class SensorUpdate(BaseModel):
    """Payload for updating an existing sensor.

    All fields are optional — only supplied keys are applied.

    Attributes:
        name: New sensor label.
        type: New sensor kind.
        unit: New measurement unit.
        min_value: New lower bound.
        max_value: New upper bound.
        location: New location description.
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: str | None = Field(default=None, min_length=1, max_length=50)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    min_value: float | None = None
    max_value: float | None = None
    location: str | None = Field(default=None, max_length=255)

    model_config = {"extra": "forbid"}

    @field_validator("type")
    @classmethod
    def _validate_sensor_type(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {"temperature", "humidity", "light", "soil", "co2"}
        normalised = value.strip().lower()
        if normalised not in allowed:
            raise ValueError(
                f"Sensor type must be one of: {', '.join(sorted(allowed))}"
            )
        return normalised


class SensorResponse(BaseModel):
    """Outgoing representation of a sensor.

    Attributes:
        id: Unique sensor identifier.
        gateway_id: Parent gateway.
        tenant_id: Owning tenant.
        name: Human-readable label.
        type: Sensor kind.
        unit: Measurement unit.
        is_online: Whether the sensor is currently reporting data.
        last_reading_at: Timestamp of the most recent reading.
        location: Free-text location.
        created_at: Creation timestamp.
    """

    id: UUID
    gateway_id: UUID
    tenant_id: UUID
    name: str
    type: str
    unit: str
    is_online: bool
    last_reading_at: datetime | None = None
    location: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ------------------------------------------------------------------
# Reading schemas
# ------------------------------------------------------------------

class ReadingCreate(BaseModel):
    """Single reading in an ingestion request.

    Attributes:
        sensor_id: The sensor that produced this reading.
        value: The numeric measurement.
        timestamp: When the measurement was taken.  Defaults to the
            server time if omitted.
    """

    sensor_id: UUID
    value: float
    timestamp: datetime | None = None

    model_config = {"extra": "forbid"}


class ReadingResponse(BaseModel):
    """Outgoing representation of a reading.

    Attributes:
        id: Unique reading identifier.
        sensor_id: The sensor that produced this reading.
        value: The numeric measurement.
        timestamp: When the measurement was taken.
    """

    id: UUID
    sensor_id: UUID
    value: float
    timestamp: datetime

    model_config = {"from_attributes": True}


class ReadingBatchRequest(BaseModel):
    """Batch ingestion request containing multiple readings.

    Attributes:
        readings: One or more readings to ingest.
    """

    readings: list[ReadingCreate] = Field(..., min_length=1)

    model_config = {"extra": "forbid"}


# ------------------------------------------------------------------
# Dashboard schema
# ------------------------------------------------------------------

class DashboardResponse(BaseModel):
    """Tenant-level sensor dashboard summary.

    Attributes:
        total_sensors: Count of all sensors for the tenant.
        online_sensors: Count of sensors currently online.
        latest_readings: Mapping of sensor ID → latest reading info.
            Each value contains ``value``, ``unit``, and ``timestamp``.
    """

    total_sensors: int
    online_sensors: int
    latest_readings: dict[str, Any]

    model_config = {"from_attributes": True}
