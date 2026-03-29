"""Tests del SensorManager."""
from gateway.src.application.sensor_manager import SensorManager
from gateway.src.infrastructure.drivers.ds18b20 import DS18B20Driver
from gateway.src.infrastructure.drivers.dht22 import DHT22Driver
from gateway.src.domain.entities.sensor import SensorReading


def test_sensor_manager_init():
    """Verificar inicialización del SensorManager."""
    manager = SensorManager(polling_interval=60)
    assert manager.polling_interval == 60
    assert manager.sensor_count == 0


def test_register_sensor():
    """Verificar registro de sensores."""
    manager = SensorManager()
    manager.register(DS18B20Driver("ds18b20-01", simulation=True))
    assert manager.sensor_count == 1


def test_read_all_returns_readings():
    """read_all debe retornar lecturas de todos los sensores."""
    manager = SensorManager()
    manager.register(DS18B20Driver("ds18b20-01", simulation=True))
    manager.register(DHT22Driver("dht22-01", simulation=True))
    readings = manager.read_all()
    assert len(readings) == 2
    for r in readings:
        assert isinstance(r, SensorReading)


def test_on_reading_callback():
    """El callback de lectura debe ser llamado por cada lectura."""
    manager = SensorManager()
    manager.register(DS18B20Driver("ds18b20-01", simulation=True))
    received = []
    manager.on_reading(lambda r: received.append(r))
    manager.read_all()
    assert len(received) == 1
    assert isinstance(received[0], SensorReading)
