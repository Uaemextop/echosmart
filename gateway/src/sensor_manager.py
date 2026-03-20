"""Gestión centralizada de sensores."""

import logging

logger = logging.getLogger(__name__)


class SensorManager:
    """Orquestador de lecturas y polling de sensores."""

    def __init__(self, hal, polling_interval: int = 60):
        self.hal = hal
        self.polling_interval = polling_interval
        self.sensors = []
        logger.info(f"SensorManager inicializado con intervalo de {polling_interval}s.")

    def register_sensor(self, driver):
        """Registrar un driver de sensor."""
        self.sensors.append(driver)
        logger.info(f"Sensor registrado: {driver.name}")

    def read_all(self) -> list:
        """Leer todos los sensores registrados."""
        readings = []
        for sensor in self.sensors:
            try:
                reading = sensor.read()
                readings.append(reading)
            except Exception as e:
                logger.error(f"Error leyendo sensor {sensor.name}: {e}")
        return readings

    def start_polling(self):
        """Iniciar polling periódico."""
        # TODO: Implementar polling con schedule
        pass
