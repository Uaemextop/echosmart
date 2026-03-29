"""Pydantic v2 schemas for alert API payloads.

Each schema serves a specific role in the request/response cycle:

- ``AlertRuleCreate`` — validates incoming ``POST /rules`` bodies.
- ``AlertResponse`` — serialises ORM models for outgoing JSON.
- ``AlertAcknowledge`` — validates ``POST /{id}/acknowledge`` bodies.
- ``AlertStatsResponse`` — serialises aggregate statistics.

All response schemas use ``from_attributes = True`` so they can be
constructed directly from SQLAlchemy model instances via
:meth:`model_validate`.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ------------------------------------------------------------------
# Request schemas
# ------------------------------------------------------------------

class AlertRuleCreate(BaseModel):
    """Payload for creating a new alert rule.

    Attributes:
        sensor_id: The sensor this rule monitors.
        rule_name: Human-readable rule label.
        condition: Comparison operator — one of ``gt``, ``lt``,
            ``eq``, or ``out_of_range``.
        threshold: Numeric threshold value.
        severity: Alert severity — one of ``critical``, ``high``,
            ``medium``, or ``low``.
    """

    sensor_id: UUID
    rule_name: str = Field(..., min_length=1, max_length=255)
    condition: str = Field(..., min_length=1, max_length=50)
    threshold: float
    severity: str = Field(..., min_length=1, max_length=20)

    model_config = {"extra": "forbid"}

    @field_validator("condition")
    @classmethod
    def _validate_condition(cls, value: str) -> str:
        allowed = {"gt", "lt", "eq", "out_of_range"}
        normalised = value.strip().lower()
        if normalised not in allowed:
            raise ValueError(
                f"Condition must be one of: {', '.join(sorted(allowed))}"
            )
        return normalised

    @field_validator("severity")
    @classmethod
    def _validate_severity(cls, value: str) -> str:
        allowed = {"critical", "high", "medium", "low"}
        normalised = value.strip().lower()
        if normalised not in allowed:
            raise ValueError(
                f"Severity must be one of: {', '.join(sorted(allowed))}"
            )
        return normalised


class AlertAcknowledge(BaseModel):
    """Payload for acknowledging an alert.

    The ``acknowledged_by`` field is optional — when omitted the
    router uses the current user's ID from the JWT claims.

    Attributes:
        acknowledged_by: Override user ID for the acknowledgement.
    """

    acknowledged_by: UUID | None = None

    model_config = {"extra": "forbid"}


# ------------------------------------------------------------------
# Response schemas
# ------------------------------------------------------------------

class AlertResponse(BaseModel):
    """Outgoing representation of an alert.

    Attributes:
        id: Unique alert identifier.
        sensor_id: The monitored sensor.
        tenant_id: Owning tenant.
        rule_name: Human-readable rule label.
        condition: Comparison operator.
        threshold: Numeric threshold value.
        severity: Alert severity level.
        is_active: Whether the alert is still active (unresolved).
        acknowledged: Whether a user has acknowledged the alert.
        triggered_at: When the alert was triggered.
        acknowledged_at: When the alert was acknowledged (if ever).
    """

    id: UUID
    sensor_id: UUID
    tenant_id: UUID
    rule_name: str
    condition: str
    threshold: float
    severity: str
    is_active: bool
    acknowledged: bool
    triggered_at: datetime
    acknowledged_at: datetime | None = None

    model_config = {"from_attributes": True}


class SeverityBreakdown(BaseModel):
    """Per-severity counts used inside :class:`AlertStatsResponse`.

    Attributes:
        critical: Number of critical-severity alerts.
        high: Number of high-severity alerts.
        medium: Number of medium-severity alerts.
        low: Number of low-severity alerts.
    """

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0

    model_config = {"from_attributes": True}


class AlertStatsResponse(BaseModel):
    """Aggregate alert statistics for a tenant.

    Attributes:
        total: Total number of alerts.
        active: Number of currently active (unresolved) alerts.
        acknowledged: Number of acknowledged alerts.
        by_severity: Breakdown by severity level.
    """

    total: int
    active: int
    acknowledged: int
    by_severity: SeverityBreakdown

    model_config = {"from_attributes": True}
