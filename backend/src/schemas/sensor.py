from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SensorCreate(BaseModel):
    sensor_id: Optional[str] = None
    gateway_id: str
    name: str
    sensor_type: str
    unit: str
    location: Optional[str] = None
    polling_interval: int = 60


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    unit: Optional[str] = None
    polling_interval: Optional[int] = None
    status: Optional[str] = None
    config: Optional[dict] = None


class SensorResponse(BaseModel):
    id: str
    gateway_id: str
    tenant_id: str
    type: str
    name: str
    location: Optional[str] = None
    unit: str
    polling_interval: int
    status: str
    config: Optional[dict] = None
    last_reading_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SensorReading(BaseModel):
    sensor_id: str
    value: float
    unit: str
    timestamp: datetime
