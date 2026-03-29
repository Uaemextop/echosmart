"""Modelo de número de serie para kits EchoPy."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.database import Base

import enum
import uuid


class SerialStatus(str, enum.Enum):
    """Estado de un número de serie."""

    AVAILABLE = "available"  # Generado, no usado
    REGISTERED = "registered"  # Vinculado a un usuario
    REVOKED = "revoked"  # Revocado por admin
    EXPIRED = "expired"  # Expirado


class Serial(Base):
    """Modelo ORM para números de serie de kits.

    Formato: ES-YYYYMM-XXXX (e.g., ES-202603-0001)
    - ES: prefijo EchoSmart
    - YYYYMM: año y mes de generación
    - XXXX: secuencial (extensible a 5 dígitos para alto volumen)
    """

    __tablename__ = "serials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)
    status = Column(
        Enum(SerialStatus),
        nullable=False,
        default=SerialStatus.AVAILABLE,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    echopy_id = Column(UUID(as_uuid=True), ForeignKey("echopys.id"), nullable=True)
    batch_id = Column(String(50), nullable=True)  # Identificador del lote de generación
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    registered_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String(500), nullable=True)  # Notas admin
