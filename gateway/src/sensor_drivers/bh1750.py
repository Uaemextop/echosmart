import random
import logging
from typing import Optional

from src.sensor_drivers.base import SensorDriver
from src.hal import I2CManager

logger = logging.getLogger(__name__)

MIN_LUX = 0
MAX_LUX = 65535
BH1750_ADDRESS = 0x23
BH1750_CONTINUOUS_HIGH_RES = 0x10


class BH1750Driver(SensorDriver):
    """BH1750 digital ambient light sensor driver (I2C)."""

    def __init__(self, sensor_id: str, config: dict = None):
        super().__init__(sensor_id, config)
        self.address = self.config.get("address", BH1750_ADDRESS)
        self.simulation = self.config.get("simulation", True)
        self._i2c = None

    def initialize(self) -> bool:
        if not self.simulation:
            bus = self.config.get("i2c_bus", 1)
            self._i2c = I2CManager(bus)
            self._i2c.write(self.address, bytes([BH1750_CONTINUOUS_HIGH_RES]))
        logger.info("BH1750 %s initialised at 0x%02x (simulation=%s)", self.sensor_id, self.address, self.simulation)
        return True

    def read(self) -> Optional[dict]:
        try:
            if self.simulation:
                value = round(random.uniform(100.0, 2000.0), 1)
            else:
                data = self._i2c.read(self.address, 2)
                value = round((data[0] << 8 | data[1]) / 1.2, 1)

            quality = "good" if self.validate_reading(value) else "warning"
            self._update_state(value)
            return {"value": value, "unit": "lux", "quality": quality}
        except Exception as e:
            logger.error("BH1750 read error: %s", e)
            return {"value": 0.0, "unit": "lux", "quality": "error"}

    def validate_reading(self, value: float) -> bool:
        return MIN_LUX <= value <= MAX_LUX

    def cleanup(self):
        if self._i2c:
            self._i2c.close()
