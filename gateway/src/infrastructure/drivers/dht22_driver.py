"""DHT22 temperature + humidity sensor driver (GPIO protocol).

Supports simulation mode with rate limiting, validation, and retry logic.
"""

from __future__ import annotations

import logging
import random
import time

from gateway.src.domain.constants import (
    DHT22_MIN_READ_INTERVAL_S,
    SENSOR_RANGES,
    SIMULATION_RANGES,
)
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver

logger = logging.getLogger(__name__)

_TEMP_RANGE = SENSOR_RANGES["temperature"]
_HUM_RANGE = SENSOR_RANGES["humidity"]
_SIM_TEMP = SIMULATION_RANGES["temperature"]
_SIM_HUM = SIMULATION_RANGES["humidity"]
_MAX_RETRIES = 3


class DHT22Driver(BaseSensorDriver):
    """Driver for Aosong DHT22 / AM2302 temperature + humidity sensor.

    The DHT22 has a hardware limitation of one read every 2 seconds.

    Args:
        sensor_id: Unique identifier for this sensor instance.
        pin: GPIO pin number.
        simulation: If True, generate realistic random data.
    """

    def __init__(
        self,
        sensor_id: str = "dht22-01",
        pin: int = 17,
        simulation: bool = True,
    ) -> None:
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="temperature_humidity",
            protocol="gpio",
            simulation=simulation,
        )
        self._pin = pin
        self._last_read_time: float = 0.0

    def initialize(self) -> bool:
        if self._is_simulation:
            logger.info("%s initialized in simulation mode (pin=%d).", self._sensor_id, self._pin)
        else:
            logger.info("%s initializing on GPIO %d.", self._sensor_id, self._pin)
            # TODO: Phase 8 — initialize adafruit_dht
        self._initialized = True
        return True

    def read(self) -> SensorReading:
        self._enforce_rate_limit()

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                temperature, humidity = self._read_raw()
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
                        unit=_TEMP_RANGE["unit"],
                        is_valid=False,
                    )
                time.sleep(DHT22_MIN_READ_INTERVAL_S)

        temp_valid = _TEMP_RANGE["min"] <= temperature <= _TEMP_RANGE["max"]
        hum_valid = _HUM_RANGE["min"] < humidity <= _HUM_RANGE["max"]
        is_valid = temp_valid and hum_valid

        if not is_valid:
            logger.warning(
                "%s invalid reading: temp=%.1f, hum=%.1f",
                self._sensor_id,
                temperature,
                humidity,
            )

        self._last_read_time = time.monotonic()

        return SensorReading(
            sensor_id=self._sensor_id,
            sensor_type=self._sensor_type,
            value=round(temperature, 1),
            unit=_TEMP_RANGE["unit"],
            is_valid=is_valid,
            metadata={"humidity": round(humidity, 1), "humidity_unit": _HUM_RANGE["unit"]},
        )

    def shutdown(self) -> None:
        logger.info("%s shutting down.", self._sensor_id)
        self._initialized = False

    def is_healthy(self) -> bool:
        return self._initialized

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _read_raw(self) -> tuple[float, float]:
        if self._is_simulation:
            temp = round(random.uniform(_SIM_TEMP["min"], _SIM_TEMP["max"]), 1)
            hum = round(random.uniform(_SIM_HUM["min"], _SIM_HUM["max"]), 1)
            return temp, hum
        # TODO: Phase 8 — read from adafruit_dht
        raise RuntimeError("Hardware reads not implemented")

    def _enforce_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_read_time
        if elapsed < DHT22_MIN_READ_INTERVAL_S:
            wait = DHT22_MIN_READ_INTERVAL_S - elapsed
            time.sleep(wait)
