"""Alert service — business logic and use cases.

``AlertService`` orchestrates every alert-related operation:

- Rule creation and alert triggering.
- Listing with optional severity / active-status filters.
- Acknowledgement and resolution workflows.
- Automatic evaluation of sensor readings against alert rules.
- Aggregate statistics for dashboards.

**Transaction policy:** The service owns ``commit`` / ``rollback``
because write operations may span multiple aggregates (e.g.
``evaluate_reading`` can create several alerts in one batch).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from src.alerts.repository import AlertRepository
from src.models.alert import Alert
from src.shared.exceptions import NotFoundError, ValidationError

_VALID_CONDITIONS: set[str] = {"gt", "lt", "eq", "out_of_range"}
_VALID_SEVERITIES: set[str] = {"critical", "high", "medium", "low"}


class AlertService:
    """High-level alert use-case orchestrator.

    Args:
        db: An active SQLAlchemy session — the service manages
            ``commit`` and ``rollback`` internally.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._alerts = AlertRepository(db)

    # ------------------------------------------------------------------
    # Alert CRUD
    # ------------------------------------------------------------------

    def create_alert(self, tenant_id: UUID, data: dict) -> Alert:
        """Create a new alert rule entry.

        The ``tenant_id`` is injected by the router from the
        authenticated user's claims — it is *not* accepted from the
        request body.

        Args:
            tenant_id: Owning tenant's primary key.
            data: Validated alert attributes (from ``AlertRuleCreate``).

        Returns:
            The newly persisted :class:`Alert`.

        Raises:
            ValidationError: If ``condition`` or ``severity`` values
                are not in the allowed set.
        """
        condition = data.get("condition", "")
        if condition not in _VALID_CONDITIONS:
            raise ValidationError(
                f"Condition must be one of: {', '.join(sorted(_VALID_CONDITIONS))}",
                field="condition",
            )

        severity = data.get("severity", "")
        if severity not in _VALID_SEVERITIES:
            raise ValidationError(
                f"Severity must be one of: {', '.join(sorted(_VALID_SEVERITIES))}",
                field="severity",
            )

        data["tenant_id"] = tenant_id
        data.setdefault("is_active", True)
        data.setdefault("acknowledged", False)

        alert = self._alerts.create(data)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def list_alerts(
        self,
        tenant_id: UUID,
        severity: str | None = None,
        is_active: bool | None = None,
    ) -> list[Alert]:
        """List alerts for a tenant with optional filters.

        Args:
            tenant_id: The tenant's primary key.
            severity: If provided, only return alerts of this severity.
            is_active: If provided, filter by active/resolved status.

        Returns:
            A list of :class:`Alert` instances matching the criteria.

        Raises:
            ValidationError: If an invalid ``severity`` value is given.
        """
        if severity is not None and severity not in _VALID_SEVERITIES:
            raise ValidationError(
                f"Severity must be one of: {', '.join(sorted(_VALID_SEVERITIES))}",
                field="severity",
            )

        # Prefer the most specific query available.
        if severity is not None:
            return self._alerts.get_by_severity(tenant_id, severity)

        if is_active is True:
            return self._alerts.get_active_by_tenant(tenant_id)

        # Default: return all alerts for the tenant.
        return self._alerts.get_all(filters={"tenant_id": tenant_id})

    def get_alert(self, alert_id: UUID) -> Alert:
        """Retrieve a single alert by ID.

        Args:
            alert_id: The alert's primary key.

        Returns:
            The :class:`Alert` instance.

        Raises:
            NotFoundError: If no alert matches the given ID.
        """
        return self._alerts.get_by_id_or_raise(alert_id)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def acknowledge_alert(self, alert_id: UUID, user_id: UUID) -> Alert:
        """Acknowledge an alert.

        Marks the alert as seen by the given user, recording the
        timestamp of acknowledgement.

        Args:
            alert_id: The alert's primary key.
            user_id: The user performing the acknowledgement.

        Returns:
            The updated :class:`Alert`.

        Raises:
            NotFoundError: If the alert does not exist.
            ValidationError: If the alert is already acknowledged.
        """
        alert = self._alerts.get_by_id_or_raise(alert_id)

        if alert.acknowledged:
            raise ValidationError(
                "Alert has already been acknowledged",
                field="acknowledged",
            )

        updated = self._alerts.acknowledge(alert_id, user_id)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def resolve_alert(self, alert_id: UUID) -> Alert:
        """Resolve (deactivate) an alert.

        Args:
            alert_id: The alert's primary key.

        Returns:
            The resolved :class:`Alert`.

        Raises:
            NotFoundError: If the alert does not exist.
            ValidationError: If the alert is already resolved.
        """
        alert = self._alerts.get_by_id_or_raise(alert_id)

        if not alert.is_active:
            raise ValidationError(
                "Alert is already resolved",
                field="is_active",
            )

        resolved = self._alerts.resolve(alert_id)
        self.db.commit()
        self.db.refresh(resolved)
        return resolved

    # ------------------------------------------------------------------
    # Rule evaluation
    # ------------------------------------------------------------------

    def evaluate_reading(
        self,
        sensor_id: UUID,
        value: float,
        rules: list[dict],
    ) -> list[Alert]:
        """Evaluate a sensor reading against a set of alert rules.

        For each rule whose condition is satisfied by *value*, a new
        active :class:`Alert` is created.  All triggered alerts are
        committed in a single transaction.

        Supported conditions:

        - ``gt``  — *value* > threshold
        - ``lt``  — *value* < threshold
        - ``eq``  — *value* == threshold
        - ``out_of_range`` — *value* < threshold_low **or**
          *value* > threshold_high  (rule must include both
          ``threshold_low`` and ``threshold_high``; ``threshold``
          is ignored).

        Args:
            sensor_id: The sensor that produced the reading.
            value: The numeric reading value.
            rules: A list of rule dicts, each containing at least
                ``rule_name``, ``condition``, ``threshold``,
                ``severity``, and ``tenant_id``.

        Returns:
            A list of newly created :class:`Alert` instances (may be
            empty if no rules triggered).
        """
        triggered: list[Alert] = []

        for rule in rules:
            if self._condition_met(value, rule):
                alert = self._alerts.create({
                    "sensor_id": sensor_id,
                    "tenant_id": rule["tenant_id"],
                    "rule_name": rule["rule_name"],
                    "condition": rule["condition"],
                    "threshold": rule["threshold"],
                    "severity": rule["severity"],
                    "is_active": True,
                    "acknowledged": False,
                })
                triggered.append(alert)

        if triggered:
            self.db.commit()

        return triggered

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_alert_stats(self, tenant_id: UUID) -> dict:
        """Return aggregate alert statistics for a tenant.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            A dict with keys ``total``, ``active``, ``acknowledged``,
            and ``by_severity``.
        """
        return self._alerts.get_stats(tenant_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _condition_met(value: float, rule: dict) -> bool:
        """Check whether *value* satisfies the rule's condition.

        Args:
            value: The sensor reading value.
            rule: A rule dict with ``condition`` and ``threshold``
                keys (and optionally ``threshold_low`` /
                ``threshold_high`` for ``out_of_range``).

        Returns:
            ``True`` if the condition is met (alert should fire).
        """
        condition = rule.get("condition", "")
        threshold = rule.get("threshold", 0.0)

        if condition == "gt":
            return value > threshold
        if condition == "lt":
            return value < threshold
        if condition == "eq":
            return value == threshold
        if condition == "out_of_range":
            low = rule.get("threshold_low", threshold)
            high = rule.get("threshold_high", threshold)
            return value < low or value > high

        return False
