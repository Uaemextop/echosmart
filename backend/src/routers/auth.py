"""Router de autenticación — /api/v1/auth/*."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login")
async def login():
    """Iniciar sesión con email y contraseña."""
    # TODO: Implementar autenticación JWT
    pass


@router.post("/refresh")
async def refresh_token():
    """Renovar access token con refresh token."""
    # TODO: Implementar refresh token
    pass


@router.post("/logout")
async def logout():
    """Cerrar sesión."""
    # TODO: Implementar logout
    pass
