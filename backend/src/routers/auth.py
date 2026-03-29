"""Router de autenticación — /api/v1/auth/*.

Dos flujos de login separados:
- /login: usuarios finales (requiere serial válido para registro)
- /admin/login: administradores (requiere rol admin + 2FA)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


# --- Schemas ---


class RegisterRequest(BaseModel):
    """Request de registro de usuario (requiere serial del kit)."""

    serial_code: str  # Número de serie del kit
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None


class RegisterResponse(BaseModel):
    """Response de registro exitoso."""

    user_id: str
    email: str
    serial_code: str
    message: str


class LoginRequest(BaseModel):
    """Request de login."""

    email: str
    password: str


class AdminLoginRequest(BaseModel):
    """Request de login admin (con 2FA)."""

    email: str
    password: str
    totp_code: Optional[str] = None  # Código 2FA


class TokenResponse(BaseModel):
    """Response con tokens JWT."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class ForgotPasswordRequest(BaseModel):
    """Request para solicitar reset de contraseña."""

    email: str


class ResetPasswordRequest(BaseModel):
    """Request para confirmar reset de contraseña."""

    token: str
    new_password: str


class UserProfile(BaseModel):
    """Perfil del usuario autenticado."""

    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    serial_number: Optional[str] = None
    is_active: bool


# --- Endpoints ---


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """Registro de usuario con número de serie del kit.

    1. Valida que el serial existe y está disponible
    2. Crea el usuario
    3. Marca el serial como 'registered'
    4. Retorna token de acceso
    """
    # TODO: Implementar registro con validación de serial
    return RegisterResponse(
        user_id="placeholder",
        email=request.email,
        serial_code=request.serial_code,
        message="Usuario registrado exitosamente",
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login de usuario final con email y contraseña."""
    # TODO: Implementar autenticación JWT
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(request: AdminLoginRequest):
    """Login exclusivo para administradores.

    Requiere rol admin + código 2FA (si 2FA habilitado).
    """
    # TODO: Implementar login admin con 2FA
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token():
    """Renovar access token con refresh token."""
    # TODO: Implementar refresh token
    raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout")
async def logout():
    """Cerrar sesión e invalidar tokens."""
    # TODO: Implementar logout (blacklist token)
    return {"message": "Sesión cerrada"}


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Solicitar reset de contraseña por email."""
    # TODO: Implementar envío de email con token de reset
    return {"message": "Si el email existe, recibirás instrucciones para restablecer tu contraseña"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Confirmar reset de contraseña con token."""
    # TODO: Implementar reset de contraseña
    return {"message": "Contraseña actualizada exitosamente"}


@router.get("/me", response_model=UserProfile)
async def get_profile():
    """Obtener perfil del usuario autenticado."""
    # TODO: Implementar con auth dependency
    raise HTTPException(status_code=401, detail="Not authenticated")


@router.put("/me")
async def update_profile():
    """Actualizar perfil propio."""
    # TODO: Implementar actualización de perfil
    raise HTTPException(status_code=401, detail="Not authenticated")


@router.put("/me/password")
async def change_password():
    """Cambiar contraseña (requiere contraseña actual)."""
    # TODO: Implementar cambio de contraseña
    raise HTTPException(status_code=401, detail="Not authenticated")
