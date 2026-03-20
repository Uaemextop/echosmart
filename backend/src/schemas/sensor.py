"""Esquemas Pydantic para sensores."""

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class SensorCreate(BaseModel):
    """Esquema para crear un sensor."""

    gateway_id: UUID
    name: str
    type: str
    unit: str
    min_value: float | None = None
    max_value: float | None = None
    location: str | None = None


class SensorResponse(BaseModel):
    """Esquema de respuesta de sensor."""

    id: UUID
    gateway_id: UUID
    name: str
    type: str
    unit: str
    is_online: bool
    last_reading_at: datetime | None

    model_config = {"from_attributes": True}
