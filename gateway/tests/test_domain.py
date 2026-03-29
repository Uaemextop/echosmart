"""Tests de entidades del dominio."""
from datetime import datetime
from gateway.src.domain.entities.sensor import SensorReading, SensorMetadata


def test_sensor_reading_creation():
    """Verificar creación de SensorReading."""
    reading = SensorReading(
        sensor_id="ds18b20-01",
        sensor_type="temperature",
        value=25.5,
        unit="°C",
    )
    assert reading.sensor_id == "ds18b20-01"
    assert reading.value == 25.5
    assert reading.error is None
    assert isinstance(reading.timestamp, datetime)


def test_sensor_reading_empty():
    """SensorReading.empty debe crear lectura con error."""
    reading = SensorReading.empty("ds18b20-01", "temperature", "°C", "timeout")
    assert reading.value == 0.0
    assert reading.error == "timeout"


def test_sensor_metadata_creation():
    """Verificar creación de SensorMetadata."""
    meta = SensorMetadata(
        sensor_id="ds18b20-01",
        name="Sensor Cama 1",
        sensor_type="temperature",
        driver_type="ds18b20",
        location="Cama 1",
        unit="°C",
    )
    assert meta.enabled is True
    assert meta.min_threshold is None
