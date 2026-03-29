"""BH1750 light sensor driver (I2C protocol).

Supports simulation mode with measurement modes and validation.
"""

from __future__ import annotations

import logging
import random
from enum import Enum

from gateway.src.domain.constants import SENSOR_RANGES, SIMULATION_RANGES
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver

logger = logging.getLogger(__name__)

_RANGE = SENSOR_RANGES["light"]
_SIM = SIMULATION_RANGES["light"]


class MeasurementMode(str, Enum):
    """BH1750 measurement modes."""

    CONTINUOUS_HIGH_RES = "continuous_high_res"
    CONTINUOUS_HIGH_RES2 = "continuous_high_res2"
    ONE_TIME = "one_time"


class BH1750Driver(BaseSensorDriver):
    """Driver for ROHM BH1750FVI ambient light sensor via I2C.

    Args:
        sensor_id: Unique identifier.
        address: I2C address (0x23 default, 0x5C alternative).
        simulation: If True, generate realistic random data.
        mode: Measurement mode.
    """

    def __init__(
        self,
        sensor_id: str = "bh1750-01",
        address: int = 0x23,
        simulation: bool = True,
        mode: MeasurementMode = MeasurementMode.CONTINUOUS_HIGH_RES,
    ) -> None:
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="light",
            protocol="i2c",
            simulation=simulation,
        )
        self._address = address
        self._mode = mode
        self._powered_on = False

    def initialize(self) -> bool:
        if self._is_simulation:
            logger.info(
                "%s initialized in simulation mode (addr=0x%02X).",
                self._sensor_id,
                self._address,
            )
        else:
            logger.info(
                "%s initializing I2C at 0x%02X, mode=%s.",
                self._sensor_id,
                self._address,
                self._mode.value,
            )
            # TODO: Phase 8 — open I2C bus, power on sensor
        self._powered_on = True
        self._initialized = True
        return True

    def read(self) -> SensorReading:
        raw_value = self._read_raw()
        is_valid = _RANGE["min"] <= raw_value <= _RANGE["max"]

        if not is_valid:
            logger.warning(
                "%s value %.0f lux out of range [%.0f, %.0f].",
                self._sensor_id,
                raw_value,
                _RANGE["min"],
                _RANGE["max"],
            )

        return SensorReading(
            sensor_id=self._sensor_id,
            sensor_type=self._sensor_type,
            value=round(raw_value, 0),
            unit=_RANGE["unit"],
            is_valid=is_valid,
        )

    def shutdown(self) -> None:
        self._powered_on = False
        self._initialized = False
        logger.info("%s shutting down.", self._sensor_id)

    def is_healthy(self) -> bool:
        return self._initialized and self._powered_on

    def set_mode(self, mode: MeasurementMode) -> None:
        """Change measurement mode at runtime."""
        self._mode = mode
        logger.info("%s mode changed to %s.", self._sensor_id, mode.value)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _read_raw(self) -> float:
        if self._is_simulation:
            return round(random.uniform(_SIM["min"], _SIM["max"]), 0)
        # TODO: Phase 8 — I2C read
        raise RuntimeError("Hardware reads not implemented")
