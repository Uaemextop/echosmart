"""Tests for the application-layer AlertEngine (Clean Architecture)."""

import time
from unittest.mock import MagicMock

from gateway.src.application.alert_engine import (
    AlertEngine,
    RangeRule,
    RateOfChangeRule,
    StaleDataRule,
    ThresholdRule,
)
from gateway.src.domain.entities.alert import AlertSeverity
from gateway.src.domain.entities.sensor_reading import SensorReading


def _reading(value: float, sensor_type: str = "temperature", sensor_id: str = "t1") -> SensorReading:
    return SensorReading(
        sensor_id=sensor_id,
        sensor_type=sensor_type,
        value=value,
        unit="°C",
    )


# ======================================================================
# ThresholdRule
# ======================================================================


class TestThresholdRule:
    def test_gt_violation(self):
        rule = ThresholdRule("temp_high", "temperature", threshold=30.0, condition="gt")
        alert = rule.evaluate(_reading(35.0))
        assert alert is not None
        assert alert.actual_value == 35.0

    def test_gt_no_violation(self):
        rule = ThresholdRule("temp_high", "temperature", threshold=30.0, condition="gt")
        assert rule.evaluate(_reading(25.0)) is None

    def test_lt_violation(self):
        rule = ThresholdRule("temp_low", "temperature", threshold=10.0, condition="lt")
        alert = rule.evaluate(_reading(5.0))
        assert alert is not None

    def test_wrong_sensor_type_ignored(self):
        rule = ThresholdRule("temp_high", "temperature", threshold=30.0)
        assert rule.evaluate(_reading(35.0, sensor_type="humidity")) is None


# ======================================================================
# RangeRule
# ======================================================================


class TestRangeRule:
    def test_in_range(self):
        rule = RangeRule("temp_range", "temperature", min_value=18.0, max_value=28.0)
        assert rule.evaluate(_reading(22.0)) is None

    def test_above_range(self):
        rule = RangeRule("temp_range", "temperature", min_value=18.0, max_value=28.0)
        alert = rule.evaluate(_reading(35.0))
        assert alert is not None
        assert alert.threshold == 28.0

    def test_below_range(self):
        rule = RangeRule("temp_range", "temperature", min_value=18.0, max_value=28.0)
        alert = rule.evaluate(_reading(10.0))
        assert alert is not None
        assert alert.threshold == 18.0


# ======================================================================
# RateOfChangeRule
# ======================================================================


class TestRateOfChangeRule:
    def test_no_alert_on_first_reading(self):
        rule = RateOfChangeRule("temp_rate", "temperature", max_delta=3.0)
        assert rule.evaluate(_reading(22.0)) is None

    def test_no_alert_small_change(self):
        rule = RateOfChangeRule("temp_rate", "temperature", max_delta=3.0)
        rule.evaluate(_reading(22.0))
        assert rule.evaluate(_reading(23.0)) is None

    def test_alert_on_big_change(self):
        rule = RateOfChangeRule("temp_rate", "temperature", max_delta=3.0)
        rule.evaluate(_reading(22.0))
        alert = rule.evaluate(_reading(28.0))
        assert alert is not None
        assert alert.actual_value == 6.0


# ======================================================================
# StaleDataRule
# ======================================================================


class TestStaleDataRule:
    def test_no_alert_on_first_reading(self):
        rule = StaleDataRule("stale", "temperature", max_age_seconds=1.0)
        assert rule.evaluate(_reading(22.0)) is None

    def test_no_alert_within_timeout(self):
        rule = StaleDataRule("stale", "temperature", max_age_seconds=10.0)
        rule.evaluate(_reading(22.0))
        assert rule.evaluate(_reading(23.0)) is None

    def test_alert_after_timeout(self):
        rule = StaleDataRule("stale", "temperature", max_age_seconds=0.01)
        rule.evaluate(_reading(22.0))
        time.sleep(0.02)
        alert = rule.evaluate(_reading(23.0))
        assert alert is not None


# ======================================================================
# AlertEngine
# ======================================================================


class TestAlertEngine:
    def test_add_rule_and_evaluate(self):
        engine = AlertEngine(cooldown_seconds=0)
        engine.add_rule(ThresholdRule("temp_high", "temperature", threshold=30.0))
        alerts = engine.evaluate(_reading(35.0))
        assert len(alerts) == 1

    def test_cooldown_prevents_duplicate(self):
        engine = AlertEngine(cooldown_seconds=60)
        engine.add_rule(ThresholdRule("temp_high", "temperature", threshold=30.0))
        engine.evaluate(_reading(35.0))
        # Second evaluation within cooldown
        alerts = engine.evaluate(_reading(36.0))
        assert len(alerts) == 0

    def test_multiple_rules(self):
        engine = AlertEngine(cooldown_seconds=0)
        engine.add_rule(ThresholdRule("temp_high", "temperature", threshold=30.0))
        engine.add_rule(ThresholdRule("temp_critical", "temperature", threshold=40.0, severity=AlertSeverity.CRITICAL))
        alerts = engine.evaluate(_reading(45.0))
        assert len(alerts) == 2

    def test_saves_alerts_to_storage(self):
        storage = MagicMock()
        engine = AlertEngine(storage=storage, cooldown_seconds=0)
        engine.add_rule(ThresholdRule("temp_high", "temperature", threshold=30.0))
        engine.evaluate(_reading(35.0))
        storage.save_alert.assert_called_once()

    def test_rule_count(self):
        engine = AlertEngine()
        assert engine.rule_count == 0
        engine.add_rule(ThresholdRule("r1", "temperature", threshold=30.0))
        assert engine.rule_count == 1
