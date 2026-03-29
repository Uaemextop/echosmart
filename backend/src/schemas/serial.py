"""Schemas Pydantic para números de serie."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SerialBase(BaseModel):
    """Base schema para serial."""

    code: str


class SerialCreate(SerialBase):
    """Schema para crear serial."""

    batch_id: Optional[str] = None


class SerialResponse(SerialBase):
    """Schema de respuesta con info de serial."""

    id: str
    status: str
    user_id: Optional[str] = None
    echopy_id: Optional[str] = None
    generated_at: Optional[datetime] = None
    registered_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SerialBatchRequest(BaseModel):
    """Request para generar batch de seriales."""

    quantity: int = 10
    prefix: str = "ES"


class SerialBatchResponse(BaseModel):
    """Response de generación de batch."""

    batch_id: str
    generated: int
    serials: list[str]
