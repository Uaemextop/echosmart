"""Modelo de sensor."""

from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.database import Base

import uuid


class Sensor(Base):
    """Modelo ORM para sensores."""

    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gateway_id = Column(UUID(as_uuid=True), ForeignKey("gateways.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # temperature, humidity, light, soil, co2
    unit = Column(String(20), nullable=False)  # °C, %, lux, ppm
    min_value = Column(Float)
    max_value = Column(Float)
    is_online = Column(Boolean, default=False)
    last_reading_at = Column(DateTime(timezone=True))
    location = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
