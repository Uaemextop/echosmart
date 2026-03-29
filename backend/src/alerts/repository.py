"""Alert data-access layer.

Extends :class:`~src.shared.repository.BaseRepository` with
domain-specific queries for alert management: filtering by tenant,
severity, and acknowledgement status, plus aggregate statistics.

All write operations use :meth:`Session.flush` so callers can batch
several mutations inside a single transaction managed by the service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import case, func as sa_func
from sqlalchemy.orm import Session

from src.models.alert import Alert
from src.shared.repository import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    """Repository for :class:`Alert` entities.

    Inherits ``get_by_id``, ``get_all``, ``create``, ``update``, and
    ``delete`` from ``BaseRepository``.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Alert, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_active_by_tenant(self, tenant_id: UUID) -> list[Alert]:
        """Return all active (unresolved) alerts for a tenant.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            A list of active alerts ordered by most-recently triggered
            first.
        """
        return (
            self.db.query(Alert)
            .filter(Alert.tenant_id == tenant_id, Alert.is_active.is_(True))
            .order_by(Alert.triggered_at.desc())
            .all()
        )

    def get_unacknowledged(self, tenant_id: UUID) -> list[Alert]:
        """Return active alerts that have not been acknowledged yet.

        Useful for operator dashboards that highlight items needing
        human attention.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            A list of unacknowledged alerts, newest first.
        """
        return (
            self.db.query(Alert)
            .filter(
                Alert.tenant_id == tenant_id,
                Alert.is_active.is_(True),
                Alert.acknowledged.is_(False),
            )
            .order_by(Alert.triggered_at.desc())
            .all()
        )

    def get_by_severity(self, tenant_id: UUID, severity: str) -> list[Alert]:
        """Return alerts filtered by severity level.

        Args:
            tenant_id: The tenant's primary key.
            severity: One of ``critical``, ``high``, ``medium``, or
                ``low``.

        Returns:
            A list of matching alerts, newest first.
        """
        return (
            self.db.query(Alert)
            .filter(Alert.tenant_id == tenant_id, Alert.severity == severity)
            .order_by(Alert.triggered_at.desc())
            .all()
        )

    def acknowledge(self, alert_id: UUID, user_id: UUID) -> Alert | None:
        """Mark an alert as acknowledged by a user.

        Sets ``acknowledged``, ``acknowledged_by``, and
        ``acknowledged_at`` in a single flush.

        Args:
            alert_id: The alert's primary key.
            user_id: The user performing the acknowledgement.

        Returns:
            The updated :class:`Alert`, or ``None`` if not found.
        """
        return self.update(
            alert_id,
            {
                "acknowledged": True,
                "acknowledged_by": user_id,
                "acknowledged_at": datetime.now(timezone.utc),
            },
        )

    def resolve(self, alert_id: UUID) -> Alert | None:
        """Deactivate an alert (mark it as resolved).

        Args:
            alert_id: The alert's primary key.

        Returns:
            The updated :class:`Alert`, or ``None`` if not found.
        """
        return self.update(alert_id, {"is_active": False})

    def get_stats(self, tenant_id: UUID) -> dict:
        """Compute aggregate alert statistics for a tenant.

        Uses a single query with conditional aggregation to avoid
        multiple round-trips.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            A dict with keys ``total``, ``active``, ``acknowledged``,
            and ``by_severity`` (a breakdown by severity level).
        """
        row = (
            self.db.query(
                sa_func.count(Alert.id).label("total"),
                sa_func.count(
                    case((Alert.is_active.is_(True), Alert.id))
                ).label("active"),
                sa_func.count(
                    case((Alert.acknowledged.is_(True), Alert.id))
                ).label("acknowledged"),
                sa_func.count(
                    case((Alert.severity == "critical", Alert.id))
                ).label("critical"),
                sa_func.count(
                    case((Alert.severity == "high", Alert.id))
                ).label("high"),
                sa_func.count(
                    case((Alert.severity == "medium", Alert.id))
                ).label("medium"),
                sa_func.count(
                    case((Alert.severity == "low", Alert.id))
                ).label("low"),
            )
            .filter(Alert.tenant_id == tenant_id)
            .one()
        )

        return {
            "total": row.total,
            "active": row.active,
            "acknowledged": row.acknowledged,
            "by_severity": {
                "critical": row.critical,
                "high": row.high,
                "medium": row.medium,
                "low": row.low,
            },
        }
