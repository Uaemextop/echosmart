"""Tenant data-access layer.

Extends :class:`~src.shared.repository.BaseRepository` with
domain-specific queries for tenant management: lookup by slug
and listing active tenants.

All write operations use :meth:`Session.flush` so callers can batch
several mutations inside a single transaction managed by the service.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.models.tenant import Tenant
from src.shared.repository import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Repository for :class:`Tenant` entities.

    Inherits ``get_by_id``, ``get_all``, ``create``, ``update``, and
    ``delete`` from ``BaseRepository``.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Tenant, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_slug(self, slug: str) -> Tenant | None:
        """Find a tenant by its unique slug.

        Args:
            slug: The URL-friendly tenant identifier.

        Returns:
            The matching :class:`Tenant`, or ``None``.
        """
        return (
            self.db.query(Tenant)
            .filter(Tenant.slug == slug)
            .first()
        )

    def get_active_tenants(self) -> list[Tenant]:
        """Return all active tenants.

        Returns:
            A list of active tenants ordered by name.
        """
        return (
            self.db.query(Tenant)
            .filter(Tenant.is_active.is_(True))
            .order_by(Tenant.name)
            .all()
        )
