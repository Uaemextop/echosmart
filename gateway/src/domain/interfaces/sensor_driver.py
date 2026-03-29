"""Base sensor driver interface — Contract for all sensor implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from gateway.src.domain.entities.sensor_reading import SensorReading


class BaseSensorDriver(ABC):
    """Abstract base class that every sensor driver must implement.

    Follows the Liskov Substitution Principle: any driver can be swapped
    for another without breaking the SensorManager.

    Attributes:
        sensor_id: Unique identifier for this sensor instance.
        sensor_type: Category of measurement (temperature, humidity, etc.).
        protocol: Communication protocol (1-wire, gpio, i2c, uart).
        is_simulation: Whether the driver is running in simulation mode.
    """

    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        protocol: str,
        simulation: bool = True,
    ) -> None:
        self._sensor_id = sensor_id
        self._sensor_type = sensor_type
        self._protocol = protocol
        self._is_simulation = simulation
        self._initialized = False

    @property
    def sensor_id(self) -> str:
        return self._sensor_id

    @property
    def sensor_type(self) -> str:
        return self._sensor_type

    @property
    def protocol(self) -> str:
        return self._protocol

    @property
    def is_simulation(self) -> bool:
        return self._is_simulation

    @property
    def initialized(self) -> bool:
        return self._initialized

    # ------------------------------------------------------------------
    # Abstract methods — must be implemented by every driver
    # ------------------------------------------------------------------

    @abstractmethod
    def read(self) -> SensorReading:
        """Take a measurement and return a validated SensorReading."""

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the sensor hardware / simulation. Return True on success."""

    @abstractmethod
    def shutdown(self) -> None:
        """Release hardware resources cleanly."""

    @abstractmethod
    def is_healthy(self) -> bool:
        """Return True if the sensor can produce readings."""

    # ------------------------------------------------------------------
    # Optional hooks with default implementations
    # ------------------------------------------------------------------

    def calibrate(self, reference_value: float) -> None:
        """Calibrate the sensor against a known reference value.

        Override in drivers that support calibration (e.g. SoilMoisture).
        """

    def get_info(self) -> dict:
        """Return metadata about the sensor for diagnostics."""
        return {
            "sensor_id": self._sensor_id,
            "sensor_type": self._sensor_type,
            "protocol": self._protocol,
            "simulation": self._is_simulation,
            "initialized": self._initialized,
            "healthy": self.is_healthy(),
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self._sensor_id!r}, "
            f"type={self._sensor_type!r}, "
            f"sim={self._is_simulation})"
        )
