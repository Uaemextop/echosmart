"""Gateway data-access layer.

Extends :class:`~src.shared.repository.BaseRepository` with
domain-specific queries for gateway management: lookup by serial
number, tenant, API key, and detection of offline devices.

All write operations use :meth:`Session.flush` so callers can batch
several mutations inside a single transaction managed by the service.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.gateway import Gateway
from src.shared.repository import BaseRepository


class GatewayRepository(BaseRepository[Gateway]):
    """Repository for :class:`Gateway` entities.

    Inherits ``get_by_id``, ``get_all``, ``create``, ``update``, and
    ``delete`` from ``BaseRepository``.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Gateway, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_serial(self, serial_number: str) -> Gateway | None:
        """Find a gateway by its unique serial number.

        Args:
            serial_number: The hardware serial number.

        Returns:
            The matching :class:`Gateway`, or ``None``.
        """
        return (
            self.db.query(Gateway)
            .filter(Gateway.serial_number == serial_number)
            .first()
        )

    def get_by_tenant(self, tenant_id: UUID) -> list[Gateway]:
        """Return all gateways belonging to a tenant.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            A list of gateways ordered by name.
        """
        return (
            self.db.query(Gateway)
            .filter(Gateway.tenant_id == tenant_id)
            .order_by(Gateway.name)
            .all()
        )

    def get_by_api_key(self, api_key: str) -> Gateway | None:
        """Find a gateway by its unique API key.

        Used during device authentication to resolve which gateway
        is connecting.

        Args:
            api_key: The gateway's API key.

        Returns:
            The matching :class:`Gateway`, or ``None``.
        """
        return (
            self.db.query(Gateway)
            .filter(Gateway.api_key == api_key)
            .first()
        )

    def update_last_seen(self, gateway_id: UUID) -> Gateway | None:
        """Update the ``last_seen`` timestamp and mark the gateway online.

        Args:
            gateway_id: The gateway's primary key.

        Returns:
            The updated :class:`Gateway`, or ``None`` if not found.
        """
        from src.models.gateway import GatewayStatus

        return self.update(
            gateway_id,
            {
                "last_seen": datetime.now(timezone.utc),
                "is_online": True,
                "status": GatewayStatus.ONLINE,
            },
        )

    def get_offline(self, threshold_minutes: int = 5) -> list[Gateway]:
        """Return gateways that have not reported within the threshold.

        A gateway is considered offline if its ``last_seen`` is older
        than ``now() - threshold_minutes`` or has never reported.

        Args:
            threshold_minutes: Minutes of silence before a gateway is
                considered offline.  Defaults to ``5``.

        Returns:
            A list of potentially offline gateways.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=threshold_minutes)
        return (
            self.db.query(Gateway)
            .filter(
                Gateway.is_online.is_(True),
                (Gateway.last_seen < cutoff) | (Gateway.last_seen.is_(None)),
            )
            .all()
        )
