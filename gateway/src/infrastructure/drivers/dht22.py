"""Driver para sensor DHT22 (temperatura + humedad, GPIO)."""
import logging
import random

from ...domain.interfaces.sensor_driver import BaseSensorDriver
from ...domain.entities.sensor import SensorReading

logger = logging.getLogger(__name__)


class DHT22Driver(BaseSensorDriver):
    """Driver para sensor DHT22 vía GPIO."""

    def __init__(self, sensor_id: str, gpio_pin: int = 17, simulation: bool = False) -> None:
        self._sensor_id = sensor_id
        self.gpio_pin = gpio_pin
        self.simulation = simulation

    @property
    def sensor_id(self) -> str:
        return self._sensor_id

    @property
    def name(self) -> str:
        return "DHT22"

    @property
    def sensor_type(self) -> str:
        return "humidity"

    @property
    def unit(self) -> str:
        return "%"

    def read(self) -> SensorReading:
        """Leer humedad del sensor."""
        if self.simulation:
            value = round(random.uniform(40.0, 90.0), 1)
        else:
            value = self._read_hardware()
        return SensorReading(
            sensor_id=self._sensor_id,
            sensor_type="humidity",
            value=value,
            unit="%",
        )

    def is_available(self) -> bool:
        return self.simulation or self.gpio_pin >= 0

    def _read_hardware(self) -> float:
        """Leer del GPIO real."""
        # TODO: usar Adafruit_DHT o RPi.GPIO
        return 0.0
