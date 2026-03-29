"""Sensor driver factory — Creates the correct driver from configuration.

Follows the Factory pattern so that new sensor types can be added without
modifying the SensorManager.
"""

from __future__ import annotations

import logging
from typing import Type

from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver
from gateway.src.infrastructure.drivers.bh1750_driver import BH1750Driver
from gateway.src.infrastructure.drivers.dht22_driver import DHT22Driver
from gateway.src.infrastructure.drivers.ds18b20_driver import DS18B20Driver
from gateway.src.infrastructure.drivers.mhz19c_driver import MHZ19CDriver
from gateway.src.infrastructure.drivers.soil_moisture_driver import SoilMoistureDriver

logger = logging.getLogger(__name__)

# Default driver registry — maps sensor type keys to driver classes
_DEFAULT_REGISTRY: dict[str, Type[BaseSensorDriver]] = {
    "ds18b20": DS18B20Driver,
    "dht22": DHT22Driver,
    "bh1750": BH1750Driver,
    "soil_moisture": SoilMoistureDriver,
    "mhz19c": MHZ19CDriver,
}


class SensorDriverFactory:
    """Factory for creating sensor driver instances from configuration dicts.

    Usage::

        factory = SensorDriverFactory()
        driver = factory.create("ds18b20", {"sensor_id": "t1", "simulation": True})
    """

    def __init__(self) -> None:
        self._registry: dict[str, Type[BaseSensorDriver]] = dict(_DEFAULT_REGISTRY)

    def register(self, sensor_type: str, driver_cls: Type[BaseSensorDriver]) -> None:
        """Register a new driver class for a sensor type (Open/Closed principle)."""
        self._registry[sensor_type] = driver_cls
        logger.info("Registered driver %s for type '%s'.", driver_cls.__name__, sensor_type)

    def create(self, sensor_type: str, config: dict) -> BaseSensorDriver:
        """Create and return a driver instance.

        Args:
            sensor_type: Key identifying the sensor type (e.g. ``ds18b20``).
            config: Driver-specific keyword arguments passed to the constructor.

        Returns:
            An initialized ``BaseSensorDriver`` subclass instance.

        Raises:
            ValueError: If *sensor_type* is not registered.
        """
        driver_cls = self._registry.get(sensor_type)
        if driver_cls is None:
            available = ", ".join(sorted(self._registry))
            raise ValueError(
                f"Unknown sensor type '{sensor_type}'. Available: {available}"
            )
        driver = driver_cls(**config)
        logger.info("Created %s driver: %r", sensor_type, driver)
        return driver

    @property
    def available_types(self) -> list[str]:
        """Return sorted list of registered sensor type keys."""
        return sorted(self._registry)
