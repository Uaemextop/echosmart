"""Router de gateways — /api/v1/gateways/*."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/gateways", tags=["Gateways"])


@router.get("/")
async def list_gateways():
    """Listar gateways del tenant."""
    # TODO: Implementar listado
    pass


@router.post("/")
async def create_gateway():
    """Registrar un nuevo gateway."""
    # TODO: Implementar creación
    pass


@router.get("/{gateway_id}")
async def get_gateway(gateway_id: str):
    """Obtener detalle de un gateway."""
    # TODO: Implementar detalle
    pass
