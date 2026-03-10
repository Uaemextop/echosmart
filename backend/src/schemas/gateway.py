from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GatewayCreate(BaseModel):
    gateway_id: str
    name: str
    location: Optional[str] = None
    description: Optional[str] = None


class GatewayUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    firmware_version: Optional[str] = None
    ip_address: Optional[str] = None
    config: Optional[dict] = None


class GatewayResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    status: str
    firmware_version: Optional[str] = None
    ip_address: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    config: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GatewayDetailResponse(GatewayResponse):
    sensors_count: int = 0


class ReadingItem(BaseModel):
    sensor_id: str
    value: float
    unit: str
    timestamp: Optional[str] = None


class ReadingsIngest(BaseModel):
    readings: list[ReadingItem]


class ReadingsIngestResponse(BaseModel):
    status: str = "ok"
    readings_ingested: int


class PaginatedGateways(BaseModel):
    items: list[GatewayResponse]
    total: int
    page: int
    limit: int
