import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone

from src.sensor_drivers.base import SensorDriver
from src.sensor_drivers.ds18b20 import DS18B20Driver
from src.sensor_drivers.dht22 import DHT22Driver
from src.sensor_drivers.bh1750 import BH1750Driver
from src.sensor_drivers.soil_moisture import SoilMoistureDriver
from src.sensor_drivers.mhz19c import MHZ19CDriver

logger = logging.getLogger(__name__)

DRIVER_MAP: Dict[str, type] = {
    "DS18B20": DS18B20Driver,
    "DHT22": DHT22Driver,
    "BH1750": BH1750Driver,
    "SoilMoisture": SoilMoistureDriver,
    "MHZ19C": MHZ19CDriver,
}


class SensorManager:
    """Orchestrates sensor registration, polling and lifecycle."""

    def __init__(self, config):
        self.sensors: Dict[str, SensorDriver] = {}
        self.config = config

    def register_sensor(
        self, sensor_id: str, sensor_type: str, sensor_config: dict = None
    ) -> bool:
        if sensor_id in self.sensors:
            logger.warning("Sensor %s already registered", sensor_id)
            return False

        driver_cls = DRIVER_MAP.get(sensor_type)
        if driver_cls is None:
            logger.error("Unknown sensor type: %s", sensor_type)
            return False

        cfg = sensor_config or {}
        cfg.setdefault("simulation", True)
        driver = driver_cls(sensor_id, cfg)

        if not driver.initialize():
            logger.error("Failed to initialize sensor %s", sensor_id)
            return False

        self.sensors[sensor_id] = driver
        logger.info("Registered sensor %s (%s)", sensor_id, sensor_type)
        return True

    def unregister_sensor(self, sensor_id: str) -> bool:
        driver = self.sensors.pop(sensor_id, None)
        if driver is None:
            return False
        driver.cleanup()
        logger.info("Unregistered sensor %s", sensor_id)
        return True

    def read_all_sensors(self) -> List[dict]:
        readings = []
        for sensor_id, driver in self.sensors.items():
            reading = self._read_single(sensor_id, driver)
            if reading:
                readings.append(reading)
        return readings

    def read_sensor(self, sensor_id: str) -> Optional[dict]:
        driver = self.sensors.get(sensor_id)
        if driver is None:
            logger.warning("Sensor %s not registered", sensor_id)
            return None
        return self._read_single(sensor_id, driver)

    def get_registered_sensors(self) -> List[str]:
        return list(self.sensors.keys())

    def _read_single(self, sensor_id: str, driver: SensorDriver) -> Optional[dict]:
        raw = driver.read()
        if raw is None:
            return None
        sensor_type = type(driver).__name__.replace("Driver", "")
        return {
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "value": raw["value"],
            "unit": raw["unit"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "quality": raw["quality"],
        }
