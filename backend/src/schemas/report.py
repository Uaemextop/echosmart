from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class ReportCreate(BaseModel):
    title: str
    date_from: date
    date_to: date
    sensors: list[str]
    format: str = "pdf"


class ReportResponse(BaseModel):
    id: str
    tenant_id: str
    requested_by: str
    title: str
    format: str
    status: str
    date_from: date
    date_to: date
    sensors: list
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReportGenerateResponse(BaseModel):
    report_id: str
    status: str
