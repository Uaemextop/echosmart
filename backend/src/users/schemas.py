"""Pydantic v2 schemas for user management API payloads.

Each schema serves a specific role in the request/response cycle:

- ``UserCreate`` — validates incoming ``POST`` bodies (admin creates user).
- ``UserUpdate`` — validates incoming ``PUT`` bodies (all fields optional).
- ``UserResponse`` — serialises ORM models for outgoing JSON.
- ``UserRoleUpdate`` — validates role change requests.

All response schemas use ``from_attributes = True`` so they can be
constructed directly from SQLAlchemy model instances via
:meth:`model_validate`.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ------------------------------------------------------------------
# Input schemas
# ------------------------------------------------------------------

class UserCreate(BaseModel):
    """Payload for admin-creating a new user.

    Attributes:
        email: User's email address.
        password: Initial password (will be hashed).
        full_name: User's display name.
        role: User role — defaults to ``"user"``.
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="user", max_length=50)

    model_config = {"extra": "forbid"}

    @field_validator("role")
    @classmethod
    def _validate_role(cls, value: str) -> str:
        allowed = {"admin", "user"}
        normalised = value.strip().lower()
        if normalised not in allowed:
            raise ValueError(
                f"Role must be one of: {', '.join(sorted(allowed))}"
            )
        return normalised


class UserUpdate(BaseModel):
    """Payload for updating an existing user.

    All fields are optional — only supplied keys are applied.

    Attributes:
        full_name: New display name.
        phone: New phone number.
        role: New role assignment.
    """

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    role: str | None = Field(default=None, max_length=50)

    model_config = {"extra": "forbid"}

    @field_validator("role")
    @classmethod
    def _validate_role(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {"admin", "user"}
        normalised = value.strip().lower()
        if normalised not in allowed:
            raise ValueError(
                f"Role must be one of: {', '.join(sorted(allowed))}"
            )
        return normalised


class UserRoleUpdate(BaseModel):
    """Payload for changing a user's role.

    Attributes:
        role: The new role to assign.
    """

    role: str = Field(..., max_length=50)

    model_config = {"extra": "forbid"}

    @field_validator("role")
    @classmethod
    def _validate_role(cls, value: str) -> str:
        allowed = {"admin", "user"}
        normalised = value.strip().lower()
        if normalised not in allowed:
            raise ValueError(
                f"Role must be one of: {', '.join(sorted(allowed))}"
            )
        return normalised


# ------------------------------------------------------------------
# Output schemas
# ------------------------------------------------------------------

class UserResponse(BaseModel):
    """Outgoing representation of a user.

    Attributes:
        id: Unique user identifier.
        email: User's email address.
        full_name: Display name.
        phone: Phone number.
        role: Current role.
        is_active: Whether the account is active.
        last_login: Timestamp of last login.
        created_at: Creation timestamp.
    """

    id: UUID
    email: str
    full_name: str
    phone: str | None = None
    role: str
    is_active: bool
    last_login: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
