"""Alert entity — Pure domain object."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class AlertSeverity(str, Enum):
    """Alert severity levels ordered by criticality."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents an alert triggered by a sensor reading violating a rule.

    Attributes:
        id: Unique alert identifier.
        sensor_id: Sensor that triggered the alert.
        sensor_type: Type of sensor measurement.
        rule_name: Name of the rule that was violated.
        severity: Severity level of the alert.
        message: Human-readable description.
        threshold: Rule threshold that was violated.
        actual_value: The actual sensor value that triggered the alert.
        created_at: UTC datetime when the alert was created.
        acknowledged: Whether the alert has been acknowledged by a user.
        synced: Whether the alert has been synced to the cloud.
    """

    sensor_id: str
    sensor_type: str
    rule_name: str
    severity: AlertSeverity
    message: str
    threshold: float
    actual_value: float
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged: bool = False
    synced: bool = False

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "threshold": self.threshold,
            "actual_value": self.actual_value,
            "created_at": self.created_at.isoformat(),
            "acknowledged": self.acknowledged,
            "synced": self.synced,
        }
