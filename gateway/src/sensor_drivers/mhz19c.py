"""Driver para sensor de CO₂ MHZ-19C (UART)."""

import logging
import random

logger = logging.getLogger(__name__)


class MHZ19CDriver:
    """Driver para sensor de CO₂ MHZ-19C vía UART."""

    name = "MHZ-19C"
    type = "co2"
    unit = "ppm"

    def __init__(self, port: str = "/dev/ttyS0", simulation: bool = False):
        self.port = port
        self.simulation = simulation

    def read(self) -> dict:
        """Leer concentración de CO₂ del sensor."""
        if self.simulation:
            value = round(random.uniform(350.0, 2000.0), 0)
        else:
            # TODO: Leer del puerto UART
            value = 0.0
        return {"sensor": self.name, "type": self.type, "value": value, "unit": self.unit}
