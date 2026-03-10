import random
import logging
from typing import Optional

from src.sensor_drivers.base import SensorDriver
from src.hal import GPIOManager

logger = logging.getLogger(__name__)

MIN_TEMP = -40.0
MAX_TEMP = 80.0
MIN_HUMIDITY = 0.0
MAX_HUMIDITY = 100.0


class DHT22Driver(SensorDriver):
    """DHT22 temperature and humidity sensor driver (GPIO)."""

    def __init__(self, sensor_id: str, config: dict = None):
        super().__init__(sensor_id, config)
        self.pin = self.config.get("pin", 4)
        self.simulation = self.config.get("simulation", True)
        self._gpio = None

    def initialize(self) -> bool:
        if not self.simulation:
            self._gpio = GPIOManager()
            self._gpio.setup_pin(self.pin, "input")
        logger.info("DHT22 %s initialised on pin %d (simulation=%s)", self.sensor_id, self.pin, self.simulation)
        return True

    def read(self) -> Optional[dict]:
        try:
            if self.simulation:
                temp = round(random.uniform(18.0, 35.0), 1)
                humidity = round(random.uniform(30.0, 80.0), 1)
            else:
                temp, humidity = self._read_hardware()

            temp_valid = self.validate_reading(temp)
            hum_valid = MIN_HUMIDITY <= humidity <= MAX_HUMIDITY
            quality = "good" if (temp_valid and hum_valid) else "warning"
            self._update_state(temp)
            return {"value": temp, "humidity": humidity, "unit": "°C", "quality": quality}
        except Exception as e:
            logger.error("DHT22 read error: %s", e)
            return {"value": 0.0, "humidity": 0.0, "unit": "°C", "quality": "error"}

    def _read_hardware(self):
        """Read from real hardware — placeholder for actual DHT22 protocol."""
        raise NotImplementedError("Hardware reading not available in simulation")

    def validate_reading(self, value: float) -> bool:
        return MIN_TEMP <= value <= MAX_TEMP

    def cleanup(self):
        if self._gpio:
            self._gpio.cleanup()
