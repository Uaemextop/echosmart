"""Caso de uso: Gestión y polling de sensores."""
import logging
from typing import List, Callable

from ..domain.interfaces.sensor_driver import BaseSensorDriver
from ..domain.entities.sensor import SensorReading

logger = logging.getLogger(__name__)


class SensorManager:
    """Orquesta el registro y lectura periódica de sensores.

    Sigue el principio Open/Closed: nuevos sensores se agregan
    registrando un nuevo driver sin modificar esta clase.
    """

    def __init__(self, polling_interval: int = 60) -> None:
        self._drivers: List[BaseSensorDriver] = []
        self._on_reading_callbacks: List[Callable[[SensorReading], None]] = []
        self.polling_interval = polling_interval
        logger.info("SensorManager inicializado con intervalo=%ds", polling_interval)

    def register(self, driver: BaseSensorDriver) -> None:
        """Registrar un driver de sensor."""
        self._drivers.append(driver)
        logger.info("Sensor registrado: %s (%s)", driver.name, driver.sensor_type)

    def on_reading(self, callback: Callable[[SensorReading], None]) -> None:
        """Suscribir callback a nuevas lecturas (patrón Observer)."""
        self._on_reading_callbacks.append(callback)

    def read_all(self) -> List[SensorReading]:
        """Leer todos los sensores registrados."""
        readings: List[SensorReading] = []
        for driver in self._drivers:
            try:
                reading = driver.read()
                readings.append(reading)
                for cb in self._on_reading_callbacks:
                    cb(reading)
            except Exception as exc:
                logger.error("Error leyendo sensor %s: %s", driver.name, exc)
                error_reading = SensorReading.empty(
                    driver.sensor_id, driver.sensor_type, driver.unit, str(exc)
                )
                readings.append(error_reading)
        return readings

    @property
    def sensor_count(self) -> int:
        """Número de sensores registrados."""
        return len(self._drivers)
