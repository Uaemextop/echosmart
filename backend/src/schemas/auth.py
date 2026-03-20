"""Esquemas Pydantic para autenticación."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Esquema para solicitud de login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Esquema para respuesta con tokens JWT."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Esquema para renovar access token."""

    refresh_token: str
