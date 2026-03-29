"""Driver para sensor capacitivo de humedad de suelo + ADS1115 (I2C/ADC)."""
import logging
import random

from ...domain.interfaces.sensor_driver import BaseSensorDriver
from ...domain.entities.sensor import SensorReading

logger = logging.getLogger(__name__)

ADS1115_ADDRESS = 0x48
SIM_MIN = 0.0
SIM_MAX = 100.0


class SoilMoistureDriver(BaseSensorDriver):
    """Driver para sensor de humedad de suelo vía ADS1115 (ADC I2C)."""

    def __init__(
        self,
        sensor_id: str,
        ads_address: int = ADS1115_ADDRESS,
        channel: int = 0,
        simulation: bool = False,
    ) -> None:
        self._sensor_id = sensor_id
        self.ads_address = ads_address
        self.channel = channel
        self.simulation = simulation

    @property
    def sensor_id(self) -> str:
        return self._sensor_id

    @property
    def name(self) -> str:
        return "Soil+ADS1115"

    @property
    def sensor_type(self) -> str:
        return "soil_moisture"

    @property
    def unit(self) -> str:
        return "%"

    def read(self) -> SensorReading:
        """Leer humedad del suelo."""
        if self.simulation:
            value = round(random.uniform(SIM_MIN, SIM_MAX), 1)
        else:
            value = self._read_hardware()
        return SensorReading(
            sensor_id=self._sensor_id,
            sensor_type="soil_moisture",
            value=value,
            unit="%",
        )

    def is_available(self) -> bool:
        return self.simulation

    def _read_hardware(self) -> float:
        """Leer del ADS1115 real vía I2C."""
        # TODO: usar ADS1x15
        return 0.0
