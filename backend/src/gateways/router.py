"""FastAPI router for the ``/api/v1/gateways`` endpoints.

The router is intentionally **thin** — it:

1. Parses the HTTP request (path params, query params, body).
2. Delegates to :class:`~src.gateways.service.GatewayService`.
3. Wraps the result in :class:`~src.shared.responses.ApiResponse`.

All domain exceptions are translated to HTTP status codes via a
``_handle_domain_errors`` context manager, keeping endpoints clean and
consistent with the rest of the codebase.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.gateways.schemas import (
    GatewayCreate,
    GatewayResponse,
    GatewayStatusUpdate,
    GatewayUpdate,
)
from src.gateways.service import GatewayService
from src.models.user import User
from src.shared.dependencies import get_current_user
from src.shared.exceptions import (
    AuthenticationError,
    ConflictError,
    EchoSmartError,
    NotFoundError,
    ValidationError,
)
from src.shared.responses import ApiResponse

router = APIRouter(prefix="/api/v1/gateways", tags=["Gateways"])


# ------------------------------------------------------------------
# Error translation
# ------------------------------------------------------------------

_STATUS_MAP: dict[type[EchoSmartError], int] = {
    ValidationError: 422,
    NotFoundError: 404,
    ConflictError: 409,
    AuthenticationError: 401,
}


@contextmanager
def _handle_domain_errors() -> Generator[None, None, None]:
    """Translate domain exceptions into ``HTTPException``."""
    try:
        yield
    except EchoSmartError as exc:
        status = _STATUS_MAP.get(type(exc), 500)
        raise HTTPException(status_code=status, detail=exc.message) from exc


# ------------------------------------------------------------------
# Dependencies
# ------------------------------------------------------------------

def _gateway_service(db: Session = Depends(get_db)) -> GatewayService:
    """FastAPI dependency that creates a ``GatewayService``."""
    return GatewayService(db)


def _get_tenant_id(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UUID:
    """Resolve the tenant_id for the authenticated user."""
    user_id = UUID(current_user["sub"])
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise AuthenticationError("User account no longer exists")
    return user.tenant_id


# ------------------------------------------------------------------
# Gateway CRUD
# ------------------------------------------------------------------

@router.get("/", response_model=ApiResponse)
async def list_gateways(
    tenant_id: UUID = Depends(_get_tenant_id),
    service: GatewayService = Depends(_gateway_service),
) -> ApiResponse:
    """List all gateways for the authenticated user's tenant."""
    with _handle_domain_errors():
        gateways = service.list_gateways(tenant_id)
    return ApiResponse(
        status="ok",
        data=[GatewayResponse.model_validate(g).model_dump(mode="json") for g in gateways],
    )


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_gateway(
    body: GatewayCreate,
    tenant_id: UUID = Depends(_get_tenant_id),
    service: GatewayService = Depends(_gateway_service),
) -> ApiResponse:
    """Create a new gateway under the authenticated user's tenant."""
    with _handle_domain_errors():
        gateway = service.create_gateway(tenant_id, body.model_dump())
    return ApiResponse(
        status="ok",
        message="Gateway created successfully",
        data=GatewayResponse.model_validate(gateway).model_dump(mode="json"),
    )


@router.get("/{gateway_id}", response_model=ApiResponse)
async def get_gateway(
    gateway_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: GatewayService = Depends(_gateway_service),
) -> ApiResponse:
    """Retrieve a single gateway by its ID."""
    with _handle_domain_errors():
        gateway = service.get_gateway(gateway_id)
    return ApiResponse(
        status="ok",
        data=GatewayResponse.model_validate(gateway).model_dump(mode="json"),
    )


@router.put("/{gateway_id}", response_model=ApiResponse)
async def update_gateway(
    gateway_id: UUID,
    body: GatewayUpdate,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: GatewayService = Depends(_gateway_service),
) -> ApiResponse:
    """Update an existing gateway (partial update supported)."""
    update_data = body.model_dump(exclude_unset=True)
    with _handle_domain_errors():
        gateway = service.update_gateway(gateway_id, update_data)
    return ApiResponse(
        status="ok",
        message="Gateway updated successfully",
        data=GatewayResponse.model_validate(gateway).model_dump(mode="json"),
    )


@router.delete("/{gateway_id}", response_model=ApiResponse)
async def delete_gateway(
    gateway_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: GatewayService = Depends(_gateway_service),
) -> ApiResponse:
    """Delete a gateway by its ID."""
    with _handle_domain_errors():
        service.delete_gateway(gateway_id)
    return ApiResponse(
        status="ok",
        message="Gateway deleted successfully",
    )


# ------------------------------------------------------------------
# Status & heartbeat
# ------------------------------------------------------------------

@router.get("/{gateway_id}/status", response_model=ApiResponse)
async def get_gateway_status(
    gateway_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: GatewayService = Depends(_gateway_service),
) -> ApiResponse:
    """Return the current status of a gateway."""
    with _handle_domain_errors():
        gateway = service.get_gateway(gateway_id)
    return ApiResponse(
        status="ok",
        data={
            "id": str(gateway.id),
            "status": gateway.status.value if hasattr(gateway.status, "value") else gateway.status,
            "is_online": gateway.is_online,
            "last_seen": gateway.last_seen.isoformat() if gateway.last_seen else None,
            "ip_address": gateway.ip_address,
            "firmware_version": gateway.firmware_version,
        },
    )


@router.post("/{gateway_id}/heartbeat", response_model=ApiResponse)
async def heartbeat(
    gateway_id: UUID,
    body: GatewayStatusUpdate,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: GatewayService = Depends(_gateway_service),
) -> ApiResponse:
    """Process a heartbeat from a gateway device.

    Updates the gateway's online status, last-seen timestamp, IP
    address, and firmware version.
    """
    with _handle_domain_errors():
        gateway = service.update_status(gateway_id, body.model_dump())
    return ApiResponse(
        status="ok",
        message="Heartbeat recorded",
        data=GatewayResponse.model_validate(gateway).model_dump(mode="json"),
    )
