"""MH-Z19C CO₂ sensor driver (UART protocol).

Supports simulation, checksum validation, warm-up tracking, and retry.
"""

from __future__ import annotations

import logging
import random
import time

from gateway.src.domain.constants import (
    MHZ19C_UART_TIMEOUT_S,
    MHZ19C_WARMUP_TIME_S,
    SENSOR_RANGES,
    SIMULATION_RANGES,
)
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver

logger = logging.getLogger(__name__)

_RANGE = SENSOR_RANGES["co2"]
_SIM = SIMULATION_RANGES["co2"]
_MAX_RETRIES = 3

# MH-Z19C UART read command
_READ_CMD = bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])


class MHZ19CDriver(BaseSensorDriver):
    """Driver for Winsen MH-Z19C NDIR CO₂ sensor via UART.

    Args:
        sensor_id: Unique identifier.
        port: Serial port path (e.g. ``/dev/ttyS0``).
        simulation: If True, generate realistic random data.
    """

    def __init__(
        self,
        sensor_id: str = "mhz19c-01",
        port: str = "/dev/ttyS0",
        simulation: bool = True,
    ) -> None:
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="co2",
            protocol="uart",
            simulation=simulation,
        )
        self._port = port
        self._init_time: float | None = None
        self._timeout = MHZ19C_UART_TIMEOUT_S

    def initialize(self) -> bool:
        self._init_time = time.monotonic()
        if self._is_simulation:
            logger.info("%s initialized in simulation mode.", self._sensor_id)
        else:
            logger.info(
                "%s initializing UART on %s (9600 baud).",
                self._sensor_id,
                self._port,
            )
            # TODO: Phase 8 — open serial port
        self._initialized = True
        return True

    def read(self) -> SensorReading:
        if self._is_warming_up():
            remaining = MHZ19C_WARMUP_TIME_S - (time.monotonic() - self._init_time)
            logger.info(
                "%s still warming up (%.0fs remaining).",
                self._sensor_id,
                remaining,
            )
            return SensorReading(
                sensor_id=self._sensor_id,
                sensor_type=self._sensor_type,
                value=0.0,
                unit=_RANGE["unit"],
                is_valid=False,
                metadata={"warming_up": True},
            )

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
                time.sleep(0.5)

        is_valid = _RANGE["min"] <= raw_value <= _RANGE["max"]
        if not is_valid:
            logger.warning(
                "%s value %.0f ppm out of range [%.0f, %.0f].",
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
        logger.info("%s shutting down.", self._sensor_id)
        self._initialized = False
        # TODO: Phase 8 — close serial port

    def is_healthy(self) -> bool:
        return self._initialized

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _is_warming_up(self) -> bool:
        if self._is_simulation:
            return False
        if self._init_time is None:
            return True
        return (time.monotonic() - self._init_time) < MHZ19C_WARMUP_TIME_S

    def _read_raw(self) -> float:
        if self._is_simulation:
            return round(random.uniform(_SIM["min"], _SIM["max"]), 0)
        # TODO: Phase 8 — send _READ_CMD, parse response, validate checksum
        raise RuntimeError("Hardware reads not implemented")

    @staticmethod
    def _validate_checksum(response: bytes) -> bool:
        """Validate MH-Z19C response checksum (byte 8)."""
        if len(response) != 9 or response[0] != 0xFF:
            return False
        checksum = (~sum(response[1:8]) & 0xFF) + 1
        return checksum == response[8]

    @staticmethod
    def _parse_ppm(response: bytes) -> int:
        """Extract CO₂ ppm from a 9-byte MH-Z19C response."""
        return response[2] * 256 + response[3]
