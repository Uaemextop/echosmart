"""Router de tenants — /api/v1/tenants/*."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/tenants", tags=["Tenants"])


@router.get("/current")
async def get_current_tenant():
    """Obtener información del tenant actual."""
    # TODO: Implementar detalle
    pass


@router.put("/current")
async def update_tenant():
    """Actualizar configuración del tenant."""
    # TODO: Implementar actualización
    pass


@router.put("/current/branding")
async def update_branding():
    """Actualizar branding del tenant."""
    # TODO: Implementar branding
    pass
