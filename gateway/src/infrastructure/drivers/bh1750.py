"""Driver para sensor BH1750 (luz, I2C)."""
import logging
import random

from ...domain.interfaces.sensor_driver import BaseSensorDriver
from ...domain.entities.sensor import SensorReading

logger = logging.getLogger(__name__)

I2C_ADDRESS = 0x23
SIM_MIN_LUX = 100.0
SIM_MAX_LUX = 10000.0


class BH1750Driver(BaseSensorDriver):
    """Driver para sensor de luz BH1750 vía I2C."""

    def __init__(self, sensor_id: str, i2c_address: int = I2C_ADDRESS, simulation: bool = False) -> None:
        self._sensor_id = sensor_id
        self.i2c_address = i2c_address
        self.simulation = simulation

    @property
    def sensor_id(self) -> str:
        return self._sensor_id

    @property
    def name(self) -> str:
        return "BH1750"

    @property
    def sensor_type(self) -> str:
        return "light"

    @property
    def unit(self) -> str:
        return "lux"

    def read(self) -> SensorReading:
        """Leer luminosidad."""
        if self.simulation:
            value = round(random.uniform(SIM_MIN_LUX, SIM_MAX_LUX), 1)
        else:
            value = self._read_hardware()
        return SensorReading(
            sensor_id=self._sensor_id,
            sensor_type="light",
            value=value,
            unit="lux",
        )

    def is_available(self) -> bool:
        return self.simulation

    def _read_hardware(self) -> float:
        """Leer del bus I2C real."""
        # TODO: usar smbus2
        return 0.0
