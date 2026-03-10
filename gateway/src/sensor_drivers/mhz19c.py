import random
import logging
from typing import Optional

from src.sensor_drivers.base import SensorDriver
from src.hal import UARTManager

logger = logging.getLogger(__name__)

MIN_CO2 = 0
MAX_CO2 = 5000
READ_COMMAND = b"\xff\x01\x86\x00\x00\x00\x00\x00\x79"


class MHZ19CDriver(SensorDriver):
    """Winsen MH-Z19C CO2 sensor driver (UART)."""

    def __init__(self, sensor_id: str, config: dict = None):
        super().__init__(sensor_id, config)
        self.port = self.config.get("port", "/dev/serial0")
        self.simulation = self.config.get("simulation", True)
        self._uart = None

    def initialize(self) -> bool:
        if not self.simulation:
            baudrate = self.config.get("baudrate", 9600)
            self._uart = UARTManager(self.port, baudrate)
        logger.info("MHZ19C %s initialised (simulation=%s)", self.sensor_id, self.simulation)
        return True

    def read(self) -> Optional[dict]:
        try:
            if self.simulation:
                value = round(random.uniform(400.0, 1200.0), 0)
            else:
                self._uart.write(READ_COMMAND)
                response = self._uart.read(9)
                if len(response) == 9 and response[0] == 0xFF and response[1] == 0x86:
                    value = float(response[2] * 256 + response[3])
                else:
                    raise IOError("Invalid response from MH-Z19C")

            quality = "good" if self.validate_reading(value) else "warning"
            self._update_state(value)
            return {"value": value, "unit": "ppm", "quality": quality}
        except Exception as e:
            logger.error("MHZ19C read error: %s", e)
            return {"value": 0.0, "unit": "ppm", "quality": "error"}

    def validate_reading(self, value: float) -> bool:
        return MIN_CO2 <= value <= MAX_CO2

    def cleanup(self):
        if self._uart:
            self._uart.close()
