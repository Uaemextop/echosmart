"""Driver para sensor de humedad de suelo (ADC ADS1115)."""

import logging
import random

logger = logging.getLogger(__name__)


class SoilMoistureDriver:
    """Driver para sensor de humedad de suelo vía ADC ADS1115."""

    name = "SoilMoisture"
    type = "soil_moisture"
    unit = "%"

    def __init__(self, channel: int = 0, simulation: bool = False):
        self.channel = channel
        self.simulation = simulation

    def read(self) -> dict:
        """Leer humedad de suelo del sensor."""
        if self.simulation:
            value = round(random.uniform(20.0, 90.0), 1)
        else:
            # TODO: Leer del ADC ADS1115
            value = 0.0
        return {"sensor": self.name, "type": self.type, "value": value, "unit": self.unit}
