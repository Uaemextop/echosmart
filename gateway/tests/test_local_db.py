import pytest
from src.local_db import LocalDB


class TestLocalDB:
    def test_store_and_retrieve_reading(self, local_db):
        rid = local_db.store_reading("t1", "DS18B20", 22.5, "°C", "2024-01-01T00:00:00")
        assert rid is not None
        unsynced = local_db.get_unsynced_readings()
        assert len(unsynced) == 1
        assert unsynced[0]["sensor_id"] == "t1"
        assert unsynced[0]["value"] == 22.5

    def test_mark_readings_synced(self, local_db):
        r1 = local_db.store_reading("t1", "DS18B20", 22.5, "°C", "2024-01-01T00:00:00")
        r2 = local_db.store_reading("t2", "DS18B20", 23.0, "°C", "2024-01-01T00:01:00")
        count = local_db.mark_readings_synced([r1, r2])
        assert count == 2
        assert local_db.get_unsynced_readings() == []

    def test_mark_empty_list(self, local_db):
        assert local_db.mark_readings_synced([]) == 0

    def test_store_and_retrieve_alert(self, local_db):
        aid = local_db.store_alert("r1", "t1", "high", "temp exceeded", 35.0)
        assert aid is not None
        alerts = local_db.get_unsynced_alerts()
        assert len(alerts) == 1
        assert alerts[0]["rule_id"] == "r1"

    def test_mark_alerts_synced(self, local_db):
        a1 = local_db.store_alert("r1", "t1", "high", "msg1", 35.0)
        a2 = local_db.store_alert("r2", "t2", "low", "msg2", 3.0)
        count = local_db.mark_alerts_synced([a1, a2])
        assert count == 2
        assert local_db.get_unsynced_alerts() == []

    def test_readings_count(self, local_db):
        local_db.store_reading("t1", "DS18B20", 22.5, "°C", "2024-01-01T00:00:00")
        local_db.store_reading("t2", "DS18B20", 23.0, "°C", "2024-01-01T00:01:00")
        local_db.mark_readings_synced([1])
        counts = local_db.get_readings_count()
        assert counts["total"] == 2
        assert counts["synced"] == 1
        assert counts["pending"] == 1

    def test_get_unsynced_readings_limit(self, local_db):
        for i in range(5):
            local_db.store_reading(f"t{i}", "DS18B20", 20.0 + i, "°C", "2024-01-01")
        assert len(local_db.get_unsynced_readings(limit=3)) == 3

    def test_quality_default(self, local_db):
        local_db.store_reading("t1", "DS18B20", 22.5, "°C", "2024-01-01T00:00:00")
        readings = local_db.get_unsynced_readings()
        assert readings[0]["quality"] == "good"
