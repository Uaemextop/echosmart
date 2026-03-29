"""Integration test: full flow sensor → storage → alert → sync."""

import os
import tempfile
from unittest.mock import MagicMock

from gateway.src.application.alert_engine import AlertEngine, ThresholdRule
from gateway.src.application.cloud_sync_service import CloudSyncService
from gateway.src.application.sensor_manager import SensorManager
from gateway.src.domain.entities.alert import AlertSeverity
from gateway.src.infrastructure.drivers.ds18b20_driver import DS18B20Driver
from gateway.src.infrastructure.drivers.dht22_driver import DHT22Driver
from gateway.src.infrastructure.sqlite_storage import SqliteStorageRepository


class TestIntegrationFlow:
    """End-to-end test: sensors → manager → storage → alerts → sync."""

    def test_full_pipeline(self):
        # Setup temp database
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:
            storage = SqliteStorageRepository(db_path=db_path)

            # Alert engine
            alert_engine = AlertEngine(storage=storage, cooldown_seconds=0)
            alert_engine.add_rule(
                ThresholdRule(
                    "temp_high",
                    "temperature",
                    threshold=30.0,
                    severity=AlertSeverity.WARNING,
                )
            )

            # Sensor manager with on_reading callback
            alerts_triggered = []

            def on_reading(reading):
                triggered = alert_engine.evaluate(reading)
                alerts_triggered.extend(triggered)

            manager = SensorManager(
                storage=storage,
                on_reading=on_reading,
            )

            # Register drivers
            ds18b20 = DS18B20Driver(sensor_id="t1", simulation=True)
            dht22 = DHT22Driver(sensor_id="th1", simulation=True)
            manager.register(ds18b20)
            manager.register(dht22)
            manager.initialize_all()

            # Run multiple polling cycles
            for _ in range(5):
                manager.read_all()

            # Verify readings stored (DS18B20 outlier filter may reject some;
            # DHT22 always produces valid readings — at least 5 from it)
            stats = storage.get_stats()
            assert stats["total_readings"] >= 5

            # Cloud sync
            sync_client = MagicMock()
            sync_client.sync_readings.return_value = []
            sync_client.sync_alerts.return_value = []
            cloud_sync = CloudSyncService(storage=storage, sync_client=sync_client)
            cloud_sync.sync()

            # Verify sync attempted
            sync_client.sync_readings.assert_called_once()

            manager.shutdown_all()
            storage.close()
        finally:
            os.unlink(db_path)
