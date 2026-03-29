"""Tests for infrastructure drivers (Clean Architecture)."""

from gateway.src.infrastructure.drivers.ds18b20_driver import DS18B20Driver
from gateway.src.infrastructure.drivers.dht22_driver import DHT22Driver
from gateway.src.infrastructure.drivers.bh1750_driver import BH1750Driver
from gateway.src.infrastructure.drivers.soil_moisture_driver import SoilMoistureDriver
from gateway.src.infrastructure.drivers.mhz19c_driver import MHZ19CDriver
from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver
from gateway.src.domain.constants import SENSOR_RANGES, SIMULATION_RANGES


# ======================================================================
# DS18B20 Driver
# ======================================================================


class TestDS18B20Driver:
    def test_implements_interface(self):
        driver = DS18B20Driver(simulation=True)
        assert isinstance(driver, BaseSensorDriver)

    def test_initialize(self):
        driver = DS18B20Driver(simulation=True)
        assert driver.initialize() is True
        assert driver.initialized is True

    def test_read_simulation(self):
        driver = DS18B20Driver(simulation=True)
        driver.initialize()
        reading = driver.read()
        assert reading.sensor_type == "temperature"
        assert reading.unit == "°C"
        assert reading.is_valid is True
        assert SIMULATION_RANGES["temperature"]["min"] <= reading.value <= SIMULATION_RANGES["temperature"]["max"]

    def test_shutdown(self):
        driver = DS18B20Driver(simulation=True)
        driver.initialize()
        driver.shutdown()
        assert driver.initialized is False

    def test_is_healthy(self):
        driver = DS18B20Driver(simulation=True)
        assert driver.is_healthy() is False
        driver.initialize()
        assert driver.is_healthy() is True

    def test_get_info(self):
        driver = DS18B20Driver(sensor_id="t-01", simulation=True)
        driver.initialize()
        info = driver.get_info()
        assert info["sensor_id"] == "t-01"
        assert info["protocol"] == "1-wire"
        assert info["simulation"] is True

    def test_repr(self):
        driver = DS18B20Driver(sensor_id="t-01", simulation=True)
        assert "t-01" in repr(driver)

    def test_properties(self):
        driver = DS18B20Driver(sensor_id="t-01", simulation=True)
        assert driver.sensor_id == "t-01"
        assert driver.sensor_type == "temperature"
        assert driver.protocol == "1-wire"
        assert driver.is_simulation is True


# ======================================================================
# DHT22 Driver
# ======================================================================


class TestDHT22Driver:
    def test_implements_interface(self):
        driver = DHT22Driver(simulation=True)
        assert isinstance(driver, BaseSensorDriver)

    def test_read_simulation(self):
        driver = DHT22Driver(simulation=True)
        driver.initialize()
        reading = driver.read()
        assert reading.sensor_type == "temperature_humidity"
        assert reading.is_valid is True
        assert reading.metadata is not None
        assert "humidity" in reading.metadata

    def test_humidity_in_metadata(self):
        driver = DHT22Driver(simulation=True)
        driver.initialize()
        reading = driver.read()
        hum = reading.metadata["humidity"]
        assert SIMULATION_RANGES["humidity"]["min"] <= hum <= SIMULATION_RANGES["humidity"]["max"]


# ======================================================================
# BH1750 Driver
# ======================================================================


class TestBH1750Driver:
    def test_implements_interface(self):
        driver = BH1750Driver(simulation=True)
        assert isinstance(driver, BaseSensorDriver)

    def test_read_simulation(self):
        driver = BH1750Driver(simulation=True)
        driver.initialize()
        reading = driver.read()
        assert reading.sensor_type == "light"
        assert reading.unit == "lux"
        assert reading.is_valid is True

    def test_shutdown_makes_unhealthy(self):
        driver = BH1750Driver(simulation=True)
        driver.initialize()
        assert driver.is_healthy() is True
        driver.shutdown()
        assert driver.is_healthy() is False


# ======================================================================
# Soil Moisture Driver
# ======================================================================


class TestSoilMoistureDriver:
    def test_implements_interface(self):
        driver = SoilMoistureDriver(simulation=True)
        assert isinstance(driver, BaseSensorDriver)

    def test_read_simulation(self):
        driver = SoilMoistureDriver(simulation=True)
        driver.initialize()
        reading = driver.read()
        assert reading.sensor_type == "soil_moisture"
        assert reading.unit == "%"
        assert reading.is_valid is True

    def test_auto_calibrate(self):
        driver = SoilMoistureDriver(simulation=True)
        driver.auto_calibrate(dry_reading=30000, wet_reading=10000)
        assert driver._dry_value == 30000
        assert driver._wet_value == 10000


# ======================================================================
# MHZ19C Driver
# ======================================================================


class TestMHZ19CDriver:
    def test_implements_interface(self):
        driver = MHZ19CDriver(simulation=True)
        assert isinstance(driver, BaseSensorDriver)

    def test_read_simulation(self):
        driver = MHZ19CDriver(simulation=True)
        driver.initialize()
        reading = driver.read()
        assert reading.sensor_type == "co2"
        assert reading.unit == "ppm"
        assert reading.is_valid is True

    def test_checksum_validation(self):
        # Valid MH-Z19C response for 410 ppm (checksum = 0xDF)
        valid = bytes([0xFF, 0x86, 0x01, 0x9A, 0x00, 0x00, 0x00, 0x00, 0xDF])
        assert MHZ19CDriver._validate_checksum(valid) is True

        # Corrupted response
        invalid = bytes([0xFF, 0x86, 0x01, 0x9A, 0x00, 0x00, 0x00, 0x00, 0x00])
        assert MHZ19CDriver._validate_checksum(invalid) is False

    def test_parse_ppm(self):
        response = bytes([0xFF, 0x86, 0x01, 0x9A, 0x00, 0x00, 0x00, 0x00, 0xE1])
        ppm = MHZ19CDriver._parse_ppm(response)
        assert ppm == 410
