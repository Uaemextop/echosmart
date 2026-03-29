"""User-specific data-access layer.

Extends :class:`~src.shared.repository.BaseRepository` with queries
that the auth domain needs beyond generic CRUD:

- look-up by email (login, duplicate-check)
- look-up by serial number
- stamp ``last_login``

All write operations use :meth:`Session.flush` so callers can batch
several mutations inside a single transaction managed by the service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.user import User
from src.shared.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for :class:`User` entities.

    Inherits ``get_by_id``, ``get_all``, ``create``, ``update``, and
    ``delete`` from ``BaseRepository``.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_email(self, email: str) -> User | None:
        """Find a user by their unique e-mail address.

        The comparison is **case-insensitive** (lowered before query).

        Args:
            email: The e-mail to search for.

        Returns:
            The matching :class:`User`, or ``None``.
        """
        return (
            self.db.query(User)
            .filter(User.email == email.lower().strip())
            .first()
        )

    def get_by_serial_number(self, serial: str) -> User | None:
        """Find a user by the serial number used during registration.

        Args:
            serial: The kit serial code (e.g. ``"ES-202603-0001"``).

        Returns:
            The matching :class:`User`, or ``None``.
        """
        return (
            self.db.query(User)
            .filter(User.serial_number == serial)
            .first()
        )

    def update_last_login(self, user_id: UUID) -> None:
        """Set ``last_login`` to the current UTC time.

        The change is flushed but **not** committed — the service layer
        owns the transaction boundary.

        Args:
            user_id: Primary key of the user to update.
        """
        user = self.get_by_id(user_id)
        if user is not None:
            user.last_login = datetime.now(timezone.utc)
            self.db.flush()
