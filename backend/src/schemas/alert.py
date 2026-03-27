"""Esquemas Pydantic para alertas."""

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class AlertRuleCreate(BaseModel):
    """Esquema para crear una regla de alerta."""

    sensor_id: UUID
    rule_name: str
    condition: str  # gt, lt, eq, out_of_range
    threshold: float
    severity: str  # critical, high, medium, low


class AlertResponse(BaseModel):
    """Esquema de respuesta de alerta."""

    id: UUID
    sensor_id: UUID
    rule_name: str
    condition: str
    threshold: float
    severity: str
    is_active: bool
    acknowledged: bool
    triggered_at: datetime

    model_config = {"from_attributes": True}
