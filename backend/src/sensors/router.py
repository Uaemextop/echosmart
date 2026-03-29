"""FastAPI router for the ``/api/v1/sensors`` endpoints.

The router is intentionally **thin** — it:

1. Parses the HTTP request (path params, query params, body).
2. Delegates to :class:`~src.sensors.service.SensorService`.
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

from src.database import get_db
from src.models.user import User
from src.sensors.schemas import (
    DashboardResponse,
    ReadingBatchRequest,
    ReadingResponse,
    SensorCreate,
    SensorResponse,
    SensorUpdate,
)
from src.sensors.service import SensorService
from src.shared.dependencies import get_current_user
from src.shared.exceptions import (
    AuthenticationError,
    ConflictError,
    EchoSmartError,
    NotFoundError,
    ValidationError,
)
from src.shared.responses import ApiResponse

router = APIRouter(prefix="/api/v1/sensors", tags=["Sensors"])


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

def _sensor_service(db: Session = Depends(get_db)) -> SensorService:
    """FastAPI dependency that creates a ``SensorService``."""
    return SensorService(db)


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


# ------------------------------------------------------------------
# Sensor CRUD
# ------------------------------------------------------------------


@router.get("/dashboard", response_model=ApiResponse)
async def dashboard(
    tenant_id: UUID = Depends(_get_tenant_id),
    service: SensorService = Depends(_sensor_service),
) -> ApiResponse:
    """Return a tenant-level sensor dashboard summary.

    Includes total/online sensor counts and the latest reading per
    sensor.
    """
    with _handle_domain_errors():
        data = service.get_dashboard_data(tenant_id)
    return ApiResponse(
        status="ok",
        data=DashboardResponse(**data).model_dump(),
    )


@router.get("/", response_model=ApiResponse)
async def list_sensors(
    skip: int = Query(default=0, ge=0, description="Records to skip"),
    limit: int = Query(default=50, ge=1, le=100, description="Max records"),
    tenant_id: UUID = Depends(_get_tenant_id),
    service: SensorService = Depends(_sensor_service),
) -> ApiResponse:
    """List sensors for the authenticated user's tenant."""
    with _handle_domain_errors():
        sensors = service.list_sensors(tenant_id, skip=skip, limit=limit)
    return ApiResponse(
        status="ok",
        data=[SensorResponse.model_validate(s).model_dump(mode="json") for s in sensors],
    )


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_sensor(
    body: SensorCreate,
    tenant_id: UUID = Depends(_get_tenant_id),
    service: SensorService = Depends(_sensor_service),
) -> ApiResponse:
    """Create a new sensor under the authenticated user's tenant."""
    with _handle_domain_errors():
        sensor = service.create_sensor(tenant_id, body.model_dump())
    return ApiResponse(
        status="ok",
        message="Sensor created successfully",
        data=SensorResponse.model_validate(sensor).model_dump(mode="json"),
    )


@router.get("/{sensor_id}", response_model=ApiResponse)
async def get_sensor(
    sensor_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: SensorService = Depends(_sensor_service),
) -> ApiResponse:
    """Retrieve a single sensor by its ID."""
    with _handle_domain_errors():
        sensor = service.get_sensor(sensor_id)
    return ApiResponse(
        status="ok",
        data=SensorResponse.model_validate(sensor).model_dump(mode="json"),
    )


@router.put("/{sensor_id}", response_model=ApiResponse)
async def update_sensor(
    sensor_id: UUID,
    body: SensorUpdate,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: SensorService = Depends(_sensor_service),
) -> ApiResponse:
    """Update an existing sensor (partial update supported)."""
    update_data = body.model_dump(exclude_unset=True)
    with _handle_domain_errors():
        sensor = service.update_sensor(sensor_id, update_data)
    return ApiResponse(
        status="ok",
        message="Sensor updated successfully",
        data=SensorResponse.model_validate(sensor).model_dump(mode="json"),
    )


@router.delete("/{sensor_id}", response_model=ApiResponse)
async def delete_sensor(
    sensor_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: SensorService = Depends(_sensor_service),
) -> ApiResponse:
    """Delete a sensor by its ID."""
    with _handle_domain_errors():
        service.delete_sensor(sensor_id)
    return ApiResponse(
        status="ok",
        message="Sensor deleted successfully",
    )


# ------------------------------------------------------------------
# Readings
# ------------------------------------------------------------------


@router.get("/{sensor_id}/readings", response_model=ApiResponse)
async def get_readings(
    sensor_id: UUID,
    limit: int = Query(default=100, ge=1, le=1000, description="Max readings"),
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: SensorService = Depends(_sensor_service),
) -> ApiResponse:
    """Return the most recent readings for a sensor."""
    with _handle_domain_errors():
        readings = service.get_readings(sensor_id, limit=limit)
    return ApiResponse(
        status="ok",
        data=[ReadingResponse.model_validate(r).model_dump(mode="json") for r in readings],
    )


@router.get("/{sensor_id}/readings/latest", response_model=ApiResponse)
async def get_latest_reading(
    sensor_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: SensorService = Depends(_sensor_service),
) -> ApiResponse:
    """Return the single most recent reading for a sensor."""
    with _handle_domain_errors():
        reading = service.get_latest_reading(sensor_id)
    data = ReadingResponse.model_validate(reading).model_dump(mode="json") if reading else None
    return ApiResponse(status="ok", data=data)


@router.post("/ingest", response_model=ApiResponse, status_code=201)
async def ingest_readings(
    body: ReadingBatchRequest,
    tenant_id: UUID = Depends(_get_tenant_id),
    service: SensorService = Depends(_sensor_service),
) -> ApiResponse:
    """Bulk-ingest sensor readings.

    Accepts a batch of readings and updates each affected sensor's
    ``last_reading_at`` timestamp.
    """
    readings_data = [r.model_dump() for r in body.readings]
    with _handle_domain_errors():
        count = service.ingest_readings(tenant_id, readings_data)
    return ApiResponse(
        status="ok",
        message=f"{count} readings ingested successfully",
        data={"count": count},
    )
