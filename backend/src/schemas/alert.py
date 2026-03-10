from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AlertRuleCreate(BaseModel):
    sensor_id: str
    name: str
    description: Optional[str] = None
    condition: str
    threshold: float
    threshold_max: Optional[float] = None
    severity: str
    cooldown_minutes: int = 30
    notification_channels: list[str] = ["email"]


class AlertRuleResponse(BaseModel):
    id: str
    tenant_id: str
    sensor_id: str
    name: str
    description: Optional[str] = None
    condition: str
    threshold: float
    threshold_max: Optional[float] = None
    severity: str
    cooldown_minutes: int
    notification_channels: list
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    id: str
    tenant_id: str
    rule_id: Optional[str] = None
    sensor_id: str
    severity: str
    message: str
    current_value: float
    threshold: float
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AcknowledgeRequest(BaseModel):
    notes: Optional[str] = None
