import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.middleware.auth import get_current_user
from src.models.gateway import Gateway
from src.models.sensor import Sensor
from src.models.user import User
from src.schemas.sensor import SensorCreate, SensorUpdate, SensorResponse, SensorReading
from src.services.sensor_service import get_sensors_for_tenant

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("/", response_model=list[SensorResponse])
def list_sensors(
    gateway_id: str | None = None,
    sensor_type: str | None = Query(None, alias="type"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_sensors_for_tenant(
        db,
        tenant_id=current_user.tenant_id,
        gateway_id=gateway_id,
        sensor_type=sensor_type,
        limit=limit,
        offset=offset,
    )


@router.post("/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
def create_sensor(
    body: SensorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    gateway = (
        db.query(Gateway)
        .filter(
            Gateway.id == body.gateway_id,
            Gateway.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not gateway:
        raise HTTPException(status_code=404, detail="Gateway not found")

    sensor_id = body.sensor_id or str(uuid.uuid4())
    existing = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Sensor ID already exists"
        )

    sensor = Sensor(
        id=sensor_id,
        gateway_id=body.gateway_id,
        tenant_id=current_user.tenant_id,
        type=body.sensor_type,
        name=body.name,
        unit=body.unit,
        location=body.location,
        polling_interval=body.polling_interval,
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor


@router.get("/{sensor_id}", response_model=SensorResponse)
def get_sensor(
    sensor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sensor = (
        db.query(Sensor)
        .filter(Sensor.id == sensor_id, Sensor.tenant_id == current_user.tenant_id)
        .first()
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.get("/{sensor_id}/readings", response_model=list[SensorReading])
def get_sensor_readings(
    sensor_id: str,
    from_date: str | None = None,
    to_date: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sensor = (
        db.query(Sensor)
        .filter(Sensor.id == sensor_id, Sensor.tenant_id == current_user.tenant_id)
        .first()
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    # Readings would come from a time-series DB in production; return empty list
    return []


@router.put("/{sensor_id}", response_model=SensorResponse)
def update_sensor(
    sensor_id: str,
    body: SensorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    sensor = (
        db.query(Sensor)
        .filter(Sensor.id == sensor_id, Sensor.tenant_id == current_user.tenant_id)
        .first()
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sensor, key, value)
    db.commit()
    db.refresh(sensor)
    return sensor


@router.delete("/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor(
    sensor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    sensor = (
        db.query(Sensor)
        .filter(Sensor.id == sensor_id, Sensor.tenant_id == current_user.tenant_id)
        .first()
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    db.delete(sensor)
    db.commit()
    return None
