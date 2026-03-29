"""FastAPI router for the ``/api/v1/tenants`` endpoints.

Provides tenant self-service endpoints — the authenticated user
accesses their own tenant's data via ``/current``.

The router is intentionally **thin** — it:

1. Parses the HTTP request (path params, query params, body).
2. Delegates to :class:`~src.tenants.service.TenantService`.
3. Wraps the result in :class:`~src.shared.responses.ApiResponse`.

All domain exceptions are translated to HTTP status codes via a
``_handle_domain_errors`` context manager.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
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
from src.tenants.schemas import (
    TenantBranding,
    TenantResponse,
    TenantUpdate,
    TenantUsage,
)
from src.tenants.service import TenantService

router = APIRouter(prefix="/api/v1/tenants", tags=["Tenants"])


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

def _tenant_service(db: Session = Depends(get_db)) -> TenantService:
    """FastAPI dependency that creates a ``TenantService``."""
    return TenantService(db)


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
# Tenant endpoints
# ------------------------------------------------------------------

@router.get("/current", response_model=ApiResponse)
async def get_current_tenant(
    tenant_id: UUID = Depends(_get_tenant_id),
    service: TenantService = Depends(_tenant_service),
) -> ApiResponse:
    """Retrieve the authenticated user's tenant profile."""
    with _handle_domain_errors():
        tenant = service.get_tenant(tenant_id)
    return ApiResponse(
        status="ok",
        data=TenantResponse.model_validate(tenant).model_dump(mode="json"),
    )


@router.put("/current", response_model=ApiResponse)
async def update_current_tenant(
    body: TenantUpdate,
    tenant_id: UUID = Depends(_get_tenant_id),
    service: TenantService = Depends(_tenant_service),
) -> ApiResponse:
    """Update the authenticated user's tenant profile."""
    update_data = body.model_dump(exclude_unset=True)
    with _handle_domain_errors():
        tenant = service.update_tenant(tenant_id, update_data)
    return ApiResponse(
        status="ok",
        message="Tenant updated successfully",
        data=TenantResponse.model_validate(tenant).model_dump(mode="json"),
    )


@router.put("/current/branding", response_model=ApiResponse)
async def update_current_tenant_branding(
    body: TenantBranding,
    tenant_id: UUID = Depends(_get_tenant_id),
    service: TenantService = Depends(_tenant_service),
) -> ApiResponse:
    """Update branding for the authenticated user's tenant."""
    branding_data = body.model_dump(exclude_unset=True)
    with _handle_domain_errors():
        tenant = service.update_branding(tenant_id, branding_data)
    return ApiResponse(
        status="ok",
        message="Branding updated successfully",
        data=TenantResponse.model_validate(tenant).model_dump(mode="json"),
    )


@router.get("/current/usage", response_model=ApiResponse)
async def get_current_tenant_usage(
    tenant_id: UUID = Depends(_get_tenant_id),
    service: TenantService = Depends(_tenant_service),
) -> ApiResponse:
    """Return usage statistics for the authenticated user's tenant."""
    with _handle_domain_errors():
        usage = service.get_usage(tenant_id)
    return ApiResponse(
        status="ok",
        data=TenantUsage(**usage).model_dump(),
    )
