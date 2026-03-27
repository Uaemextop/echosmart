"""Modelo de gateway."""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.database import Base

import uuid


class Gateway(Base):
    """Modelo ORM para gateways (Raspberry Pi)."""

    __tablename__ = "gateways"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    api_key = Column(String(255), unique=True, nullable=False)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True))
    firmware_version = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
