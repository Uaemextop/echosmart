"""Sensor and reading data-access layer.

Extends :class:`~src.shared.repository.BaseRepository` with
domain-specific queries for sensor management and time-series readings.

All write operations use :meth:`Session.flush` so callers can batch
several mutations inside a single transaction managed by the service.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from src.models.reading import Reading
from src.models.sensor import Sensor
from src.shared.repository import BaseRepository


class SensorRepository(BaseRepository[Sensor]):
    """Repository for :class:`Sensor` entities.

    Inherits ``get_by_id``, ``get_all``, ``create``, ``update``, and
    ``delete`` from ``BaseRepository``.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Sensor, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_gateway(self, gateway_id: UUID) -> list[Sensor]:
        """Return all sensors attached to a given gateway.

        Args:
            gateway_id: The parent gateway's primary key.

        Returns:
            A list of sensors (may be empty).
        """
        return (
            self.db.query(Sensor)
            .filter(Sensor.gateway_id == gateway_id)
            .order_by(Sensor.name)
            .all()
        )

    def get_by_tenant(self, tenant_id: UUID) -> list[Sensor]:
        """Return all sensors belonging to a tenant.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            A list of sensors ordered by name.
        """
        return (
            self.db.query(Sensor)
            .filter(Sensor.tenant_id == tenant_id)
            .order_by(Sensor.name)
            .all()
        )

    def get_active_by_tenant(self, tenant_id: UUID) -> list[Sensor]:
        """Return only online sensors for a tenant.

        Useful for dashboard summaries and real-time monitoring views.

        Args:
            tenant_id: The tenant's primary key.

        Returns:
            A list of online sensors ordered by name.
        """
        return (
            self.db.query(Sensor)
            .filter(Sensor.tenant_id == tenant_id, Sensor.is_online.is_(True))
            .order_by(Sensor.name)
            .all()
        )


    def bulk_update_last_reading(
        self,
        sensor_ids: set[UUID],
        timestamp: datetime,
    ) -> None:
        """Mark multiple sensors as online with a new last-reading time.

        Uses a single UPDATE … WHERE id IN (…) to avoid N round-trips.

        Args:
            sensor_ids: Set of sensor primary keys to update.
            timestamp: The timestamp to set as ``last_reading_at``.
        """
        if not sensor_ids:
            return
        (
            self.db.query(Sensor)
            .filter(Sensor.id.in_(sensor_ids))
            .update(
                {"last_reading_at": timestamp, "is_online": True},
                synchronize_session="fetch",
            )
        )
        self.db.flush()


class ReadingRepository(BaseRepository[Reading]):
    """Repository for :class:`Reading` entities.

    Provides time-series queries on sensor readings in addition to
    the standard CRUD operations inherited from ``BaseRepository``.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Reading, db)

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_sensor(self, sensor_id: UUID, limit: int = 100) -> list[Reading]:
        """Return the most recent readings for a sensor.

        Args:
            sensor_id: The sensor's primary key.
            limit: Maximum number of readings to return (newest first).

        Returns:
            A list of readings ordered by descending timestamp.
        """
        return (
            self.db.query(Reading)
            .filter(Reading.sensor_id == sensor_id)
            .order_by(Reading.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_by_sensor_range(
        self,
        sensor_id: UUID,
        date_from: datetime,
        date_to: datetime,
    ) -> list[Reading]:
        """Return readings for a sensor within a time window.

        Args:
            sensor_id: The sensor's primary key.
            date_from: Inclusive start of the range (UTC).
            date_to: Inclusive end of the range (UTC).

        Returns:
            A list of readings ordered by ascending timestamp.
        """
        return (
            self.db.query(Reading)
            .filter(
                Reading.sensor_id == sensor_id,
                Reading.timestamp >= date_from,
                Reading.timestamp <= date_to,
            )
            .order_by(Reading.timestamp.asc())
            .all()
        )

    def get_latest_by_sensor(self, sensor_id: UUID) -> Reading | None:
        """Return the single most recent reading for a sensor.

        Args:
            sensor_id: The sensor's primary key.

        Returns:
            The latest :class:`Reading`, or ``None`` if none exist.
        """
        return (
            self.db.query(Reading)
            .filter(Reading.sensor_id == sensor_id)
            .order_by(Reading.timestamp.desc())
            .first()
        )

    def get_latest_by_sensors(self, sensor_ids: list[UUID]) -> dict[UUID, Reading]:
        """Return the latest reading for each of the given sensors.

        Uses a single query with a window function to avoid N+1
        round-trips.

        Args:
            sensor_ids: List of sensor primary keys.

        Returns:
            A mapping of sensor_id → latest :class:`Reading`.
            Sensors with no readings are omitted.
        """
        if not sensor_ids:
            return {}

        from sqlalchemy import func as sa_func
        from sqlalchemy.orm import aliased

        # Subquery: rank readings per sensor by timestamp descending
        ranked = (
            self.db.query(
                Reading,
                sa_func.row_number()
                .over(
                    partition_by=Reading.sensor_id,
                    order_by=Reading.timestamp.desc(),
                )
                .label("rn"),
            )
            .filter(Reading.sensor_id.in_(sensor_ids))
            .subquery()
        )

        aliased_reading = aliased(Reading, ranked)
        results = (
            self.db.query(aliased_reading)
            .filter(ranked.c.rn == 1)
            .all()
        )

        return {r.sensor_id: r for r in results}

    def bulk_insert(self, readings: list[dict]) -> int:
        """Insert multiple readings in a single flush.

        Args:
            readings: A list of column-name → value mappings.  Each
                dict must include at least ``sensor_id``, ``value``,
                and ``tenant_id``.

        Returns:
            The number of readings inserted.
        """
        instances = [Reading(**data) for data in readings]
        self.db.add_all(instances)
        self.db.flush()
        return len(instances)

    def get_aggregated(
        self,
        sensor_id: UUID,
        date_from: datetime,
        date_to: datetime,
    ) -> dict:
        """Compute min/max/avg/count aggregations for a sensor's readings.

        Args:
            sensor_id: The sensor's primary key.
            date_from: Inclusive start of the range (UTC).
            date_to: Inclusive end of the range (UTC).

        Returns:
            A dict with keys ``min``, ``max``, ``avg``, and ``count``.
            Values are ``None`` when no readings exist in the range.
        """
        row = (
            self.db.query(
                sa_func.min(Reading.value).label("min"),
                sa_func.max(Reading.value).label("max"),
                sa_func.avg(Reading.value).label("avg"),
                sa_func.count(Reading.id).label("count"),
            )
            .filter(
                Reading.sensor_id == sensor_id,
                Reading.timestamp >= date_from,
                Reading.timestamp <= date_to,
            )
            .one()
        )
        return {
            "min": float(row.min) if row.min is not None else None,
            "max": float(row.max) if row.max is not None else None,
            "avg": round(float(row.avg), 2) if row.avg is not None else None,
            "count": row.count,
        }
