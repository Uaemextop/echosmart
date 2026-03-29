"""Tests for the sensor driver factory."""

import pytest

from gateway.src.infrastructure.driver_factory import SensorDriverFactory
from gateway.src.infrastructure.drivers.ds18b20_driver import DS18B20Driver
from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver


class TestSensorDriverFactory:
    def test_create_ds18b20(self):
        factory = SensorDriverFactory()
        driver = factory.create("ds18b20", {"sensor_id": "t1", "simulation": True})
        assert isinstance(driver, DS18B20Driver)
        assert isinstance(driver, BaseSensorDriver)

    def test_create_all_types(self):
        factory = SensorDriverFactory()
        for sensor_type in factory.available_types:
            driver = factory.create(sensor_type, {"simulation": True})
            assert isinstance(driver, BaseSensorDriver)

    def test_unknown_type_raises(self):
        factory = SensorDriverFactory()
        with pytest.raises(ValueError, match="Unknown sensor type"):
            factory.create("nonexistent", {})

    def test_register_custom_driver(self):
        factory = SensorDriverFactory()

        class CustomDriver(BaseSensorDriver):
            def read(self): pass
            def initialize(self): return True
            def shutdown(self): pass
            def is_healthy(self): return True

        factory.register("custom", CustomDriver)
        assert "custom" in factory.available_types

    def test_available_types(self):
        factory = SensorDriverFactory()
        types = factory.available_types
        assert "ds18b20" in types
        assert "dht22" in types
        assert "bh1750" in types
        assert "soil_moisture" in types
        assert "mhz19c" in types
