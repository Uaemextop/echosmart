"""Pydantic v2 schemas for tenant API payloads.

Each schema serves a specific role in the request/response cycle:

- ``TenantUpdate`` — validates incoming ``PUT`` bodies.
- ``TenantBranding`` — branding customisation payload.
- ``TenantResponse`` — serialises ORM models for outgoing JSON.
- ``TenantUsage`` — usage statistics response.

All response schemas use ``from_attributes = True`` so they can be
constructed directly from SQLAlchemy model instances via
:meth:`model_validate`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Input schemas
# ------------------------------------------------------------------

class TenantUpdate(BaseModel):
    """Payload for updating tenant profile.

    All fields are optional — only supplied keys are applied.

    Attributes:
        name: New tenant display name.
        settings: Updated settings JSON object.
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    settings: dict[str, Any] | None = None

    model_config = {"extra": "forbid"}


class TenantBranding(BaseModel):
    """Branding customisation payload.

    Attributes:
        logo_url: URL to the tenant's logo image.
        primary_color: Primary brand colour (hex).
        secondary_color: Secondary brand colour (hex).
    """

    logo_url: str | None = Field(default=None, max_length=500)
    primary_color: str | None = Field(default=None, max_length=20)
    secondary_color: str | None = Field(default=None, max_length=20)

    model_config = {"extra": "forbid"}


# ------------------------------------------------------------------
# Output schemas
# ------------------------------------------------------------------

class TenantResponse(BaseModel):
    """Outgoing representation of a tenant.

    Attributes:
        id: Unique tenant identifier.
        name: Display name.
        slug: URL-friendly identifier.
        is_active: Whether the tenant is active.
        branding: Branding configuration.
        settings: Tenant settings.
        created_at: Creation timestamp.
    """

    id: UUID
    name: str
    slug: str
    is_active: bool
    branding: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantUsage(BaseModel):
    """Tenant usage statistics.

    Attributes:
        total_users: Number of users in the tenant.
        total_gateways: Number of gateways in the tenant.
        total_sensors: Number of sensors in the tenant.
    """

    total_users: int
    total_gateways: int
    total_sensors: int
