"""Tests for infrastructure discovery and HAL."""

from gateway.src.infrastructure.hal import SimulatedHAL, RaspberryPiHAL
from gateway.src.infrastructure.discovery import SensorDiscovery


class TestSimulatedHAL:
    def test_scan_i2c(self):
        hal = SimulatedHAL()
        devices = hal.scan_i2c()
        assert isinstance(devices, list)
        assert len(devices) > 0

    def test_list_1wire_devices(self):
        hal = SimulatedHAL()
        devices = hal.list_1wire_devices()
        assert isinstance(devices, list)

    def test_read_gpio(self):
        hal = SimulatedHAL()
        assert hal.read_gpio(4) == 0

    def test_read_i2c(self):
        hal = SimulatedHAL()
        data = hal.read_i2c(0x23, 0x10, 2)
        assert len(data) == 2


class TestSensorDiscovery:
    def test_scan_all(self):
        hal = SimulatedHAL()
        discovery = SensorDiscovery(hal)
        found = discovery.scan_all()
        assert isinstance(found, list)
        assert len(found) > 0

    def test_finds_i2c_sensors(self):
        hal = SimulatedHAL()
        discovery = SensorDiscovery(hal)
        found = discovery.scan_all()
        types = [s["type"] for s in found]
        assert "bh1750" in types

    def test_finds_1wire_sensors(self):
        hal = SimulatedHAL()
        discovery = SensorDiscovery(hal)
        found = discovery.scan_all()
        types = [s["type"] for s in found]
        assert "ds18b20" in types
