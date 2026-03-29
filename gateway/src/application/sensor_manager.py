"""Sensor manager — Orchestrates sensor polling with circuit breaker.

This is a pure application-layer use case that depends only on domain
interfaces (BaseSensorDriver, IStorageRepository), never on concrete
infrastructure classes.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Callable

from gateway.src.domain.constants import (
    CIRCUIT_BREAKER_FAIL_THRESHOLD,
    CIRCUIT_BREAKER_RECOVERY_S,
)
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver
from gateway.src.domain.interfaces.storage import IStorageRepository

logger = logging.getLogger(__name__)


@dataclass
class _CircuitState:
    """Per-sensor circuit breaker state."""

    consecutive_failures: int = 0
    tripped: bool = False
    tripped_at: float = 0.0


@dataclass
class SensorMetrics:
    """Observable metrics for the sensor manager."""

    total_reads: int = 0
    total_errors: int = 0
    readings_per_sensor: dict[str, int] = field(default_factory=dict)
    errors_per_sensor: dict[str, int] = field(default_factory=dict)


class SensorManager:
    """Orchestrates sensor polling with circuit breaker and storage.

    Args:
        storage: Repository for persisting readings.
        polling_interval: Seconds between polling cycles.
        on_reading: Optional callback invoked after each successful reading.
        on_error: Optional callback invoked after a read failure.
    """

    def __init__(
        self,
        storage: IStorageRepository | None = None,
        polling_interval: int = 60,
        on_reading: Callable[[SensorReading], None] | None = None,
        on_error: Callable[[str, Exception], None] | None = None,
    ) -> None:
        self._sensors: dict[str, BaseSensorDriver] = {}
        self._circuit: dict[str, _CircuitState] = {}
        self._storage = storage
        self._polling_interval = polling_interval
        self._on_reading = on_reading
        self._on_error = on_error
        self._running = False
        self.metrics = SensorMetrics()
        logger.info("SensorManager initialized (interval=%ds).", polling_interval)

    @property
    def polling_interval(self) -> int:
        return self._polling_interval

    @property
    def sensor_count(self) -> int:
        return len(self._sensors)

    # ------------------------------------------------------------------
    # Sensor registration
    # ------------------------------------------------------------------

    def register(self, driver: BaseSensorDriver) -> None:
        """Register a sensor driver for polling."""
        sid = driver.sensor_id
        self._sensors[sid] = driver
        self._circuit[sid] = _CircuitState()
        self.metrics.readings_per_sensor[sid] = 0
        self.metrics.errors_per_sensor[sid] = 0
        logger.info("Registered sensor: %r", driver)

    def unregister(self, sensor_id: str) -> None:
        """Remove a sensor from polling and shut it down."""
        driver = self._sensors.pop(sensor_id, None)
        self._circuit.pop(sensor_id, None)
        if driver:
            driver.shutdown()
            logger.info("Unregistered sensor: %s", sensor_id)

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    def read_all(self) -> list[SensorReading]:
        """Read all registered sensors once, respecting circuit breakers."""
        readings: list[SensorReading] = []
        for sid, driver in list(self._sensors.items()):
            cb = self._circuit[sid]

            if cb.tripped:
                if time.monotonic() - cb.tripped_at >= CIRCUIT_BREAKER_RECOVERY_S:
                    logger.info("Circuit breaker reset for %s — retrying.", sid)
                    cb.tripped = False
                    cb.consecutive_failures = 0
                else:
                    continue

            try:
                reading = driver.read()
                readings.append(reading)
                cb.consecutive_failures = 0
                self.metrics.total_reads += 1
                self.metrics.readings_per_sensor[sid] = (
                    self.metrics.readings_per_sensor.get(sid, 0) + 1
                )

                if self._storage and reading.is_valid:
                    self._storage.save_reading(reading)
                if self._on_reading:
                    self._on_reading(reading)

            except Exception as exc:
                cb.consecutive_failures += 1
                self.metrics.total_errors += 1
                self.metrics.errors_per_sensor[sid] = (
                    self.metrics.errors_per_sensor.get(sid, 0) + 1
                )
                logger.error("Error reading %s: %s", sid, exc)

                if cb.consecutive_failures >= CIRCUIT_BREAKER_FAIL_THRESHOLD:
                    cb.tripped = True
                    cb.tripped_at = time.monotonic()
                    logger.warning(
                        "Circuit breaker TRIPPED for %s after %d failures.",
                        sid,
                        cb.consecutive_failures,
                    )

                if self._on_error:
                    self._on_error(sid, exc)

        return readings

    def initialize_all(self) -> None:
        """Initialize all registered sensor drivers."""
        for sid, driver in self._sensors.items():
            try:
                driver.initialize()
            except Exception as exc:
                logger.error("Failed to initialize %s: %s", sid, exc)

    def shutdown_all(self) -> None:
        """Gracefully shut down all sensor drivers."""
        for sid, driver in self._sensors.items():
            try:
                driver.shutdown()
            except Exception as exc:
                logger.error("Error shutting down %s: %s", sid, exc)
        logger.info("All sensors shut down.")
