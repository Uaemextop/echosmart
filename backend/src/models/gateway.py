"""Modelo de gateway (compatibilidad con EchoPy)."""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.database import Base

import enum
import uuid


class GatewayStatus(str, enum.Enum):
    """Estado del gateway."""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class Gateway(Base):
    """Modelo ORM para gateways (Raspberry Pi / EchoPy).

    Este modelo se conserva por compatibilidad. Los nuevos dispositivos
    se gestionan a través del modelo EchoPy.
    """

    __tablename__ = "gateways"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    serial_number = Column(String(20), unique=True, nullable=True, index=True)
    location = Column(String(255))
    api_key = Column(String(255), unique=True, nullable=False)
    status = Column(
        Enum(GatewayStatus),
        nullable=False,
        default=GatewayStatus.OFFLINE,
    )
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True))
    firmware_version = Column(String(50))
    ip_address = Column(String(45), nullable=True)
    mac_address = Column(String(17), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
