"""Tests for SqliteStorageRepository."""

import os
import tempfile

import pytest

from gateway.src.domain.entities.alert import Alert, AlertSeverity
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.infrastructure.sqlite_storage import SqliteStorageRepository


@pytest.fixture
def storage():
    """Create a temporary SQLite database for each test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    repo = SqliteStorageRepository(db_path=path)
    yield repo
    repo.close()
    os.unlink(path)


class TestSqliteStorage:
    def test_save_and_get_reading(self, storage):
        reading = SensorReading(
            sensor_id="t1",
            sensor_type="temperature",
            value=25.0,
            unit="°C",
        )
        storage.save_reading(reading)
        readings = storage.get_readings(sensor_id="t1")
        assert len(readings) == 1
        assert readings[0].value == 25.0

    def test_get_unsynced_readings(self, storage):
        reading = SensorReading(
            sensor_id="t1", sensor_type="temperature", value=22.0, unit="°C"
        )
        storage.save_reading(reading)
        unsynced = storage.get_unsynced_readings()
        assert len(unsynced) == 1
        assert unsynced[0]["sensor_id"] == "t1"

    def test_mark_readings_synced(self, storage):
        reading = SensorReading(
            sensor_id="t1", sensor_type="temperature", value=22.0, unit="°C"
        )
        storage.save_reading(reading)
        unsynced = storage.get_unsynced_readings()
        ids = [r["id"] for r in unsynced]
        storage.mark_readings_synced(ids)
        assert len(storage.get_unsynced_readings()) == 0

    def test_save_and_get_alert(self, storage):
        alert = Alert(
            sensor_id="t1",
            sensor_type="temperature",
            rule_name="temp_high",
            severity=AlertSeverity.WARNING,
            message="Too hot",
            threshold=30.0,
            actual_value=35.0,
        )
        storage.save_alert(alert)
        unsynced = storage.get_unsynced_alerts()
        assert len(unsynced) == 1
        assert unsynced[0]["sensor_id"] == "t1"

    def test_mark_alerts_synced(self, storage):
        alert = Alert(
            sensor_id="t1",
            sensor_type="temperature",
            rule_name="temp_high",
            severity=AlertSeverity.WARNING,
            message="Too hot",
            threshold=30.0,
            actual_value=35.0,
        )
        storage.save_alert(alert)
        unsynced = storage.get_unsynced_alerts()
        ids = [a["id"] for a in unsynced]
        storage.mark_alerts_synced(ids)
        assert len(storage.get_unsynced_alerts()) == 0

    def test_get_stats(self, storage):
        stats = storage.get_stats()
        assert stats["total_readings"] == 0
        assert stats["unsynced_readings"] == 0

        reading = SensorReading(
            sensor_id="t1", sensor_type="temperature", value=22.0, unit="°C"
        )
        storage.save_reading(reading)
        stats = storage.get_stats()
        assert stats["total_readings"] == 1
        assert stats["unsynced_readings"] == 1

    def test_get_readings_with_limit(self, storage):
        for i in range(10):
            storage.save_reading(
                SensorReading(
                    sensor_id="t1",
                    sensor_type="temperature",
                    value=float(i),
                    unit="°C",
                )
            )
        readings = storage.get_readings(limit=5)
        assert len(readings) == 5

    def test_mark_readings_synced_empty_list(self, storage):
        # Should not raise
        storage.mark_readings_synced([])

    def test_mark_alerts_synced_empty_list(self, storage):
        # Should not raise
        storage.mark_alerts_synced([])
