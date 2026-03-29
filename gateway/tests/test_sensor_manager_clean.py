"""Tests for the application-layer SensorManager (Clean Architecture)."""

from unittest.mock import MagicMock, patch

from gateway.src.application.sensor_manager import SensorManager
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.interfaces.sensor_driver import BaseSensorDriver


def _make_mock_driver(sensor_id: str = "mock-01", value: float = 25.0) -> MagicMock:
    """Create a mock driver that returns a fixed reading."""
    driver = MagicMock(spec=BaseSensorDriver)
    driver.sensor_id = sensor_id
    driver.read.return_value = SensorReading(
        sensor_id=sensor_id,
        sensor_type="temperature",
        value=value,
        unit="°C",
    )
    return driver


class TestSensorManagerClean:
    def test_register_and_count(self):
        mgr = SensorManager()
        driver = _make_mock_driver()
        mgr.register(driver)
        assert mgr.sensor_count == 1

    def test_read_all_returns_readings(self):
        mgr = SensorManager()
        mgr.register(_make_mock_driver("t1", 22.0))
        mgr.register(_make_mock_driver("t2", 24.0))
        readings = mgr.read_all()
        assert len(readings) == 2

    def test_read_all_stores_valid_readings(self):
        storage = MagicMock()
        mgr = SensorManager(storage=storage)
        mgr.register(_make_mock_driver())
        mgr.read_all()
        storage.save_reading.assert_called_once()

    def test_on_reading_callback(self):
        callback = MagicMock()
        mgr = SensorManager(on_reading=callback)
        mgr.register(_make_mock_driver())
        mgr.read_all()
        callback.assert_called_once()

    def test_circuit_breaker_trips_after_failures(self):
        mgr = SensorManager()
        driver = _make_mock_driver()
        driver.read.side_effect = RuntimeError("Sensor offline")
        mgr.register(driver)

        # Read enough times to trip the breaker (default threshold = 5)
        for _ in range(6):
            mgr.read_all()

        # Now the sensor should be skipped
        driver.read.reset_mock()
        readings = mgr.read_all()
        assert len(readings) == 0
        driver.read.assert_not_called()

    def test_unregister_shuts_down_driver(self):
        mgr = SensorManager()
        driver = _make_mock_driver("t1")
        mgr.register(driver)
        mgr.unregister("t1")
        driver.shutdown.assert_called_once()
        assert mgr.sensor_count == 0

    def test_metrics_tracking(self):
        mgr = SensorManager()
        mgr.register(_make_mock_driver("t1"))
        mgr.read_all()
        assert mgr.metrics.total_reads == 1
        assert mgr.metrics.readings_per_sensor["t1"] == 1

    def test_error_metrics_tracking(self):
        mgr = SensorManager()
        driver = _make_mock_driver()
        driver.read.side_effect = RuntimeError("fail")
        mgr.register(driver)
        mgr.read_all()
        assert mgr.metrics.total_errors == 1

    def test_initialize_all(self):
        mgr = SensorManager()
        d1 = _make_mock_driver("t1")
        d2 = _make_mock_driver("t2")
        mgr.register(d1)
        mgr.register(d2)
        mgr.initialize_all()
        d1.initialize.assert_called_once()
        d2.initialize.assert_called_once()

    def test_shutdown_all(self):
        mgr = SensorManager()
        d1 = _make_mock_driver("t1")
        d2 = _make_mock_driver("t2")
        mgr.register(d1)
        mgr.register(d2)
        mgr.shutdown_all()
        d1.shutdown.assert_called_once()
        d2.shutdown.assert_called_once()
