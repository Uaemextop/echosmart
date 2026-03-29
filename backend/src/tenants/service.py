"""Tenant service — business logic and use cases.

``TenantService`` orchestrates tenant-related operations:

- Tenant profile retrieval and updates.
- Branding customisation.
- Usage statistics aggregation.

**Transaction policy:** The service owns ``commit`` / ``rollback``
because write operations must be atomic.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from src.models.gateway import Gateway
from src.models.sensor import Sensor
from src.models.tenant import Tenant
from src.models.user import User
from src.shared.exceptions import NotFoundError
from src.tenants.repository import TenantRepository


class TenantService:
    """High-level tenant use-case orchestrator.

    Args:
        db: An active SQLAlchemy session — the service manages
            ``commit`` and ``rollback`` internally.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._repo = TenantRepository(db)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_tenant(self, tenant_id: UUID) -> Tenant:
        """Retrieve a single tenant by ID.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            The :class:`Tenant` instance.

        Raises:
            NotFoundError: If no tenant matches the given ID.
        """
        return self._repo.get_by_id_or_raise(tenant_id)

    def get_usage(self, tenant_id: UUID) -> dict:
        """Compute usage statistics for a tenant.

        Counts users, gateways, and sensors belonging to the tenant
        using efficient COUNT queries.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            A dict with ``total_users``, ``total_gateways``, and
            ``total_sensors``.

        Raises:
            NotFoundError: If the tenant does not exist.
        """
        self._repo.get_by_id_or_raise(tenant_id)

        total_users = (
            self.db.query(sa_func.count())
            .select_from(User)
            .filter(User.tenant_id == tenant_id)
            .scalar() or 0
        )
        total_gateways = (
            self.db.query(sa_func.count())
            .select_from(Gateway)
            .filter(Gateway.tenant_id == tenant_id)
            .scalar() or 0
        )
        total_sensors = (
            self.db.query(sa_func.count())
            .select_from(Sensor)
            .filter(Sensor.tenant_id == tenant_id)
            .scalar() or 0
        )

        return {
            "total_users": total_users,
            "total_gateways": total_gateways,
            "total_sensors": total_sensors,
        }

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def update_tenant(self, tenant_id: UUID, data: dict) -> Tenant:
        """Update a tenant's profile.

        Only the keys present in *data* are modified.

        Args:
            tenant_id: The tenant's primary key.
            data: Partial update attributes (from ``TenantUpdate``).

        Returns:
            The updated :class:`Tenant`.

        Raises:
            NotFoundError: If the tenant does not exist.
        """
        self._repo.get_by_id_or_raise(tenant_id)
        updated = self._repo.update(tenant_id, data)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def update_branding(self, tenant_id: UUID, branding_data: dict) -> Tenant:
        """Update a tenant's branding configuration.

        Merges the provided branding fields with any existing branding
        data so that partial updates are supported.

        Args:
            tenant_id: The tenant's primary key.
            branding_data: Branding attributes (from ``TenantBranding``).

        Returns:
            The updated :class:`Tenant`.

        Raises:
            NotFoundError: If the tenant does not exist.
        """
        tenant = self._repo.get_by_id_or_raise(tenant_id)

        # Merge with existing branding
        current_branding = tenant.branding or {}
        for key, value in branding_data.items():
            if value is not None:
                current_branding[key] = value

        updated = self._repo.update(tenant_id, {"branding": current_branding})
        self.db.commit()
        self.db.refresh(updated)
        return updated
