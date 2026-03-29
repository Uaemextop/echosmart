"""Sensor discovery service — Scans hardware buses for connected sensors."""

from __future__ import annotations

import logging

from gateway.src.infrastructure.hal import IHardwareInterface

logger = logging.getLogger(__name__)

# Known I2C addresses for supported sensors
_I2C_KNOWN_DEVICES: dict[int, str] = {
    0x23: "bh1750",
    0x5C: "bh1750",
    0x48: "soil_moisture",
}


class SensorDiscovery:
    """Discovers sensors connected to the gateway hardware buses.

    Args:
        hal: Hardware abstraction layer for bus scanning.
    """

    def __init__(self, hal: IHardwareInterface) -> None:
        self._hal = hal

    def scan_all(self) -> list[dict]:
        """Scan all buses and return a list of discovered sensor configs."""
        discovered: list[dict] = []
        discovered.extend(self._scan_i2c())
        discovered.extend(self._scan_1wire())
        logger.info("Discovery complete: found %d sensor(s).", len(discovered))
        return discovered

    def _scan_i2c(self) -> list[dict]:
        try:
            addresses = self._hal.scan_i2c()
        except Exception as exc:
            logger.warning("I2C scan failed: %s", exc)
            return []

        results: list[dict] = []
        for addr in addresses:
            sensor_type = _I2C_KNOWN_DEVICES.get(addr)
            if sensor_type:
                results.append({"type": sensor_type, "address": addr, "bus": "i2c"})
                logger.info("I2C: found %s at 0x%02X.", sensor_type, addr)
        return results

    def _scan_1wire(self) -> list[dict]:
        try:
            devices = self._hal.list_1wire_devices()
        except Exception as exc:
            logger.warning("1-Wire scan failed: %s", exc)
            return []

        results: list[dict] = []
        for dev_id in devices:
            if dev_id.startswith("28-"):
                results.append({"type": "ds18b20", "device_id": dev_id, "bus": "1-wire"})
                logger.info("1-Wire: found DS18B20 %s.", dev_id)
        return results
