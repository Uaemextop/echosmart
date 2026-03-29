"""DS18B20 temperature sensor driver (1-Wire protocol).

Supports simulation mode and includes validation, outlier filtering,
and retry logic.  Hardware reads are a TODO for Phase 8.
"""

from __future__ import annotations

import logging
import random
import time

from gateway.src.domain.constants import (
    DS18B20_MAX_DELTA_PER_SAMPLE,
    DS18B20_MIN_READ_INTERVAL_S,
    SENSOR_RANGES,
    SIMULATION_RANGES,
)
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver

logger = logging.getLogger(__name__)

_RANGE = SENSOR_RANGES["temperature"]
_SIM = SIMULATION_RANGES["temperature"]
_MAX_RETRIES = 3


class DS18B20Driver(BaseSensorDriver):
    """Driver for Dallas DS18B20 temperature sensor via 1-Wire bus.

    Args:
        sensor_id: Unique identifier for this sensor instance.
        device_id: 1-Wire device address (e.g. ``28-xxxxxxxxxxxx``).
        simulation: If True, generate realistic random data.
        resolution_bits: Measurement resolution (9-12 bits).
    """

    def __init__(
        self,
        sensor_id: str = "ds18b20-01",
        device_id: str | None = None,
        simulation: bool = True,
        resolution_bits: int = 12,
    ) -> None:
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="temperature",
            protocol="1-wire",
            simulation=simulation,
        )
        self._device_id = device_id
        self._resolution_bits = max(9, min(12, resolution_bits))
        self._last_value: float | None = None
        self._last_read_time: float = 0.0

    # ------------------------------------------------------------------
    # BaseSensorDriver implementation
    # ------------------------------------------------------------------

    def initialize(self) -> bool:
        if self._is_simulation:
            logger.info("%s initialized in simulation mode.", self._sensor_id)
        else:
            logger.info(
                "%s initializing on 1-Wire bus (device=%s, res=%d-bit).",
                self._sensor_id,
                self._device_id,
                self._resolution_bits,
            )
            # TODO: Phase 8 — verify device file exists in /sys/bus/w1/devices/
        self._initialized = True
        return True

    def read(self) -> SensorReading:
        self._enforce_rate_limit()

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                raw_value = self._read_raw()
                break
            except RuntimeError as exc:
                logger.warning(
                    "%s read attempt %d/%d failed: %s",
                    self._sensor_id,
                    attempt,
                    _MAX_RETRIES,
                    exc,
                )
                if attempt == _MAX_RETRIES:
                    return SensorReading(
                        sensor_id=self._sensor_id,
                        sensor_type=self._sensor_type,
                        value=0.0,
                        unit=_RANGE["unit"],
                        is_valid=False,
                    )
                time.sleep(0.1 * attempt)

        is_valid = self._validate(raw_value)
        self._last_value = raw_value if is_valid else self._last_value
        self._last_read_time = time.monotonic()

        return SensorReading(
            sensor_id=self._sensor_id,
            sensor_type=self._sensor_type,
            value=round(raw_value, 2),
            unit=_RANGE["unit"],
            is_valid=is_valid,
        )

    def shutdown(self) -> None:
        logger.info("%s shutting down.", self._sensor_id)
        self._initialized = False

    def is_healthy(self) -> bool:
        return self._initialized

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_raw(self) -> float:
        if self._is_simulation:
            return round(random.uniform(_SIM["min"], _SIM["max"]), 2)
        # TODO: Phase 8 — read from /sys/bus/w1/devices/{device_id}/temperature
        raise RuntimeError("Hardware reads not implemented")

    def _validate(self, value: float) -> bool:
        if not (_RANGE["min"] <= value <= _RANGE["max"]):
            logger.warning(
                "%s value %.2f out of sensor range [%.1f, %.1f].",
                self._sensor_id,
                value,
                _RANGE["min"],
                _RANGE["max"],
            )
            return False

        if self._last_value is not None:
            delta = abs(value - self._last_value)
            if delta > DS18B20_MAX_DELTA_PER_SAMPLE:
                logger.warning(
                    "%s outlier detected: delta=%.2f°C (max=%.1f).",
                    self._sensor_id,
                    delta,
                    DS18B20_MAX_DELTA_PER_SAMPLE,
                )
                return False

        return True

    def _enforce_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_read_time
        if elapsed < DS18B20_MIN_READ_INTERVAL_S:
            wait = DS18B20_MIN_READ_INTERVAL_S - elapsed
            time.sleep(wait)
