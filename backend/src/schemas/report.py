"""Esquemas Pydantic para reportes."""

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ReportGenerate(BaseModel):
    """Esquema para generar un reporte."""

    title: str
    format: str  # pdf, excel
    period_start: datetime
    period_end: datetime
    sensor_ids: list[UUID] | None = None


class ReportResponse(BaseModel):
    """Esquema de respuesta de reporte."""

    id: UUID
    title: str
    format: str
    status: str
    file_url: str | None
    period_start: datetime
    period_end: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
