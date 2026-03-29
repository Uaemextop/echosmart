"""Generic base repository for SQLAlchemy models.

Implements the *Repository* pattern — a thin persistence abstraction that
keeps SQLAlchemy details out of service / use-case code.

Feature modules extend ``BaseRepository`` to add domain-specific queries
while inheriting standard CRUD operations for free.

Example::

    class SensorRepository(BaseRepository[Sensor]):
        \"\"\"Sensor-specific queries.\"\"\"

        def find_online(self) -> list[Sensor]:
            return self.db.query(self.model).filter_by(is_online=True).all()


    # In a dependency or service:
    repo = SensorRepository(Sensor, db)
    sensor = repo.get_by_id(sensor_id)
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from src.shared.exceptions import NotFoundError

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic CRUD repository backed by a SQLAlchemy ``Session``.

    Attributes:
        model: The SQLAlchemy ORM class this repository manages.
        db: The active database session.
    """

    def __init__(self, model: type[T], db: Session) -> None:
        self.model = model
        self.db = db

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, entity_id: UUID) -> T | None:
        """Fetch a single record by primary key.

        Args:
            entity_id: The UUID primary key.

        Returns:
            The model instance, or ``None`` if not found.
        """
        return self.db.query(self.model).filter_by(id=entity_id).first()

    def get_by_id_or_raise(self, entity_id: UUID) -> T:
        """Fetch a single record by primary key, raising on miss.

        Args:
            entity_id: The UUID primary key.

        Returns:
            The model instance.

        Raises:
            NotFoundError: If no record matches *entity_id*.
        """
        instance = self.get_by_id(entity_id)
        if instance is None:
            raise NotFoundError(self.model.__name__, str(entity_id))
        return instance

    def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> list[T]:
        """Return a paginated, optionally filtered list of records.

        Args:
            skip: Number of rows to skip (offset).
            limit: Maximum rows to return.
            filters: Column-name → value equality filters applied via
                ``filter_by``.

        Returns:
            A list of model instances (may be empty).
        """
        query = self.db.query(self.model)
        if filters:
            query = query.filter_by(**filters)
        return query.offset(skip).limit(limit).all()

    def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count records, optionally applying equality filters.

        Args:
            filters: Column-name → value equality filters.

        Returns:
            The total number of matching rows.
        """
        query = self.db.query(sa_func.count()).select_from(self.model)
        if filters:
            query = query.filter_by(**filters)
        return query.scalar() or 0

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, data: dict[str, Any]) -> T:
        """Insert a new record from a plain dictionary.

        The session is flushed so that server-side defaults (e.g. ``id``,
        ``created_at``) are populated, but the caller is responsible for
        committing the transaction.

        Args:
            data: Column-name → value mapping.

        Returns:
            The newly created and refreshed model instance.
        """
        instance = self.model(**data)
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def update(self, entity_id: UUID, data: dict[str, Any]) -> T | None:
        """Update an existing record.

        Only the keys present in *data* are modified; ``None`` values
        are set explicitly (use ``dict.pop`` before calling if you want
        to skip them).

        Args:
            entity_id: Primary key of the record to update.
            data: Column-name → new value mapping.

        Returns:
            The updated instance, or ``None`` if not found.
        """
        instance = self.get_by_id(entity_id)
        if instance is None:
            return None
        for key, value in data.items():
            setattr(instance, key, value)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def delete(self, entity_id: UUID) -> bool:
        """Delete a record by primary key.

        Args:
            entity_id: Primary key of the record to remove.

        Returns:
            ``True`` if a record was deleted, ``False`` if not found.
        """
        instance = self.get_by_id(entity_id)
        if instance is None:
            return False
        self.db.delete(instance)
        self.db.flush()
        return True
