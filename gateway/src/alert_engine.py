import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertEngine:
    """Evaluates sensor readings against configurable rules."""

    def __init__(self):
        self.rules: Dict[str, dict] = {}
        self.cooldowns: Dict[str, float] = {}

    def add_rule(
        self,
        rule_id: str,
        sensor_id: str,
        condition: str,
        threshold: float,
        severity: str = "medium",
        cooldown_minutes: int = 30,
        threshold_max: float = None,
    ) -> None:
        self.rules[rule_id] = {
            "rule_id": rule_id,
            "sensor_id": sensor_id,
            "condition": condition,
            "threshold": threshold,
            "threshold_max": threshold_max,
            "severity": severity,
            "cooldown_minutes": cooldown_minutes,
        }
        logger.info("Added alert rule %s for sensor %s", rule_id, sensor_id)

    def remove_rule(self, rule_id: str) -> bool:
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.cooldowns.pop(rule_id, None)
            return True
        return False

    def evaluate(self, sensor_id: str, value: float) -> List[dict]:
        triggered = []
        for rule_id, rule in self.rules.items():
            if rule["sensor_id"] != sensor_id:
                continue
            if not self.check_cooldown(rule_id):
                continue
            if self._condition_met(rule, value):
                alert = {
                    "rule_id": rule_id,
                    "sensor_id": sensor_id,
                    "severity": rule["severity"],
                    "message": self._build_message(rule, value),
                    "current_value": value,
                    "threshold": rule["threshold"],
                }
                triggered.append(alert)
                self.cooldowns[rule_id] = time.time()
                logger.warning("Alert triggered: %s", alert["message"])
        return triggered

    def check_cooldown(self, rule_id: str) -> bool:
        last = self.cooldowns.get(rule_id)
        if last is None:
            return True
        rule = self.rules.get(rule_id)
        if rule is None:
            return True
        cooldown_secs = rule["cooldown_minutes"] * 60
        return (time.time() - last) >= cooldown_secs

    def get_active_rules(self, sensor_id: str = None) -> List[dict]:
        if sensor_id is None:
            return list(self.rules.values())
        return [r for r in self.rules.values() if r["sensor_id"] == sensor_id]

    @staticmethod
    def _condition_met(rule: dict, value: float) -> bool:
        cond = rule["condition"]
        threshold = rule["threshold"]
        if cond == "gt":
            return value > threshold
        if cond == "lt":
            return value < threshold
        if cond == "eq":
            return value == threshold
        if cond == "range":
            low = threshold
            high = rule.get("threshold_max")
            if high is None:
                return False
            return not (low <= value <= high)
        return False

    @staticmethod
    def _build_message(rule: dict, value: float) -> str:
        cond = rule["condition"]
        if cond == "gt":
            return (
                f"Sensor {rule['sensor_id']}: value {value} exceeds threshold {rule['threshold']}"
            )
        if cond == "lt":
            return (
                f"Sensor {rule['sensor_id']}: value {value} below threshold {rule['threshold']}"
            )
        if cond == "eq":
            return (
                f"Sensor {rule['sensor_id']}: value {value} equals threshold {rule['threshold']}"
            )
        if cond == "range":
            return (
                f"Sensor {rule['sensor_id']}: value {value} outside range "
                f"[{rule['threshold']}, {rule['threshold_max']}]"
            )
        return f"Sensor {rule['sensor_id']}: alert condition met (value={value})"
