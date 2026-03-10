import pytest

from src.sensor_drivers.ds18b20 import DS18B20Driver
from src.sensor_drivers.dht22 import DHT22Driver
from src.sensor_drivers.bh1750 import BH1750Driver
from src.sensor_drivers.soil_moisture import SoilMoistureDriver
from src.sensor_drivers.mhz19c import MHZ19CDriver


class TestDS18B20Driver:
    def test_initialize(self):
        d = DS18B20Driver("t1", {"simulation": True})
        assert d.initialize() is True

    def test_read_simulation(self):
        d = DS18B20Driver("t1", {"simulation": True})
        d.initialize()
        reading = d.read()
        assert reading is not None
        assert reading["unit"] == "°C"
        assert reading["quality"] == "good"
        assert -55.0 <= reading["value"] <= 125.0

    def test_validate_reading(self):
        d = DS18B20Driver("t1")
        assert d.validate_reading(25.0) is True
        assert d.validate_reading(-60.0) is False
        assert d.validate_reading(130.0) is False


class TestDHT22Driver:
    def test_initialize(self):
        d = DHT22Driver("h1", {"simulation": True})
        assert d.initialize() is True

    def test_read_simulation(self):
        d = DHT22Driver("h1", {"simulation": True})
        d.initialize()
        reading = d.read()
        assert reading is not None
        assert reading["unit"] == "°C"
        assert "humidity" in reading
        assert 0.0 <= reading["humidity"] <= 100.0

    def test_validate_reading(self):
        d = DHT22Driver("h1")
        assert d.validate_reading(20.0) is True
        assert d.validate_reading(-50.0) is False
        assert d.validate_reading(90.0) is False


class TestBH1750Driver:
    def test_initialize(self):
        d = BH1750Driver("l1", {"simulation": True})
        assert d.initialize() is True

    def test_read_simulation(self):
        d = BH1750Driver("l1", {"simulation": True})
        d.initialize()
        reading = d.read()
        assert reading is not None
        assert reading["unit"] == "lux"
        assert reading["quality"] == "good"
        assert 0 <= reading["value"] <= 65535

    def test_validate_reading(self):
        d = BH1750Driver("l1")
        assert d.validate_reading(500.0) is True
        assert d.validate_reading(-1.0) is False
        assert d.validate_reading(70000.0) is False


class TestSoilMoistureDriver:
    def test_initialize(self):
        d = SoilMoistureDriver("m1", {"simulation": True})
        assert d.initialize() is True

    def test_read_simulation(self):
        d = SoilMoistureDriver("m1", {"simulation": True})
        d.initialize()
        reading = d.read()
        assert reading is not None
        assert reading["unit"] == "%"
        assert 0.0 <= reading["value"] <= 100.0

    def test_validate_reading(self):
        d = SoilMoistureDriver("m1")
        assert d.validate_reading(50.0) is True
        assert d.validate_reading(-1.0) is False
        assert d.validate_reading(101.0) is False


class TestMHZ19CDriver:
    def test_initialize(self):
        d = MHZ19CDriver("c1", {"simulation": True})
        assert d.initialize() is True

    def test_read_simulation(self):
        d = MHZ19CDriver("c1", {"simulation": True})
        d.initialize()
        reading = d.read()
        assert reading is not None
        assert reading["unit"] == "ppm"
        assert 0 <= reading["value"] <= 5000

    def test_validate_reading(self):
        d = MHZ19CDriver("c1")
        assert d.validate_reading(400.0) is True
        assert d.validate_reading(-1.0) is False
        assert d.validate_reading(6000.0) is False


class TestDriverStateTracking:
    def test_last_value_updated(self):
        d = DS18B20Driver("t1", {"simulation": True})
        d.initialize()
        d.read()
        assert d.last_value is not None
        assert d.last_read_time is not None

    def test_cleanup(self):
        d = DS18B20Driver("t1", {"simulation": True})
        d.initialize()
        d.cleanup()  # should not raise
