"""Esquemas Pydantic para gateways."""

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class GatewayCreate(BaseModel):
    """Esquema para crear un gateway."""

    name: str
    location: str | None = None


class GatewayResponse(BaseModel):
    """Esquema de respuesta de gateway."""

    id: UUID
    name: str
    location: str | None
    is_online: bool
    last_seen: datetime | None
    firmware_version: str | None

    model_config = {"from_attributes": True}
