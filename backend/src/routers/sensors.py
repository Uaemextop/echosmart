"""Router de sensores — /api/v1/sensors/*."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/sensors", tags=["Sensors"])


@router.get("/")
async def list_sensors():
    """Listar sensores del tenant."""
    # TODO: Implementar listado
    pass


@router.post("/")
async def create_sensor():
    """Registrar un nuevo sensor."""
    # TODO: Implementar creación
    pass


@router.get("/{sensor_id}")
async def get_sensor(sensor_id: str):
    """Obtener detalle de un sensor."""
    # TODO: Implementar detalle
    pass


@router.get("/{sensor_id}/readings")
async def get_readings(sensor_id: str):
    """Obtener lecturas históricas de un sensor."""
    # TODO: Implementar historial
    pass
