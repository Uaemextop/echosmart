"""Router de alertas — /api/v1/alerts/*."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])


@router.get("/")
async def list_alerts():
    """Listar alertas activas del tenant."""
    # TODO: Implementar listado
    pass


@router.post("/rules")
async def create_alert_rule():
    """Crear una nueva regla de alerta."""
    # TODO: Implementar creación de regla
    pass


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Confirmar atención de una alerta."""
    # TODO: Implementar acknowledge
    pass
