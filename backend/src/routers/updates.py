"""Router de actualizaciones Cosmuodate — /api/v1/updates/*.

Sistema de actualizaciones para gateway, sistema, apps y sensores.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/updates", tags=["Updates (Cosmuodate)"])


# --- Schemas ---


class UpdateInfo(BaseModel):
    """Información de una actualización disponible."""

    component: str  # gateway, system, app-web, app-mobile, app-desktop, sensor
    version: str
    channel: str  # stable, beta
    release_date: str
    size_mb: float
    checksum_sha256: str
    changelog: str
    is_critical: bool = False


class UpdateDownloadResponse(BaseModel):
    """Response con URL de descarga autorizada."""

    download_url: str
    expires_at: str
    checksum_sha256: str


class UpdateApplyRequest(BaseModel):
    """Request para confirmar aplicación de update."""

    component: str
    version: str
    echopy_id: Optional[str] = None


# --- Endpoints ---


@router.get("/gateway/latest", response_model=UpdateInfo)
async def get_latest_gateway_update(
    channel: str = Query("stable", description="Canal: stable o beta"),
):
    """Última actualización disponible del gateway/EchoPy.

    Consultado por `echosmart cosmuodate gateway --check=true`.
    """
    return UpdateInfo(
        component="gateway",
        version="1.0.0",
        channel=channel,
        release_date="2026-03-29",
        size_mb=45.2,
        checksum_sha256="placeholder",
        changelog="Initial release",
    )


@router.get("/system/latest", response_model=UpdateInfo)
async def get_latest_system_update(
    channel: str = Query("stable"),
):
    """Última actualización del sistema base."""
    return UpdateInfo(
        component="system",
        version="1.0.0",
        channel=channel,
        release_date="2026-03-29",
        size_mb=120.0,
        checksum_sha256="placeholder",
        changelog="Initial release",
    )


@router.get("/app/{platform}/latest", response_model=UpdateInfo)
async def get_latest_app_update(
    platform: str,
    channel: str = Query("stable"),
):
    """Última actualización de la app (web, mobile, desktop)."""
    return UpdateInfo(
        component=f"app-{platform}",
        version="1.0.0",
        channel=channel,
        release_date="2026-03-29",
        size_mb=25.0,
        checksum_sha256="placeholder",
        changelog="Initial release",
    )


@router.get("/sensor/{sensor_type}/latest", response_model=UpdateInfo)
async def get_latest_sensor_update(
    sensor_type: str,
    channel: str = Query("stable"),
):
    """Último firmware o perfil de sensor."""
    return UpdateInfo(
        component=f"sensor-{sensor_type}",
        version="1.0.0",
        channel=channel,
        release_date="2026-03-29",
        size_mb=0.5,
        checksum_sha256="placeholder",
        changelog="Initial sensor profile",
    )


@router.post("/{component}/{update_id}/download", response_model=UpdateDownloadResponse)
async def authorize_download(component: str, update_id: str):
    """Registrar/autorizar descarga de actualización."""
    return UpdateDownloadResponse(
        download_url=f"https://updates.echosmart.io/{component}/{update_id}",
        expires_at="2026-03-30T00:00:00Z",
        checksum_sha256="placeholder",
    )


@router.post("/{component}/{update_id}/apply")
async def confirm_apply(component: str, update_id: str, request: UpdateApplyRequest):
    """Confirmar que la actualización fue aplicada exitosamente."""
    return {
        "component": component,
        "update_id": update_id,
        "status": "applied",
    }


@router.get("/checksums/{artifact}")
async def get_checksum(artifact: str):
    """SHA256 y firma del artefacto."""
    return {
        "artifact": artifact,
        "sha256": "placeholder",
        "signature": "placeholder",
    }
