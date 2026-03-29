"""Gateway service — business logic and use cases.

``GatewayService`` orchestrates every gateway-related operation:

- Gateway CRUD (create, read, update, delete).
- API key generation for device authentication.
- Heartbeat processing and status management.

**Transaction policy:** The service owns ``commit`` / ``rollback``
because write operations may span multiple aggregates.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from src.gateways.repository import GatewayRepository
from src.models.gateway import Gateway, GatewayStatus
from src.shared.exceptions import NotFoundError, ValidationError


class GatewayService:
    """High-level gateway use-case orchestrator.

    Args:
        db: An active SQLAlchemy session — the service manages
            ``commit`` and ``rollback`` internally.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._repo = GatewayRepository(db)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_gateway(self, tenant_id: UUID, data: dict) -> Gateway:
        """Create a new gateway with an auto-generated API key.

        Args:
            tenant_id: Owning tenant's primary key.
            data: Validated gateway attributes (from ``GatewayCreate``).

        Returns:
            The newly persisted :class:`Gateway`.
        """
        data["tenant_id"] = tenant_id
        data["api_key"] = secrets.token_urlsafe(32)
        data["status"] = GatewayStatus.OFFLINE

        gateway = self._repo.create(data)
        self.db.commit()
        self.db.refresh(gateway)
        return gateway

    def get_gateway(self, gateway_id: UUID) -> Gateway:
        """Retrieve a single gateway by ID.

        Args:
            gateway_id: The gateway's primary key.

        Returns:
            The :class:`Gateway` instance.

        Raises:
            NotFoundError: If no gateway matches the given ID.
        """
        return self._repo.get_by_id_or_raise(gateway_id)

    def list_gateways(self, tenant_id: UUID) -> list[Gateway]:
        """List all gateways for a tenant.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            A list of :class:`Gateway` instances ordered by name.
        """
        return self._repo.get_by_tenant(tenant_id)

    def update_gateway(self, gateway_id: UUID, data: dict) -> Gateway:
        """Update an existing gateway.

        Only the keys present in *data* are modified.

        Args:
            gateway_id: The gateway's primary key.
            data: Partial update attributes (from ``GatewayUpdate``).

        Returns:
            The updated :class:`Gateway`.

        Raises:
            NotFoundError: If the gateway does not exist.
        """
        self._repo.get_by_id_or_raise(gateway_id)
        updated = self._repo.update(gateway_id, data)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def delete_gateway(self, gateway_id: UUID) -> bool:
        """Delete a gateway by ID.

        Args:
            gateway_id: The gateway's primary key.

        Returns:
            ``True`` if the gateway was deleted.

        Raises:
            NotFoundError: If the gateway does not exist.
        """
        self._repo.get_by_id_or_raise(gateway_id)
        result = self._repo.delete(gateway_id)
        self.db.commit()
        return result

    # ------------------------------------------------------------------
    # Status & heartbeat
    # ------------------------------------------------------------------

    def update_status(self, gateway_id: UUID, status_data: dict) -> Gateway:
        """Update gateway status from a heartbeat payload.

        Marks the gateway as online/offline and records the IP address
        and firmware version reported by the device.

        Args:
            gateway_id: The gateway's primary key.
            status_data: Validated status attributes (from
                ``GatewayStatusUpdate``).

        Returns:
            The updated :class:`Gateway`.

        Raises:
            NotFoundError: If the gateway does not exist.
        """
        self._repo.get_by_id_or_raise(gateway_id)

        update_fields: dict = {
            "is_online": status_data["is_online"],
            "last_seen": datetime.now(timezone.utc),
            "status": GatewayStatus.ONLINE if status_data["is_online"] else GatewayStatus.OFFLINE,
        }

        if status_data.get("ip_address"):
            update_fields["ip_address"] = status_data["ip_address"]

        if status_data.get("firmware_version"):
            update_fields["firmware_version"] = status_data["firmware_version"]

        updated = self._repo.update(gateway_id, update_fields)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def get_gateway_by_api_key(self, api_key: str) -> Gateway:
        """Look up a gateway by its API key.

        Used during device authentication to resolve which gateway
        is connecting.

        Args:
            api_key: The gateway's unique API key.

        Returns:
            The matching :class:`Gateway`.

        Raises:
            NotFoundError: If no gateway matches the API key.
        """
        gateway = self._repo.get_by_api_key(api_key)
        if gateway is None:
            raise NotFoundError("Gateway", api_key)
        return gateway
