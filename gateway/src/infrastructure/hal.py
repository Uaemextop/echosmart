"""Hardware Abstraction Layer — Interface + simulation implementation.

The HAL abstracts all hardware bus access so that the gateway can run
entirely in simulation mode during development.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class IHardwareInterface(ABC):
    """Abstract hardware interface — contract for HAL implementations."""

    @abstractmethod
    def read_gpio(self, pin: int) -> int:
        """Read the digital value of a GPIO pin."""

    @abstractmethod
    def read_i2c(self, address: int, register: int, length: int = 1) -> bytes:
        """Read *length* bytes from an I2C device."""

    @abstractmethod
    def read_1wire(self, device_id: str) -> str:
        """Read raw data from a 1-Wire device."""

    @abstractmethod
    def read_uart(self, port: str, length: int = 9, baudrate: int = 9600) -> bytes:
        """Read *length* bytes from a UART port."""

    @abstractmethod
    def scan_i2c(self) -> list[int]:
        """Scan the I2C bus and return detected device addresses."""

    @abstractmethod
    def list_1wire_devices(self) -> list[str]:
        """List device IDs on the 1-Wire bus."""


class SimulatedHAL(IHardwareInterface):
    """HAL that returns stub data for development without hardware."""

    def __init__(self) -> None:
        logger.info("SimulatedHAL initialized — no real hardware access.")

    def read_gpio(self, pin: int) -> int:
        return 0

    def read_i2c(self, address: int, register: int, length: int = 1) -> bytes:
        return bytes(length)

    def read_1wire(self, device_id: str) -> str:
        return ""

    def read_uart(self, port: str, length: int = 9, baudrate: int = 9600) -> bytes:
        return bytes(length)

    def scan_i2c(self) -> list[int]:
        return [0x23, 0x48]  # BH1750 + ADS1115 default addresses

    def list_1wire_devices(self) -> list[str]:
        return ["28-000000000001"]


class RaspberryPiHAL(IHardwareInterface):
    """HAL for real Raspberry Pi hardware — implemented in Phase 8."""

    def __init__(self) -> None:
        logger.info("RaspberryPiHAL initialized — real hardware mode.")
        # TODO: Phase 8 — import RPi.GPIO, smbus2, etc.

    def read_gpio(self, pin: int) -> int:
        raise NotImplementedError("GPIO reads not yet implemented (Phase 8)")

    def read_i2c(self, address: int, register: int, length: int = 1) -> bytes:
        raise NotImplementedError("I2C reads not yet implemented (Phase 8)")

    def read_1wire(self, device_id: str) -> str:
        raise NotImplementedError("1-Wire reads not yet implemented (Phase 8)")

    def read_uart(self, port: str, length: int = 9, baudrate: int = 9600) -> bytes:
        raise NotImplementedError("UART reads not yet implemented (Phase 8)")

    def scan_i2c(self) -> list[int]:
        raise NotImplementedError("I2C scan not yet implemented (Phase 8)")

    def list_1wire_devices(self) -> list[str]:
        raise NotImplementedError("1-Wire scan not yet implemented (Phase 8)")
