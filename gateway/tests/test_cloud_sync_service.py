"""Tests for CloudSyncService (application layer)."""

from unittest.mock import MagicMock

from gateway.src.application.cloud_sync_service import CloudSyncService


class TestCloudSyncService:
    def test_sync_readings(self):
        storage = MagicMock()
        storage.get_unsynced_readings.return_value = [
            {"id": 1, "sensor_id": "t1", "value": 25.0},
            {"id": 2, "sensor_id": "t2", "value": 60.0},
        ]
        client = MagicMock()
        client.sync_readings.return_value = [1, 2]

        svc = CloudSyncService(storage=storage, sync_client=client)
        result = svc.sync()
        assert result["readings_synced"] == 2
        storage.mark_readings_synced.assert_called_once_with([1, 2])

    def test_sync_nothing_pending(self):
        storage = MagicMock()
        storage.get_unsynced_readings.return_value = []
        storage.get_unsynced_alerts.return_value = []
        client = MagicMock()

        svc = CloudSyncService(storage=storage, sync_client=client)
        result = svc.sync()
        assert result["readings_synced"] == 0
        assert result["alerts_synced"] == 0

    def test_sync_alerts(self):
        storage = MagicMock()
        storage.get_unsynced_readings.return_value = []
        storage.get_unsynced_alerts.return_value = [
            {"id": "a1", "sensor_id": "t1"},
        ]
        client = MagicMock()
        client.sync_alerts.return_value = ["a1"]

        svc = CloudSyncService(storage=storage, sync_client=client)
        result = svc.sync()
        assert result["alerts_synced"] == 1
        storage.mark_alerts_synced.assert_called_once_with(["a1"])
