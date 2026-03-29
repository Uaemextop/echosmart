"""Driver para sensor de temperatura DS18B20 (1-Wire)."""
import logging
import random

from ...domain.interfaces.sensor_driver import BaseSensorDriver
from ...domain.entities.sensor import SensorReading

logger = logging.getLogger(__name__)

SENSOR_TYPE = "temperature"
UNIT = "°C"
SIM_MIN = 15.0
SIM_MAX = 35.0


class DS18B20Driver(BaseSensorDriver):
    """Driver para sensor de temperatura DS18B20 vía protocolo 1-Wire."""

    def __init__(self, sensor_id: str, device_id: str = None, simulation: bool = False) -> None:
        self._sensor_id = sensor_id
        self.device_id = device_id
        self.simulation = simulation

    @property
    def sensor_id(self) -> str:
        return self._sensor_id

    @property
    def name(self) -> str:
        return "DS18B20"

    @property
    def sensor_type(self) -> str:
        return SENSOR_TYPE

    @property
    def unit(self) -> str:
        return UNIT

    def read(self) -> SensorReading:
        """Leer temperatura del sensor."""
        if self.simulation:
            value = round(random.uniform(SIM_MIN, SIM_MAX), 1)
        else:
            value = self._read_hardware()
        return SensorReading(
            sensor_id=self._sensor_id,
            sensor_type=SENSOR_TYPE,
            value=value,
            unit=UNIT,
        )

    def is_available(self) -> bool:
        """Verificar disponibilidad del sensor."""
        if self.simulation:
            return True
        return self.device_id is not None

    def _read_hardware(self) -> float:
        """Leer del bus 1-Wire real."""
        # TODO: implementar lectura /sys/bus/w1/devices/{device_id}/w1_slave
        return 0.0
