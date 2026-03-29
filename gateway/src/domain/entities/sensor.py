"""Entidades del dominio de sensores."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _utcnow() -> datetime:
    """Retorna la hora UTC actual como datetime aware (compatible Python 3.11+)."""
    return datetime.now(timezone.utc)


@dataclass
class SensorReading:
    """Lectura de un sensor en un momento dado."""

    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=_utcnow)
    error: Optional[str] = None

    @classmethod
    def empty(cls, sensor_id: str, sensor_type: str, unit: str, error: str) -> "SensorReading":
        """Crear lectura vacía indicando error."""
        return cls(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            value=0.0,
            unit=unit,
            error=error,
        )


@dataclass
class SensorMetadata:
    """Metadatos de configuración de un sensor."""

    sensor_id: str
    name: str
    sensor_type: str
    driver_type: str
    location: str
    unit: str
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None
    enabled: bool = True
