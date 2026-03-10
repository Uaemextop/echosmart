import random
import logging
from typing import Optional

from src.sensor_drivers.base import SensorDriver
from src.hal import OnewireManager

logger = logging.getLogger(__name__)

MIN_TEMP = -55.0
MAX_TEMP = 125.0


class DS18B20Driver(SensorDriver):
    """Dallas DS18B20 1-Wire temperature sensor driver."""

    def __init__(self, sensor_id: str, config: dict = None):
        super().__init__(sensor_id, config)
        self.device_id = self.config.get("device_id", sensor_id)
        self.simulation = self.config.get("simulation", True)
        self._onewire = None

    def initialize(self) -> bool:
        if not self.simulation:
            self._onewire = OnewireManager()
        logger.info("DS18B20 %s initialised (simulation=%s)", self.sensor_id, self.simulation)
        return True

    def read(self) -> Optional[dict]:
        try:
            if self.simulation:
                value = round(random.uniform(18.0, 30.0), 2)
            else:
                value = self._onewire.read_temperature(self.device_id)

            quality = "good" if self.validate_reading(value) else "warning"
            self._update_state(value)
            return {"value": value, "unit": "°C", "quality": quality}
        except Exception as e:
            logger.error("DS18B20 read error: %s", e)
            return {"value": 0.0, "unit": "°C", "quality": "error"}

    def validate_reading(self, value: float) -> bool:
        return MIN_TEMP <= value <= MAX_TEMP
