"""Tests for domain entities."""

from datetime import datetime, timezone

from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.entities.alert import Alert, AlertSeverity
from gateway.src.domain.entities.gateway_config import GatewayConfig, SensorConfig


# ======================================================================
# SensorReading
# ======================================================================


class TestSensorReading:
    def test_create_reading(self):
        reading = SensorReading(
            sensor_id="t1",
            sensor_type="temperature",
            value=25.5,
            unit="°C",
        )
        assert reading.sensor_id == "t1"
        assert reading.sensor_type == "temperature"
        assert reading.value == 25.5
        assert reading.unit == "°C"
        assert reading.is_valid is True
        assert reading.metadata is None

    def test_reading_is_frozen(self):
        reading = SensorReading(
            sensor_id="t1", sensor_type="temperature", value=25.0, unit="°C"
        )
        try:
            reading.value = 30.0  # type: ignore[misc]
            assert False, "Should not allow mutation"
        except AttributeError:
            pass

    def test_to_dict(self):
        ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
        reading = SensorReading(
            sensor_id="t1",
            sensor_type="temperature",
            value=25.0,
            unit="°C",
            timestamp=ts,
        )
        d = reading.to_dict()
        assert d["sensor_id"] == "t1"
        assert d["value"] == 25.0
        assert d["timestamp"] == "2026-01-01T00:00:00+00:00"

    def test_reading_with_metadata(self):
        reading = SensorReading(
            sensor_id="dht1",
            sensor_type="temperature_humidity",
            value=22.0,
            unit="°C",
            metadata={"humidity": 65.0},
        )
        assert reading.metadata["humidity"] == 65.0


# ======================================================================
# Alert
# ======================================================================


class TestAlert:
    def test_create_alert(self):
        alert = Alert(
            sensor_id="t1",
            sensor_type="temperature",
            rule_name="temp_high",
            severity=AlertSeverity.WARNING,
            message="Temperature too high",
            threshold=30.0,
            actual_value=35.0,
        )
        assert alert.sensor_id == "t1"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.acknowledged is False
        assert alert.synced is False
        assert alert.id  # UUID auto-generated

    def test_alert_to_dict(self):
        alert = Alert(
            sensor_id="t1",
            sensor_type="temperature",
            rule_name="temp_high",
            severity=AlertSeverity.CRITICAL,
            message="Critical temp",
            threshold=40.0,
            actual_value=45.0,
        )
        d = alert.to_dict()
        assert d["severity"] == "critical"
        assert d["sensor_id"] == "t1"

    def test_severity_enum(self):
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.CRITICAL.value == "critical"


# ======================================================================
# GatewayConfig
# ======================================================================


class TestGatewayConfig:
    def test_defaults(self):
        cfg = GatewayConfig()
        assert cfg.gateway_id == "gw-001"
        assert cfg.simulation_mode is True
        assert cfg.sensors == []

    def test_with_sensors(self):
        sc = SensorConfig(sensor_type="ds18b20", name="Temp A")
        cfg = GatewayConfig(sensors=[sc])
        assert len(cfg.sensors) == 1
        assert cfg.sensors[0].sensor_type == "ds18b20"
