"""Driver para sensor de luminosidad BH1750 (I2C)."""

import logging
import random

logger = logging.getLogger(__name__)


class BH1750Driver:
    """Driver para sensor de luminosidad BH1750 vía I2C."""

    name = "BH1750"
    type = "light"
    unit = "lux"

    def __init__(self, address: int = 0x23, simulation: bool = False):
        self.address = address
        self.simulation = simulation

    def read(self) -> dict:
        """Leer luminosidad del sensor."""
        if self.simulation:
            value = round(random.uniform(500.0, 50000.0), 0)
        else:
            # TODO: Leer del bus I2C
            value = 0.0
        return {"sensor": self.name, "type": self.type, "value": value, "unit": self.unit}
