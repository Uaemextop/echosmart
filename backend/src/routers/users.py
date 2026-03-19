"""Router de usuarios — /api/v1/users/*."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/")
async def list_users():
    """Listar usuarios del tenant."""
    # TODO: Implementar listado
    pass


@router.post("/")
async def create_user():
    """Crear un nuevo usuario."""
    # TODO: Implementar creación
    pass


@router.get("/me")
async def get_current_user():
    """Obtener perfil del usuario autenticado."""
    # TODO: Implementar perfil
    pass
