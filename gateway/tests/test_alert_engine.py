import time
import pytest
from src.alert_engine import AlertEngine


class TestAlertEngine:
    def test_add_and_get_rules(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "gt", 30.0)
        rules = engine.get_active_rules()
        assert len(rules) == 1
        assert rules[0]["rule_id"] == "r1"

    def test_remove_rule(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "gt", 30.0)
        assert engine.remove_rule("r1") is True
        assert engine.get_active_rules() == []

    def test_remove_nonexistent(self):
        engine = AlertEngine()
        assert engine.remove_rule("nope") is False

    def test_evaluate_gt(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "gt", 30.0, severity="high")
        alerts = engine.evaluate("temp-1", 35.0)
        assert len(alerts) == 1
        assert alerts[0]["severity"] == "high"
        assert alerts[0]["current_value"] == 35.0

    def test_evaluate_gt_not_triggered(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "gt", 30.0)
        alerts = engine.evaluate("temp-1", 25.0)
        assert len(alerts) == 0

    def test_evaluate_lt(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "lt", 5.0)
        alerts = engine.evaluate("temp-1", 3.0)
        assert len(alerts) == 1

    def test_evaluate_eq(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "eq", 22.0)
        assert len(engine.evaluate("temp-1", 22.0)) == 1
        assert len(engine.evaluate("temp-1", 23.0)) == 0

    def test_evaluate_range_outside(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "range", 20.0, threshold_max=30.0)
        alerts = engine.evaluate("temp-1", 35.0)
        assert len(alerts) == 1

    def test_evaluate_range_inside(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "range", 20.0, threshold_max=30.0)
        alerts = engine.evaluate("temp-1", 25.0)
        assert len(alerts) == 0

    def test_cooldown_blocks_second_trigger(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "gt", 30.0, cooldown_minutes=30)
        assert len(engine.evaluate("temp-1", 35.0)) == 1
        # Second evaluation within cooldown should NOT trigger
        assert len(engine.evaluate("temp-1", 35.0)) == 0

    def test_cooldown_expired(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "gt", 30.0, cooldown_minutes=0)
        assert len(engine.evaluate("temp-1", 35.0)) == 1
        # cooldown_minutes=0 → 0 seconds cooldown, immediately re-triggerable
        assert len(engine.evaluate("temp-1", 35.0)) == 1

    def test_get_active_rules_by_sensor(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "gt", 30.0)
        engine.add_rule("r2", "hum-1", "lt", 20.0)
        assert len(engine.get_active_rules("temp-1")) == 1
        assert len(engine.get_active_rules("hum-1")) == 1
        assert len(engine.get_active_rules("nope")) == 0

    def test_evaluate_wrong_sensor(self):
        engine = AlertEngine()
        engine.add_rule("r1", "temp-1", "gt", 30.0)
        alerts = engine.evaluate("hum-1", 35.0)
        assert len(alerts) == 0
