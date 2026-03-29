"""Pydantic v2 request/response schemas for the auth module.

These schemas are the **only** objects that cross the HTTP boundary.
The router deserialises incoming JSON into a ``*Request`` schema,
and the service returns domain objects that the router maps to a
``*Response`` or to the shared ``ApiResponse`` envelope.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# -----------------------------------------------------------------------
# Requests
# -----------------------------------------------------------------------


class RegisterRequest(BaseModel):
    """Payload for user registration (requires a valid kit serial)."""

    serial_code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Serial code of the EchoPy kit",
        examples=["ES-202603-0001"],
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)

    model_config = ConfigDict(extra="forbid")

    @field_validator("password")
    @classmethod
    def _password_strength(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def _normalise_email(cls, value: str) -> str:
        return value.lower().strip()


class LoginRequest(BaseModel):
    """Payload for standard user login."""

    email: EmailStr
    password: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("email", mode="before")
    @classmethod
    def _normalise_email(cls, value: str) -> str:
        return value.lower().strip()


class AdminLoginRequest(BaseModel):
    """Payload for admin login (optionally includes a TOTP code)."""

    email: EmailStr
    password: str
    totp_code: str | None = Field(
        default=None,
        min_length=6,
        max_length=6,
        description="Time-based one-time password for 2FA",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("email", mode="before")
    @classmethod
    def _normalise_email(cls, value: str) -> str:
        return value.lower().strip()


class RefreshRequest(BaseModel):
    """Payload for refreshing an access token."""

    refresh_token: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class UpdateProfileRequest(BaseModel):
    """Payload for updating the authenticated user's profile."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)

    model_config = ConfigDict(extra="forbid")


class ChangePasswordRequest(BaseModel):
    """Payload for changing the authenticated user's password."""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(extra="forbid")

    @field_validator("new_password")
    @classmethod
    def _password_strength(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class ForgotPasswordRequest(BaseModel):
    """Payload for requesting a password-reset e-mail."""

    email: EmailStr

    model_config = ConfigDict(extra="forbid")


class ResetPasswordRequest(BaseModel):
    """Payload for confirming a password reset via token."""

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(extra="forbid")

    @field_validator("new_password")
    @classmethod
    def _password_strength(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


# -----------------------------------------------------------------------
# Responses
# -----------------------------------------------------------------------


class TokenResponse(BaseModel):
    """JWT token pair returned on successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str

    model_config = ConfigDict(extra="forbid")


class UserProfile(BaseModel):
    """Public-facing view of the authenticated user's profile."""

    id: UUID
    email: str
    full_name: str
    phone: str | None = None
    role: str
    serial_number: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
