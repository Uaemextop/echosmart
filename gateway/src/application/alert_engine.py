"""Alert engine — Evaluates sensor readings against configurable rules.

Supports multiple rule types: threshold, range, rate-of-change, and
stale-data detection.  Each rule type is a strategy (Strategy pattern).
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from gateway.src.domain.constants import ALERT_COOLDOWN_S
from gateway.src.domain.entities.alert import Alert, AlertSeverity
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.interfaces.storage import IStorageRepository

logger = logging.getLogger(__name__)


# ======================================================================
# Rule types (Strategy pattern)
# ======================================================================


class AlertRule(ABC):
    """Base class for alert rules."""

    def __init__(
        self,
        name: str,
        sensor_type: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
    ) -> None:
        self.name = name
        self.sensor_type = sensor_type
        self.severity = severity

    @abstractmethod
    def evaluate(self, reading: SensorReading) -> Alert | None:
        """Return an Alert if the rule is violated, else None."""


class ThresholdRule(AlertRule):
    """Fires when a value exceeds (or falls below) a threshold.

    Args:
        name: Rule name.
        sensor_type: Sensor type this rule applies to.
        threshold: Numeric threshold.
        condition: ``"gt"`` (greater than) or ``"lt"`` (less than).
        severity: Alert severity.
    """

    def __init__(
        self,
        name: str,
        sensor_type: str,
        threshold: float,
        condition: str = "gt",
        severity: AlertSeverity = AlertSeverity.WARNING,
    ) -> None:
        super().__init__(name, sensor_type, severity)
        self.threshold = threshold
        self.condition = condition

    def evaluate(self, reading: SensorReading) -> Alert | None:
        if reading.sensor_type != self.sensor_type:
            return None
        violated = (
            (self.condition == "gt" and reading.value > self.threshold)
            or (self.condition == "lt" and reading.value < self.threshold)
        )
        if violated:
            return Alert(
                sensor_id=reading.sensor_id,
                sensor_type=reading.sensor_type,
                rule_name=self.name,
                severity=self.severity,
                message=f"{reading.sensor_type} value {reading.value} {self.condition} {self.threshold}",
                threshold=self.threshold,
                actual_value=reading.value,
            )
        return None


class RangeRule(AlertRule):
    """Fires when a value is outside a [min, max] range.

    Args:
        name: Rule name.
        sensor_type: Sensor type this rule applies to.
        min_value: Lower bound.
        max_value: Upper bound.
        severity: Alert severity.
    """

    def __init__(
        self,
        name: str,
        sensor_type: str,
        min_value: float,
        max_value: float,
        severity: AlertSeverity = AlertSeverity.WARNING,
    ) -> None:
        super().__init__(name, sensor_type, severity)
        self.min_value = min_value
        self.max_value = max_value

    def evaluate(self, reading: SensorReading) -> Alert | None:
        if reading.sensor_type != self.sensor_type:
            return None
        if not (self.min_value <= reading.value <= self.max_value):
            return Alert(
                sensor_id=reading.sensor_id,
                sensor_type=reading.sensor_type,
                rule_name=self.name,
                severity=self.severity,
                message=(
                    f"{reading.sensor_type} value {reading.value} "
                    f"outside range [{self.min_value}, {self.max_value}]"
                ),
                threshold=self.max_value if reading.value > self.max_value else self.min_value,
                actual_value=reading.value,
            )
        return None


class RateOfChangeRule(AlertRule):
    """Fires when the change between consecutive readings exceeds a delta.

    Args:
        name: Rule name.
        sensor_type: Sensor type this rule applies to.
        max_delta: Maximum allowed change between reads.
        severity: Alert severity.
    """

    def __init__(
        self,
        name: str,
        sensor_type: str,
        max_delta: float,
        severity: AlertSeverity = AlertSeverity.WARNING,
    ) -> None:
        super().__init__(name, sensor_type, severity)
        self.max_delta = max_delta
        self._last_values: dict[str, float] = {}

    def evaluate(self, reading: SensorReading) -> Alert | None:
        if reading.sensor_type != self.sensor_type:
            return None
        sid = reading.sensor_id
        last = self._last_values.get(sid)
        self._last_values[sid] = reading.value
        if last is not None:
            delta = abs(reading.value - last)
            if delta > self.max_delta:
                return Alert(
                    sensor_id=sid,
                    sensor_type=reading.sensor_type,
                    rule_name=self.name,
                    severity=self.severity,
                    message=(
                        f"{reading.sensor_type} changed by {delta:.1f} "
                        f"(max={self.max_delta})"
                    ),
                    threshold=self.max_delta,
                    actual_value=delta,
                )
        return None


class StaleDataRule(AlertRule):
    """Fires when no reading has been received for a sensor within a timeout.

    Call ``evaluate`` with a synthetic or recent reading; the rule tracks
    the last-seen timestamp per sensor.

    Args:
        name: Rule name.
        sensor_type: Sensor type this rule applies to.
        max_age_seconds: Maximum allowed time between readings.
        severity: Alert severity.
    """

    def __init__(
        self,
        name: str,
        sensor_type: str,
        max_age_seconds: float = 300,
        severity: AlertSeverity = AlertSeverity.WARNING,
    ) -> None:
        super().__init__(name, sensor_type, severity)
        self.max_age_seconds = max_age_seconds
        self._last_seen: dict[str, float] = {}

    def evaluate(self, reading: SensorReading) -> Alert | None:
        if reading.sensor_type != self.sensor_type:
            return None
        now = time.monotonic()
        sid = reading.sensor_id
        last = self._last_seen.get(sid)
        self._last_seen[sid] = now
        if last is not None and (now - last) > self.max_age_seconds:
            return Alert(
                sensor_id=sid,
                sensor_type=reading.sensor_type,
                rule_name=self.name,
                severity=self.severity,
                message=(
                    f"No data from {sid} for {now - last:.0f}s "
                    f"(max={self.max_age_seconds}s)"
                ),
                threshold=self.max_age_seconds,
                actual_value=now - last,
            )
        return None


# ======================================================================
# Alert Engine (orchestrator)
# ======================================================================


class AlertEngine:
    """Evaluates readings against a set of alert rules with cooldown.

    Args:
        storage: Optional repository for persisting alerts.
        cooldown_seconds: Minimum seconds between identical alerts.
    """

    def __init__(
        self,
        storage: IStorageRepository | None = None,
        cooldown_seconds: float = ALERT_COOLDOWN_S,
    ) -> None:
        self._rules: list[AlertRule] = []
        self._storage = storage
        self._cooldown_s = cooldown_seconds
        self._last_fired: dict[str, float] = {}  # key = "sensor_id:rule_name"
        logger.info("AlertEngine initialized (cooldown=%ds).", cooldown_seconds)

    def add_rule(self, rule: AlertRule) -> None:
        """Register an alert rule."""
        self._rules.append(rule)
        logger.info("Added rule: %s (%s)", rule.name, rule.__class__.__name__)

    def evaluate(self, reading: SensorReading) -> list[Alert]:
        """Evaluate a reading against all rules. Return triggered alerts."""
        alerts: list[Alert] = []
        for rule in self._rules:
            alert = rule.evaluate(reading)
            if alert is None:
                continue
            cooldown_key = f"{alert.sensor_id}:{alert.rule_name}"
            now = time.monotonic()
            last = self._last_fired.get(cooldown_key, 0.0)
            if (now - last) < self._cooldown_s:
                continue
            self._last_fired[cooldown_key] = now
            alerts.append(alert)
            if self._storage:
                self._storage.save_alert(alert)
            logger.warning(
                "ALERT [%s] %s: %s",
                alert.severity.value.upper(),
                alert.rule_name,
                alert.message,
            )
        return alerts

    @property
    def rule_count(self) -> int:
        return len(self._rules)
