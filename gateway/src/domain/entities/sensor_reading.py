"""Sensor reading entity — Pure domain object."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class SensorReading:
    """Immutable value object representing a single sensor measurement.

    Attributes:
        sensor_id: Unique identifier of the sensor that produced the reading.
        sensor_type: Category of measurement (temperature, humidity, etc.).
        value: Measured numeric value.
        unit: Unit of measurement (°C, %, lux, ppm).
        timestamp: UTC datetime when the reading was taken.
        is_valid: Whether the reading passed driver-level validation.
        metadata: Optional extra data (e.g. secondary readings from DHT22).
    """

    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_valid: bool = True
    metadata: dict | None = None

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary for JSON / storage."""
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "is_valid": self.is_valid,
            "metadata": self.metadata,
        }
