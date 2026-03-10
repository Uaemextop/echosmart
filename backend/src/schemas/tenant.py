from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    max_gateways: int
    max_users: int
    branding: Optional[dict] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    branding: Optional[dict] = None
