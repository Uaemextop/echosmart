"""Schemas Pydantic para dispositivos EchoPy."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EchoPyBase(BaseModel):
    """Base schema para EchoPy."""

    name: Optional[str] = None
    location: Optional[str] = None
    greenhouse_name: Optional[str] = None


class EchoPyCreate(EchoPyBase):
    """Schema para registrar EchoPy (first-boot)."""

    hostname: str
    mac_address: str
    ble_uuid: Optional[str] = None
    firmware_version: Optional[str] = None


class EchoPyUpdate(EchoPyBase):
    """Schema para actualizar EchoPy."""

    pass


class EchoPyResponse(EchoPyBase):
    """Schema de respuesta con info de EchoPy."""

    id: str
    serial_number: Optional[str] = None
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    status: str
    is_online: bool
    firmware_version: Optional[str] = None
    ip_address: Optional[str] = None
    last_seen: Optional[datetime] = None
    bound_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EchoPyBindRequest(BaseModel):
    """Request para vincular EchoPy a serial y usuario."""

    serial_code: str
    mac_address: str
    hostname: Optional[str] = None
    ble_uuid: Optional[str] = None


class EchoPyDiagnostics(BaseModel):
    """Información de diagnóstico de un EchoPy."""

    cpu_usage: float
    memory_total_mb: int
    memory_used_mb: int
    disk_total_gb: float
    disk_used_gb: float
    temperature_celsius: Optional[float] = None
    uptime_seconds: int
    sensor_count: int
    firmware_version: str
    os_version: str
