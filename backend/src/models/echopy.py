"""Modelo de dispositivo EchoPy (gateway Raspberry Pi)."""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.database import Base

import enum
import uuid


class EchoPyStatus(str, enum.Enum):
    """Estado de un dispositivo EchoPy."""

    PENDING = "pending"  # Esperando vinculación (first-boot)
    ACTIVE = "active"  # Vinculado y operativo
    SUSPENDED = "suspended"  # Servicio suspendido por admin
    MAINTENANCE = "maintenance"  # En mantenimiento
    OFFLINE = "offline"  # Desconectado


class EchoPy(Base):
    """Modelo ORM para dispositivos EchoPy (gateway Raspberry Pi).

    Un EchoPy es un Raspberry Pi pre-configurado con el software echosmart
    que se incluye en cada kit de invernadero inteligente.
    """

    __tablename__ = "echopys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    serial_number = Column(String(20), unique=True, nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)

    # Identificación del dispositivo
    hostname = Column(String(100), nullable=True)  # e.g., echopy-a1b2c3
    mac_address = Column(String(17), unique=True, nullable=True)  # e.g., AA:BB:CC:DD:EE:FF
    ip_address = Column(String(45), nullable=True)

    # Estado
    status = Column(
        Enum(EchoPyStatus),
        nullable=False,
        default=EchoPyStatus.PENDING,
    )
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)

    # Firmware y software
    firmware_version = Column(String(50), nullable=True)
    os_version = Column(String(100), nullable=True)

    # Ubicación / invernadero
    name = Column(String(255), nullable=True)  # Nombre dado por el usuario
    location = Column(String(255), nullable=True)
    greenhouse_name = Column(String(255), nullable=True)

    # BLE pairing
    ble_uuid = Column(String(36), nullable=True)  # UUID del servicio BLE

    # SSH remoto
    ssh_enabled = Column(Boolean, default=True)
    ssh_port = Column(String(5), default="22")

    # Metadatos
    bound_at = Column(DateTime(timezone=True), nullable=True)  # Cuando se vinculó al usuario
    suspended_at = Column(DateTime(timezone=True), nullable=True)
    suspension_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
