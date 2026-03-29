"""Router de dispositivos EchoPy — /api/v1/echopy/*.

Gestión de dispositivos EchoPy (gateway Raspberry Pi).
Admin: gestión completa, SSH remoto, suspend, diagnostics.
User: solo ver sus propios EchoPys.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/echopy", tags=["EchoPy"])


# --- Schemas ---


class EchoPyBindRequest(BaseModel):
    """Request para vincular un EchoPy a serial y usuario."""

    serial_code: str
    mac_address: str
    hostname: Optional[str] = None
    ble_uuid: Optional[str] = None


class EchoPyBindResponse(BaseModel):
    """Response de vinculación de EchoPy."""

    echopy_id: str
    serial_code: str
    status: str
    message: str


class EchoPyInfo(BaseModel):
    """Información completa de un EchoPy."""

    id: str
    serial_number: Optional[str] = None
    hostname: Optional[str] = None
    status: str
    is_online: bool
    firmware_version: Optional[str] = None
    ip_address: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    greenhouse_name: Optional[str] = None
    last_seen: Optional[datetime] = None


class RemoteCommandRequest(BaseModel):
    """Request para ejecutar comando remoto en un EchoPy."""

    command: str
    use_sudo: bool = False


class RemoteCommandResponse(BaseModel):
    """Response de comando remoto."""

    stdout: str
    stderr: str
    exit_code: int


class DiagnosticsResponse(BaseModel):
    """Información de diagnóstico del EchoPy."""

    cpu_usage: float
    memory_total_mb: int
    memory_used_mb: int
    disk_total_gb: float
    disk_used_gb: float
    temperature_celsius: Optional[float] = None
    uptime_seconds: int
    network_interfaces: dict
    sensor_count: int
    firmware_version: str
    os_version: str


# --- Endpoints ---


@router.post("/bind", response_model=EchoPyBindResponse)
async def bind_echopy(request: EchoPyBindRequest):
    """Vincular EchoPy a serial y usuario.

    Usado durante el registro/pairing desde la app móvil.
    Asigna permanentemente el serial al EchoPy y al usuario.
    """
    # TODO: Implementar vinculación
    return EchoPyBindResponse(
        echopy_id="placeholder",
        serial_code=request.serial_code,
        status="active",
        message="EchoPy vinculado exitosamente",
    )


@router.get("/")
async def list_echopys(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    """Listar EchoPys.

    User: solo los propios. Admin: todos.
    """
    # TODO: Implementar con auth
    return {"echopys": [], "total": 0, "page": page, "limit": limit}


@router.get("/{echopy_id}", response_model=EchoPyInfo)
async def get_echopy(echopy_id: str):
    """Detalle de un EchoPy (info, sensores, estado, debug)."""
    # TODO: Implementar consulta
    raise HTTPException(status_code=404, detail="EchoPy not found")


@router.put("/{echopy_id}")
async def update_echopy(echopy_id: str):
    """Actualizar configuración del EchoPy."""
    # TODO: Implementar actualización
    return {"echopy_id": echopy_id, "updated": True}


@router.post("/{echopy_id}/unbind")
async def unbind_echopy(echopy_id: str):
    """Desvincular EchoPy del usuario (admin only, libera serial)."""
    # TODO: Implementar desvinculación
    return {"echopy_id": echopy_id, "status": "unbound"}


@router.post("/{echopy_id}/suspend")
async def suspend_echopy(echopy_id: str, reason: Optional[str] = None):
    """Suspender servicio del EchoPy temporalmente (admin only)."""
    # TODO: Implementar suspensión
    return {"echopy_id": echopy_id, "status": "suspended", "reason": reason}


@router.post("/{echopy_id}/reactivate")
async def reactivate_echopy(echopy_id: str):
    """Reactivar servicio suspendido (admin only)."""
    # TODO: Implementar reactivación
    return {"echopy_id": echopy_id, "status": "active"}


@router.post("/{echopy_id}/reboot")
async def reboot_echopy(echopy_id: str):
    """Reiniciar EchoPy remotamente (admin only)."""
    # TODO: Implementar reinicio via MQTT/SSH
    return {"echopy_id": echopy_id, "rebooting": True}


@router.post("/{echopy_id}/remote-command", response_model=RemoteCommandResponse)
async def remote_command(echopy_id: str, request: RemoteCommandRequest):
    """Ejecutar comando remoto en el EchoPy (admin only, SSH con sudo)."""
    # TODO: Implementar ejecución remota segura
    return RemoteCommandResponse(
        stdout="Command execution placeholder",
        stderr="",
        exit_code=0,
    )


@router.get("/{echopy_id}/diagnostics", response_model=DiagnosticsResponse)
async def get_diagnostics(echopy_id: str):
    """Info de depuración: CPU, RAM, disco, red, sensores, versiones."""
    # TODO: Implementar consulta de diagnósticos via MQTT
    raise HTTPException(status_code=404, detail="EchoPy not found or offline")


@router.get("/{echopy_id}/logs")
async def get_logs(
    echopy_id: str,
    lines: int = Query(100, ge=1, le=1000),
    service: Optional[str] = Query(None, description="Servicio específico"),
):
    """Últimas N líneas de logs del EchoPy."""
    # TODO: Implementar obtención de logs via SSH/MQTT
    return {"echopy_id": echopy_id, "lines": [], "total": 0}
