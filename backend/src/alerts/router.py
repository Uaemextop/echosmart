"""FastAPI router for the ``/api/v1/alerts`` endpoints.

The router is intentionally **thin** — it:

1. Parses the HTTP request (path params, query params, body).
2. Delegates to :class:`~src.alerts.service.AlertService`.
3. Wraps the result in :class:`~src.shared.responses.ApiResponse`.

All domain exceptions are translated to HTTP status codes via a
``_handle_domain_errors`` context manager, keeping endpoints clean and
consistent with the rest of the codebase.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.alerts.schemas import (
    AlertAcknowledge,
    AlertResponse,
    AlertRuleCreate,
    AlertStatsResponse,
    SeverityBreakdown,
)
from src.alerts.service import AlertService
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

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])


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
    """Translate domain exceptions into ``HTTPException``.

    Usage::

        with _handle_domain_errors():
            result = service.do_something()
    """
    try:
        yield
    except EchoSmartError as exc:
        status = _STATUS_MAP.get(type(exc), 500)
        raise HTTPException(status_code=status, detail=exc.message) from exc


# ------------------------------------------------------------------
# Dependencies
# ------------------------------------------------------------------

def _alert_service(db: Session = Depends(get_db)) -> AlertService:
    """FastAPI dependency that creates an ``AlertService``."""
    return AlertService(db)


def _get_tenant_id(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UUID:
    """Resolve the tenant_id for the authenticated user.

    The JWT claims contain ``sub`` (user_id) and ``role`` but *not*
    ``tenant_id``, so we look it up from the user record.

    Raises:
        AuthenticationError: If the user record no longer exists.
    """
    user_id = UUID(current_user["sub"])
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise AuthenticationError("User account no longer exists")
    return user.tenant_id


def _get_user_id(current_user: dict = Depends(get_current_user)) -> UUID:
    """Extract the authenticated user's ID from JWT claims."""
    return UUID(current_user["sub"])


# ------------------------------------------------------------------
# List & statistics
# ------------------------------------------------------------------


@router.get("/", response_model=ApiResponse)
async def list_alerts(
    severity: str | None = Query(default=None, description="Filter by severity level"),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    tenant_id: UUID = Depends(_get_tenant_id),
    service: AlertService = Depends(_alert_service),
) -> ApiResponse:
    """List alerts for the authenticated user's tenant.

    Supports optional filtering by ``severity`` and ``is_active``.
    """
    with _handle_domain_errors():
        alerts = service.list_alerts(tenant_id, severity=severity, is_active=is_active)
    return ApiResponse(
        status="ok",
        data=[AlertResponse.model_validate(a).model_dump(mode="json") for a in alerts],
    )


@router.get("/stats", response_model=ApiResponse)
async def alert_stats(
    tenant_id: UUID = Depends(_get_tenant_id),
    service: AlertService = Depends(_alert_service),
) -> ApiResponse:
    """Return aggregate alert statistics for the tenant."""
    with _handle_domain_errors():
        stats = service.get_alert_stats(tenant_id)
    return ApiResponse(
        status="ok",
        data=AlertStatsResponse(
            total=stats["total"],
            active=stats["active"],
            acknowledged=stats["acknowledged"],
            by_severity=SeverityBreakdown(**stats["by_severity"]),
        ).model_dump(),
    )


# ------------------------------------------------------------------
# Rule creation
# ------------------------------------------------------------------


@router.post("/rules", response_model=ApiResponse, status_code=201)
async def create_alert_rule(
    body: AlertRuleCreate,
    tenant_id: UUID = Depends(_get_tenant_id),
    service: AlertService = Depends(_alert_service),
) -> ApiResponse:
    """Create a new alert rule.

    The rule is stored as an :class:`Alert` entry that becomes active
    immediately.
    """
    with _handle_domain_errors():
        alert = service.create_alert(tenant_id, body.model_dump())
    return ApiResponse(
        status="ok",
        message="Alert rule created successfully",
        data=AlertResponse.model_validate(alert).model_dump(mode="json"),
    )


# ------------------------------------------------------------------
# Single-alert operations
# ------------------------------------------------------------------


@router.get("/{alert_id}", response_model=ApiResponse)
async def get_alert(
    alert_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: AlertService = Depends(_alert_service),
) -> ApiResponse:
    """Retrieve a single alert by its ID."""
    with _handle_domain_errors():
        alert = service.get_alert(alert_id)
    return ApiResponse(
        status="ok",
        data=AlertResponse.model_validate(alert).model_dump(mode="json"),
    )


@router.post("/{alert_id}/acknowledge", response_model=ApiResponse)
async def acknowledge_alert(
    alert_id: UUID,
    body: AlertAcknowledge | None = None,
    user_id: UUID = Depends(_get_user_id),
    service: AlertService = Depends(_alert_service),
) -> ApiResponse:
    """Acknowledge an alert.

    If the request body is omitted or ``acknowledged_by`` is ``null``,
    the currently authenticated user is used.
    """
    ack_user = (body.acknowledged_by if body and body.acknowledged_by else user_id)
    with _handle_domain_errors():
        alert = service.acknowledge_alert(alert_id, ack_user)
    return ApiResponse(
        status="ok",
        message="Alert acknowledged successfully",
        data=AlertResponse.model_validate(alert).model_dump(mode="json"),
    )


@router.post("/{alert_id}/resolve", response_model=ApiResponse)
async def resolve_alert(
    alert_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: AlertService = Depends(_alert_service),
) -> ApiResponse:
    """Resolve (deactivate) an alert."""
    with _handle_domain_errors():
        alert = service.resolve_alert(alert_id)
    return ApiResponse(
        status="ok",
        message="Alert resolved successfully",
        data=AlertResponse.model_validate(alert).model_dump(mode="json"),
    )
