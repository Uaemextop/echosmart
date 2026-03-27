"""Tests de CloudSync."""

from gateway.src.cloud_sync import CloudSync


def test_cloud_sync_queue():
    """Verificar que se pueden encolar lecturas."""
    sync = CloudSync(api_url="http://localhost:8000", api_key="test")
    sync.queue_reading({"sensor_id": "s1", "value": 25.0})
    assert len(sync.pending_readings) == 1
