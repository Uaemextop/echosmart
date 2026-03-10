import pytest
from src.sensor_manager import SensorManager


class TestSensorManager:
    def test_register_sensor(self, config):
        mgr = SensorManager(config)
        assert mgr.register_sensor("temp-1", "DS18B20") is True
        assert "temp-1" in mgr.get_registered_sensors()

    def test_register_unknown_type(self, config):
        mgr = SensorManager(config)
        assert mgr.register_sensor("x-1", "UnknownType") is False

    def test_register_duplicate(self, config):
        mgr = SensorManager(config)
        mgr.register_sensor("temp-1", "DS18B20")
        assert mgr.register_sensor("temp-1", "DS18B20") is False

    def test_unregister_sensor(self, config):
        mgr = SensorManager(config)
        mgr.register_sensor("temp-1", "DS18B20")
        assert mgr.unregister_sensor("temp-1") is True
        assert "temp-1" not in mgr.get_registered_sensors()

    def test_unregister_nonexistent(self, config):
        mgr = SensorManager(config)
        assert mgr.unregister_sensor("nope") is False

    def test_read_all_sensors(self, config):
        mgr = SensorManager(config)
        mgr.register_sensor("temp-1", "DS18B20")
        mgr.register_sensor("hum-1", "DHT22")
        readings = mgr.read_all_sensors()
        assert len(readings) == 2
        for r in readings:
            assert "sensor_id" in r
            assert "value" in r
            assert "unit" in r
            assert "timestamp" in r
            assert "quality" in r
            assert "sensor_type" in r

    def test_read_single_sensor(self, config):
        mgr = SensorManager(config)
        mgr.register_sensor("temp-1", "DS18B20")
        reading = mgr.read_sensor("temp-1")
        assert reading is not None
        assert reading["sensor_id"] == "temp-1"

    def test_read_unregistered_sensor(self, config):
        mgr = SensorManager(config)
        assert mgr.read_sensor("nope") is None

    def test_get_registered_sensors_empty(self, config):
        mgr = SensorManager(config)
        assert mgr.get_registered_sensors() == []
