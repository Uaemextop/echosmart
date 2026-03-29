"""Soil moisture sensor driver (Capacitive sensor + ADS1115 ADC, I2C).

Supports simulation, calibration, channel selection, and median filtering.
"""

from __future__ import annotations

import logging
import random
import statistics

from gateway.src.domain.constants import SENSOR_RANGES, SIMULATION_RANGES
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver

logger = logging.getLogger(__name__)

_RANGE = SENSOR_RANGES["soil_moisture"]
_SIM = SIMULATION_RANGES["soil_moisture"]
_MEDIAN_SAMPLES = 5


class SoilMoistureDriver(BaseSensorDriver):
    """Driver for capacitive soil moisture sensor via ADS1115 ADC.

    Args:
        sensor_id: Unique identifier.
        channel: ADS1115 channel (0-3).
        simulation: If True, generate realistic random data.
        dry_value: ADC reading for completely dry soil (calibration).
        wet_value: ADC reading for saturated soil (calibration).
    """

    def __init__(
        self,
        sensor_id: str = "soil-01",
        channel: int = 0,
        simulation: bool = True,
        dry_value: int = 25000,
        wet_value: int = 12000,
    ) -> None:
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="soil_moisture",
            protocol="i2c",
            simulation=simulation,
        )
        self._channel = max(0, min(3, channel))
        self._dry_value = dry_value
        self._wet_value = wet_value

    def initialize(self) -> bool:
        if self._is_simulation:
            logger.info(
                "%s initialized in simulation mode (ch=%d).",
                self._sensor_id,
                self._channel,
            )
        else:
            logger.info(
                "%s initializing ADS1115 channel %d.",
                self._sensor_id,
                self._channel,
            )
            # TODO: Phase 8 — open I2C, configure ADS1115 gain
        self._initialized = True
        return True

    def read(self) -> SensorReading:
        raw_value = self._read_filtered()
        is_valid = _RANGE["min"] <= raw_value <= _RANGE["max"]

        if not is_valid:
            logger.warning(
                "%s value %.1f%% out of range [%.0f, %.0f].",
                self._sensor_id,
                raw_value,
                _RANGE["min"],
                _RANGE["max"],
            )

        return SensorReading(
            sensor_id=self._sensor_id,
            sensor_type=self._sensor_type,
            value=round(raw_value, 1),
            unit=_RANGE["unit"],
            is_valid=is_valid,
        )

    def shutdown(self) -> None:
        logger.info("%s shutting down.", self._sensor_id)
        self._initialized = False

    def is_healthy(self) -> bool:
        return self._initialized

    def calibrate(self, reference_value: float) -> None:
        """Not applicable — use auto_calibrate with dry/wet readings instead."""
        logger.info(
            "%s calibrate called with ref=%.1f (use auto_calibrate for soil sensors).",
            self._sensor_id,
            reference_value,
        )

    def auto_calibrate(self, dry_reading: int, wet_reading: int) -> None:
        """Set calibration values from known dry and wet ADC readings."""
        self._dry_value = dry_reading
        self._wet_value = wet_reading
        logger.info(
            "%s calibrated: dry=%d, wet=%d.",
            self._sensor_id,
            dry_reading,
            wet_reading,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _read_filtered(self) -> float:
        """Take median of multiple raw samples to reduce noise."""
        if self._is_simulation:
            samples = [random.uniform(_SIM["min"], _SIM["max"]) for _ in range(_MEDIAN_SAMPLES)]
        else:
            samples = [self._adc_to_percent(self._read_adc()) for _ in range(_MEDIAN_SAMPLES)]
        return statistics.median(samples)

    def _read_adc(self) -> int:
        # TODO: Phase 8 — read ADS1115 channel
        raise RuntimeError("Hardware reads not implemented")

    def _adc_to_percent(self, raw: int) -> float:
        """Map an ADC value to a 0-100% moisture percentage."""
        span = self._dry_value - self._wet_value
        if span == 0:
            return 0.0
        pct = (self._dry_value - raw) / span * 100.0
        return max(0.0, min(100.0, pct))
