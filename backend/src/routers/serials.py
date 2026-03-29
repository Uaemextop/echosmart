"""Router de números de serie — /api/v1/serials/*.

Gestión de seriales para kits EchoPy.
Solo admin puede generar, listar, revocar y exportar.
El endpoint /validate es público (usado durante registro).
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/serials", tags=["Serials"])


# --- Schemas ---


class SerialValidateRequest(BaseModel):
    """Request para validar un serial."""

    code: str


class SerialValidateResponse(BaseModel):
    """Response de validación de serial."""

    valid: bool
    status: str  # available, registered, revoked, not_found


class SerialGenerateRequest(BaseModel):
    """Request para generar seriales."""

    quantity: int = 10
    prefix: str = "ES"


class SerialInfo(BaseModel):
    """Información de un serial."""

    code: str
    status: str
    user_email: Optional[str] = None
    echopy_id: Optional[str] = None
    generated_at: Optional[datetime] = None
    registered_at: Optional[datetime] = None


class SerialStatsResponse(BaseModel):
    """Estadísticas de seriales."""

    total: int
    available: int
    registered: int
    revoked: int


# --- Endpoints ---


@router.post("/validate", response_model=SerialValidateResponse)
async def validate_serial(request: SerialValidateRequest):
    """Validar que un serial existe, es válido y no está usado.

    Público — usado durante el registro de usuario desde la app.
    """
    # TODO: Consultar base de datos
    return SerialValidateResponse(valid=True, status="available")


@router.get("/")
async def list_serials(
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    """Listar todos los seriales (admin only).

    Soporta filtros por estado, paginación.
    """
    # TODO: Implementar con auth admin
    return {"serials": [], "total": 0, "page": page, "limit": limit}


@router.post("/generate")
async def generate_serials(request: SerialGenerateRequest):
    """Generar batch de seriales nuevos (admin only).

    Genera seriales con formato ES-YYYYMM-XXXX.
    """
    # TODO: Implementar generación de seriales
    return {
        "generated": request.quantity,
        "prefix": request.prefix,
        "serials": [],
    }


@router.get("/stats", response_model=SerialStatsResponse)
async def serial_stats():
    """Estadísticas de seriales (admin only)."""
    # TODO: Implementar consulta
    return SerialStatsResponse(total=0, available=0, registered=0, revoked=0)


@router.get("/export")
async def export_serials(format: str = Query("csv", description="csv o json")):
    """Exportar seriales a CSV o JSON (admin only).

    Para imprimir etiquetas con números de serie + QR code.
    """
    # TODO: Implementar exportación
    return {"format": format, "data": []}


@router.get("/{serial}")
async def get_serial(serial: str):
    """Detalle de un serial (admin only)."""
    # TODO: Implementar consulta
    raise HTTPException(status_code=404, detail="Serial not found")


@router.post("/{serial}/revoke")
async def revoke_serial(serial: str, reason: Optional[str] = None):
    """Revocar un serial (admin only)."""
    # TODO: Implementar revocación
    return {"serial": serial, "status": "revoked", "reason": reason}
