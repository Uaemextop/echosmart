"""Router de reportes — /api/v1/reports/*."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.get("/")
async def list_reports():
    """Listar reportes del tenant."""
    # TODO: Implementar listado
    pass


@router.post("/generate")
async def generate_report():
    """Generar un nuevo reporte (asincrónico)."""
    # TODO: Implementar generación
    pass


@router.get("/{report_id}/download")
async def download_report(report_id: str):
    """Descargar un reporte generado."""
    # TODO: Implementar descarga
    pass
