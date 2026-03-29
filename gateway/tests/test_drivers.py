"""Tests de los drivers de sensores en modo simulación."""
from gateway.src.infrastructure.drivers.ds18b20 import DS18B20Driver
from gateway.src.infrastructure.drivers.dht22 import DHT22Driver
from gateway.src.infrastructure.drivers.bh1750 import BH1750Driver
from gateway.src.infrastructure.drivers.mhz19c import MHZ19CDriver
from gateway.src.infrastructure.drivers.soil_moisture import SoilMoistureDriver
from gateway.src.domain.entities.sensor import SensorReading


def test_ds18b20_simulation():
    """DS18B20 en simulación debe retornar temperatura válida."""
    driver = DS18B20Driver("ds18b20-01", simulation=True)
    reading = driver.read()
    assert isinstance(reading, SensorReading)
    assert reading.sensor_type == "temperature"
    assert 15.0 <= reading.value <= 35.0
    assert reading.unit == "°C"
    assert reading.error is None


def test_dht22_simulation():
    """DHT22 en simulación debe retornar humedad válida."""
    driver = DHT22Driver("dht22-01", simulation=True)
    reading = driver.read()
    assert reading.sensor_type == "humidity"
    assert 40.0 <= reading.value <= 90.0
    assert reading.unit == "%"


def test_bh1750_simulation():
    """BH1750 en simulación debe retornar luminosidad válida."""
    driver = BH1750Driver("bh1750-01", simulation=True)
    reading = driver.read()
    assert reading.sensor_type == "light"
    assert reading.unit == "lux"
    assert reading.value > 0


def test_mhz19c_simulation():
    """MH-Z19C en simulación debe retornar CO2 válido."""
    driver = MHZ19CDriver("mhz19c-01", simulation=True)
    reading = driver.read()
    assert reading.sensor_type == "co2"
    assert reading.unit == "ppm"
    assert 400.0 <= reading.value <= 2000.0


def test_soil_moisture_simulation():
    """Sensor de suelo en simulación debe retornar humedad válida."""
    driver = SoilMoistureDriver("soil-01", simulation=True)
    reading = driver.read()
    assert reading.sensor_type == "soil_moisture"
    assert reading.unit == "%"
    assert 0.0 <= reading.value <= 100.0


def test_all_drivers_implement_base():
    """Todos los drivers deben implementar BaseSensorDriver."""
    from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver
    drivers = [
        DS18B20Driver("id1", simulation=True),
        DHT22Driver("id2", simulation=True),
        BH1750Driver("id3", simulation=True),
        MHZ19CDriver("id4", simulation=True),
        SoilMoistureDriver("id5", simulation=True),
    ]
    for driver in drivers:
        assert isinstance(driver, BaseSensorDriver)
        assert driver.sensor_id is not None
        assert driver.name is not None
        assert driver.sensor_type is not None
        assert driver.unit is not None
