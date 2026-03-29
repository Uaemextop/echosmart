"""Pydantic v2 schemas for gateway API payloads.

Each schema serves a specific role in the request/response cycle:

- ``GatewayCreate`` — validates incoming ``POST`` bodies.
- ``GatewayUpdate`` — validates incoming ``PUT`` bodies (all fields
  optional so partial updates work naturally).
- ``GatewayResponse`` — serialises ORM models for outgoing JSON.
- ``GatewayStatusUpdate`` — heartbeat / status change payload.

All response schemas use ``from_attributes = True`` so they can be
constructed directly from SQLAlchemy model instances via
:meth:`model_validate`.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Input schemas
# ------------------------------------------------------------------

class GatewayCreate(BaseModel):
    """Payload for creating a new gateway.

    Attributes:
        name: Human-readable gateway label.
        location: Free-text location description.
    """

    name: str = Field(..., min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)

    model_config = {"extra": "forbid"}


class GatewayUpdate(BaseModel):
    """Payload for updating an existing gateway.

    All fields are optional — only supplied keys are applied.

    Attributes:
        name: New gateway label.
        location: New location description.
        firmware_version: Updated firmware version string.
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    firmware_version: str | None = Field(default=None, max_length=50)

    model_config = {"extra": "forbid"}


class GatewayStatusUpdate(BaseModel):
    """Heartbeat / status change payload sent by the device.

    Attributes:
        is_online: Whether the gateway is currently reachable.
        ip_address: Current IP address reported by the device.
        firmware_version: Current firmware version running on device.
    """

    is_online: bool
    ip_address: str | None = Field(default=None, max_length=45)
    firmware_version: str | None = Field(default=None, max_length=50)

    model_config = {"extra": "forbid"}


# ------------------------------------------------------------------
# Output schemas
# ------------------------------------------------------------------

class GatewayResponse(BaseModel):
    """Outgoing representation of a gateway.

    Attributes:
        id: Unique gateway identifier.
        tenant_id: Owning tenant.
        name: Human-readable label.
        serial_number: Hardware serial number.
        location: Free-text location.
        status: Current operational status.
        is_online: Whether the gateway is currently online.
        last_seen: Timestamp of the last heartbeat.
        firmware_version: Running firmware version.
        created_at: Creation timestamp.
    """

    id: UUID
    tenant_id: UUID
    name: str
    serial_number: str | None = None
    location: str | None = None
    status: str
    is_online: bool
    last_seen: datetime | None = None
    firmware_version: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
