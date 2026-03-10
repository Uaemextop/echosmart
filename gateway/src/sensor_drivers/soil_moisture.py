import random
import logging
from typing import Optional

from src.sensor_drivers.base import SensorDriver
from src.hal import I2CManager

logger = logging.getLogger(__name__)

MIN_MOISTURE = 0.0
MAX_MOISTURE = 100.0
ADS1115_ADDRESS = 0x48


class SoilMoistureDriver(SensorDriver):
    """Soil moisture sensor via ADS1115 ADC (I2C)."""

    def __init__(self, sensor_id: str, config: dict = None):
        super().__init__(sensor_id, config)
        self.address = self.config.get("address", ADS1115_ADDRESS)
        self.channel = self.config.get("channel", 0)
        self.simulation = self.config.get("simulation", True)
        self._i2c = None

    def initialize(self) -> bool:
        if not self.simulation:
            bus = self.config.get("i2c_bus", 1)
            self._i2c = I2CManager(bus)
        logger.info(
            "SoilMoisture %s initialized on channel %d (simulation=%s)",
            self.sensor_id, self.channel, self.simulation,
        )
        return True

    def read(self) -> Optional[dict]:
        try:
            if self.simulation:
                value = round(random.uniform(20.0, 80.0), 1)
            else:
                raw = self._i2c.read(self.address, 2)
                raw_value = (raw[0] << 8 | raw[1])
                value = round((raw_value / 32767.0) * 100.0, 1)

            quality = "good" if self.validate_reading(value) else "warning"
            self._update_state(value)
            return {"value": value, "unit": "%", "quality": quality}
        except Exception as e:
            logger.error("SoilMoisture read error: %s", e)
            return {"value": 0.0, "unit": "%", "quality": "error"}

    def validate_reading(self, value: float) -> bool:
        return MIN_MOISTURE <= value <= MAX_MOISTURE

    def cleanup(self):
        if self._i2c:
            self._i2c.close()
