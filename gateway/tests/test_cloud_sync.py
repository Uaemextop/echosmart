import pytest
import requests
from unittest.mock import patch, MagicMock

from src.cloud_sync import CloudSyncManager
from src.config import Config
from src.local_db import LocalDB


@pytest.fixture
def cloud_sync(config, local_db):
    return CloudSyncManager(config, local_db)


class TestCloudSyncManager:
    def test_sync_readings_empty(self, cloud_sync):
        result = cloud_sync.sync_readings()
        assert result["synced_count"] == 0
        assert result["failed_count"] == 0

    @patch("src.cloud_sync.requests.post")
    def test_sync_readings_success(self, mock_post, cloud_sync, local_db):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        local_db.store_reading("t1", "DS18B20", 22.5, "°C", "2024-01-01T00:00:00")
        local_db.store_reading("t2", "DS18B20", 23.0, "°C", "2024-01-01T00:01:00")

        result = cloud_sync.sync_readings()
        assert result["synced_count"] == 2
        assert result["failed_count"] == 0

        counts = local_db.get_readings_count()
        assert counts["pending"] == 0

    @patch("src.cloud_sync.requests.post")
    def test_sync_readings_failure(self, mock_post, cloud_sync, local_db):
        mock_post.side_effect = requests.ConnectionError("network error")
        local_db.store_reading("t1", "DS18B20", 22.5, "°C", "2024-01-01T00:00:00")

        # Patch retry delays to zero so test runs fast
        cloud_sync.retry_delays = [0, 0, 0, 0, 0]
        result = cloud_sync.sync_readings()
        assert result["synced_count"] == 0
        assert result["failed_count"] == 1

    @patch("src.cloud_sync.requests.post")
    def test_sync_alerts_success(self, mock_post, cloud_sync, local_db):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        local_db.store_alert("r1", "t1", "high", "temp high", 35.0)
        result = cloud_sync.sync_alerts()
        assert result["synced_count"] == 1

    def test_sync_alerts_empty(self, cloud_sync):
        result = cloud_sync.sync_alerts()
        assert result["synced_count"] == 0

    @patch("src.cloud_sync.requests.get")
    def test_fetch_config_success(self, mock_get, cloud_sync):
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.json.return_value = {"polling_interval": 30}
        mock_get.return_value.raise_for_status = MagicMock()

        cfg = cloud_sync.fetch_config()
        assert cfg == {"polling_interval": 30}

    @patch("src.cloud_sync.requests.get")
    def test_fetch_config_failure(self, mock_get, cloud_sync):
        mock_get.side_effect = requests.ConnectionError("timeout")
        assert cloud_sync.fetch_config() is None
