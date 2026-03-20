"""Driver para sensor DHT22 (temperatura + humedad, GPIO)."""

import logging
import random

logger = logging.getLogger(__name__)


class DHT22Driver:
    """Driver para sensor DHT22 vía GPIO."""

    name = "DHT22"
    type = "temperature_humidity"
    unit_temp = "°C"
    unit_humidity = "%"

    def __init__(self, pin: int = 4, simulation: bool = False):
        self.pin = pin
        self.simulation = simulation

    def read(self) -> dict:
        """Leer temperatura y humedad del sensor."""
        if self.simulation:
            temperature = round(random.uniform(15.0, 35.0), 1)
            humidity = round(random.uniform(40.0, 90.0), 1)
        else:
            # TODO: Leer del pin GPIO
            temperature = 0.0
            humidity = 0.0

        return {
            "sensor": self.name,
            "type": self.type,
            "temperature": {"value": temperature, "unit": self.unit_temp},
            "humidity": {"value": humidity, "unit": self.unit_humidity},
        }
