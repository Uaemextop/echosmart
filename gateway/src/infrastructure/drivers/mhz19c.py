"""Driver para sensor MH-Z19C (CO2, UART)."""
import logging
import random

from ...domain.interfaces.sensor_driver import BaseSensorDriver
from ...domain.entities.sensor import SensorReading

logger = logging.getLogger(__name__)

UART_PORT = "/dev/ttyS0"
SIM_MIN_CO2 = 400.0
SIM_MAX_CO2 = 2000.0


class MHZ19CDriver(BaseSensorDriver):
    """Driver para sensor CO2 MH-Z19C vía UART."""

    def __init__(self, sensor_id: str, uart_port: str = UART_PORT, simulation: bool = False) -> None:
        self._sensor_id = sensor_id
        self.uart_port = uart_port
        self.simulation = simulation

    @property
    def sensor_id(self) -> str:
        return self._sensor_id

    @property
    def name(self) -> str:
        return "MH-Z19C"

    @property
    def sensor_type(self) -> str:
        return "co2"

    @property
    def unit(self) -> str:
        return "ppm"

    def read(self) -> SensorReading:
        """Leer concentración de CO2."""
        if self.simulation:
            value = round(random.uniform(SIM_MIN_CO2, SIM_MAX_CO2), 0)
        else:
            value = self._read_hardware()
        return SensorReading(
            sensor_id=self._sensor_id,
            sensor_type="co2",
            value=value,
            unit="ppm",
        )

    def is_available(self) -> bool:
        return self.simulation

    def _read_hardware(self) -> float:
        """Leer del puerto UART real."""
        # TODO: implementar protocolo MH-Z19C
        return 0.0
