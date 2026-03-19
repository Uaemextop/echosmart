"""Driver para sensor de temperatura DS18B20 (1-Wire)."""

import logging
import random

logger = logging.getLogger(__name__)


class DS18B20Driver:
    """Driver para sensor de temperatura DS18B20 vía protocolo 1-Wire."""

    name = "DS18B20"
    type = "temperature"
    unit = "°C"

    def __init__(self, device_id: str = None, simulation: bool = False):
        self.device_id = device_id
        self.simulation = simulation

    def read(self) -> dict:
        """Leer temperatura del sensor."""
        if self.simulation:
            value = round(random.uniform(15.0, 35.0), 1)
        else:
            # TODO: Leer del bus 1-Wire
            value = 0.0
        return {"sensor": self.name, "type": self.type, "value": value, "unit": self.unit}
