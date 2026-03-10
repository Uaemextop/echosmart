from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.middleware.auth import get_current_user
from src.models.gateway import Gateway
from src.models.sensor import Sensor
from src.models.user import User
from src.schemas.gateway import (
    GatewayCreate,
    GatewayUpdate,
    GatewayResponse,
    GatewayDetailResponse,
    ReadingsIngest,
    ReadingsIngestResponse,
    PaginatedGateways,
)
from src.services.sync_service import sync_gateway

router = APIRouter(prefix="/gateways", tags=["gateways"])


@router.get("/", response_model=PaginatedGateways)
def list_gateways(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway_status: str | None = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Gateway).filter(Gateway.tenant_id == current_user.tenant_id)
    if gateway_status:
        query = query.filter(Gateway.status == gateway_status)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return PaginatedGateways(items=items, total=total, page=page, limit=limit)


@router.post("/", response_model=GatewayResponse, status_code=status.HTTP_201_CREATED)
def create_gateway(
    body: GatewayCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    existing = db.query(Gateway).filter(Gateway.id == body.gateway_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Gateway ID already exists"
        )
    gateway = Gateway(
        id=body.gateway_id,
        tenant_id=current_user.tenant_id,
        name=body.name,
        location=body.location,
        description=body.description,
    )
    db.add(gateway)
    db.commit()
    db.refresh(gateway)
    return gateway


@router.get("/{gateway_id}", response_model=GatewayDetailResponse)
def get_gateway(
    gateway_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    gateway = (
        db.query(Gateway)
        .filter(Gateway.id == gateway_id, Gateway.tenant_id == current_user.tenant_id)
        .first()
    )
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway not found")
    sensors_count = (
        db.query(Sensor).filter(Sensor.gateway_id == gateway_id).count()
    )
    response = GatewayDetailResponse.model_validate(gateway)
    response.sensors_count = sensors_count
    return response


@router.put("/{gateway_id}", response_model=GatewayResponse)
def update_gateway(
    gateway_id: str,
    body: GatewayUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    gateway = (
        db.query(Gateway)
        .filter(Gateway.id == gateway_id, Gateway.tenant_id == current_user.tenant_id)
        .first()
    )
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway not found")
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(gateway, key, value)
    db.commit()
    db.refresh(gateway)
    return gateway


@router.delete("/{gateway_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gateway(
    gateway_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    gateway = (
        db.query(Gateway)
        .filter(Gateway.id == gateway_id, Gateway.tenant_id == current_user.tenant_id)
        .first()
    )
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway not found")
    db.delete(gateway)
    db.commit()
    return None


@router.post(
    "/{gateway_id}/readings", response_model=ReadingsIngestResponse
)
def ingest_readings(
    gateway_id: str,
    body: ReadingsIngest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    gateway = (
        db.query(Gateway)
        .filter(Gateway.id == gateway_id, Gateway.tenant_id == current_user.tenant_id)
        .first()
    )
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway not found")

    sync_gateway(db, gateway_id, current_user.tenant_id)
    ingested = len(body.readings)
    return ReadingsIngestResponse(status="ok", readings_ingested=ingested)
