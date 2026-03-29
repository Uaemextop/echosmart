"""Admin user data-access layer.

Extends :class:`~src.shared.repository.BaseRepository` with
domain-specific queries for administrative user management: listing
by tenant, counting, and full-text search.

All write operations use :meth:`Session.flush` so callers can batch
several mutations inside a single transaction managed by the service.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func as sa_func, or_
from sqlalchemy.orm import Session

from src.models.user import User
from src.shared.repository import BaseRepository


class AdminUserRepository(BaseRepository[User]):
    """Repository for admin-level :class:`User` operations.

    Inherits ``get_by_id``, ``get_all``, ``create``, ``update``, and
    ``delete`` from ``BaseRepository``.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_tenant(
        self,
        tenant_id: UUID,
        role: str | None = None,
    ) -> list[User]:
        """Return all users belonging to a tenant, optionally by role.

        Args:
            tenant_id: The tenant's primary key.
            role: Optional role filter (e.g. ``"admin"``, ``"user"``).

        Returns:
            A list of users ordered by full name.
        """
        query = (
            self.db.query(User)
            .filter(User.tenant_id == tenant_id)
        )
        if role is not None:
            query = query.filter(User.role == role)
        return query.order_by(User.full_name).all()

    def count_by_tenant(self, tenant_id: UUID) -> int:
        """Count the number of users in a tenant.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            The total number of users.
        """
        return (
            self.db.query(sa_func.count())
            .select_from(User)
            .filter(User.tenant_id == tenant_id)
            .scalar() or 0
        )

    def search_users(self, tenant_id: UUID, query: str) -> list[User]:
        """Search users by email or full name (case-insensitive).

        Args:
            tenant_id: The tenant's primary key.
            query: Search term to match against email and full_name.

        Returns:
            A list of matching users ordered by full name.
        """
        pattern = f"%{query}%"
        return (
            self.db.query(User)
            .filter(
                User.tenant_id == tenant_id,
                or_(
                    User.email.ilike(pattern),
                    User.full_name.ilike(pattern),
                ),
            )
            .order_by(User.full_name)
            .all()
        )
