import logging
from typing import List

logger = logging.getLogger(__name__)

KNOWN_I2C_DEVICES = {
    0x23: "BH1750",
    0x48: "ADS1115",
}


class SensorDiscovery:
    """Auto-discovers attached sensors via 1-Wire, I2C, etc."""

    def __init__(self):
        self.discovered_sensors = {}

    def scan_onewire(self) -> List[dict]:
        devices = []
        try:
            import os

            base = "/sys/bus/w1/devices/"
            if os.path.isdir(base):
                for entry in os.listdir(base):
                    if entry.startswith("28-"):
                        devices.append({"device_id": entry, "type": "DS18B20"})
        except Exception as e:
            logger.debug("1-Wire scan skipped: %s", e)
        return devices

    def scan_i2c(self) -> List[dict]:
        devices = []
        try:
            from smbus2 import SMBus  # type: ignore

            bus = SMBus(1)
            for addr, sensor_type in KNOWN_I2C_DEVICES.items():
                try:
                    bus.read_byte(addr)
                    devices.append({"device_id": f"i2c-0x{addr:02x}", "type": sensor_type})
                except OSError:
                    pass
            bus.close()
        except (ImportError, FileNotFoundError, OSError) as e:
            logger.debug("I2C scan skipped: %s", e)
        return devices

    def discover_all(self) -> List[dict]:
        all_devices = []
        all_devices.extend(self.scan_onewire())
        all_devices.extend(self.scan_i2c())

        for dev in all_devices:
            self.discovered_sensors[dev["device_id"]] = dev

        logger.info("Discovered %d sensor(s)", len(all_devices))
        return all_devices
