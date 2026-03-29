"""Sensor service — business logic and use cases.

``SensorService`` orchestrates every sensor-related operation:

- Sensor CRUD (create, read, update, delete).
- Reading retrieval and bulk ingestion.
- Dashboard aggregation for tenant-level overviews.

**Transaction policy:** The service owns ``commit`` / ``rollback``
because write operations may span multiple aggregates (e.g. ingestion
inserts readings *and* updates sensor timestamps).
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.reading import Reading
from src.models.sensor import Sensor
from src.sensors.repository import ReadingRepository, SensorRepository
from src.shared.exceptions import NotFoundError, ValidationError


class SensorService:
    """High-level sensor use-case orchestrator.

    Args:
        db: An active SQLAlchemy session — the service manages
            ``commit`` and ``rollback`` internally.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._sensors = SensorRepository(db)
        self._readings = ReadingRepository(db)

    # ------------------------------------------------------------------
    # Sensor CRUD
    # ------------------------------------------------------------------

    def create_sensor(self, tenant_id: UUID, data: dict) -> Sensor:
        """Create a new sensor for a tenant.

        The ``tenant_id`` is injected by the router from the
        authenticated user's claims — it is *not* accepted from the
        request body.

        Args:
            tenant_id: Owning tenant's primary key.
            data: Validated sensor attributes (from ``SensorCreate``).

        Returns:
            The newly persisted :class:`Sensor`.

        Raises:
            ValidationError: If ``min_value`` exceeds ``max_value``.
        """
        min_val = data.get("min_value")
        max_val = data.get("max_value")
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ValidationError(
                "min_value must be less than or equal to max_value",
                field="min_value",
            )

        data["tenant_id"] = tenant_id
        sensor = self._sensors.create(data)
        self.db.commit()
        self.db.refresh(sensor)
        return sensor

    def get_sensor(self, sensor_id: UUID) -> Sensor:
        """Retrieve a single sensor by ID.

        Args:
            sensor_id: The sensor's primary key.

        Returns:
            The :class:`Sensor` instance.

        Raises:
            NotFoundError: If no sensor matches the given ID.
        """
        return self._sensors.get_by_id_or_raise(sensor_id)

    def update_sensor(self, sensor_id: UUID, data: dict) -> Sensor:
        """Update an existing sensor.

        Only the keys present in *data* are modified.

        Args:
            sensor_id: The sensor's primary key.
            data: Partial update attributes (from ``SensorUpdate``).

        Returns:
            The updated :class:`Sensor`.

        Raises:
            NotFoundError: If the sensor does not exist.
            ValidationError: If ``min_value`` exceeds ``max_value``
                after applying the update.
        """
        sensor = self._sensors.get_by_id_or_raise(sensor_id)

        # Validate min/max with merged values
        new_min = data.get("min_value", sensor.min_value)
        new_max = data.get("max_value", sensor.max_value)
        if new_min is not None and new_max is not None and new_min > new_max:
            raise ValidationError(
                "min_value must be less than or equal to max_value",
                field="min_value",
            )

        updated = self._sensors.update(sensor_id, data)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def delete_sensor(self, sensor_id: UUID) -> bool:
        """Delete a sensor by ID.

        Args:
            sensor_id: The sensor's primary key.

        Returns:
            ``True`` if the sensor was deleted.

        Raises:
            NotFoundError: If the sensor does not exist.
        """
        self._sensors.get_by_id_or_raise(sensor_id)
        result = self._sensors.delete(sensor_id)
        self.db.commit()
        return result

    def list_sensors(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Sensor]:
        """List sensors for a tenant with pagination.

        Args:
            tenant_id: The tenant's primary key.
            skip: Number of records to skip (offset).
            limit: Maximum records to return.

        Returns:
            A list of :class:`Sensor` instances.
        """
        return self._sensors.get_all(
            skip=skip,
            limit=limit,
            filters={"tenant_id": tenant_id},
        )

    # ------------------------------------------------------------------
    # Readings
    # ------------------------------------------------------------------

    def get_readings(self, sensor_id: UUID, limit: int = 100) -> list[Reading]:
        """Return the most recent readings for a sensor.

        Verifies the sensor exists before querying readings.

        Args:
            sensor_id: The sensor's primary key.
            limit: Maximum number of readings to return.

        Returns:
            A list of :class:`Reading` instances (newest first).

        Raises:
            NotFoundError: If the sensor does not exist.
        """
        self._sensors.get_by_id_or_raise(sensor_id)
        return self._readings.get_by_sensor(sensor_id, limit=limit)

    def get_latest_reading(self, sensor_id: UUID) -> Reading | None:
        """Return the single most recent reading for a sensor.

        Args:
            sensor_id: The sensor's primary key.

        Returns:
            The latest :class:`Reading`, or ``None``.

        Raises:
            NotFoundError: If the sensor does not exist.
        """
        self._sensors.get_by_id_or_raise(sensor_id)
        return self._readings.get_latest_by_sensor(sensor_id)

    def ingest_readings(self, tenant_id: UUID, readings: list[dict]) -> int:
        """Bulk-ingest readings and update sensor timestamps.

        Each reading must include ``sensor_id`` and ``value``.  An
        optional ``timestamp`` defaults to the current UTC time.

        Args:
            tenant_id: The tenant performing the ingestion.
            readings: A list of reading dicts.

        Returns:
            The number of readings successfully inserted.

        Raises:
            ValidationError: If the readings list is empty.
        """
        if not readings:
            raise ValidationError("At least one reading is required")

        now = datetime.now(timezone.utc)
        prepared: list[dict] = []

        for entry in readings:
            prepared.append({
                "sensor_id": entry["sensor_id"],
                "tenant_id": tenant_id,
                "value": entry["value"],
                "timestamp": entry.get("timestamp") or now,
            })

        count = self._readings.bulk_insert(prepared)

        # Bulk-update last_reading_at for all affected sensors in one query
        sensor_ids = {entry["sensor_id"] for entry in prepared}
        self._sensors.bulk_update_last_reading(sensor_ids, now)

        self.db.commit()
        return count

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_dashboard_data(self, tenant_id: UUID) -> dict:
        """Build a dashboard summary for a tenant.

        Returns:
            A dict containing:

            - ``total_sensors`` — count of all sensors.
            - ``online_sensors`` — count of online sensors.
            - ``latest_readings`` — mapping of sensor ID to its most
              recent reading (``value``, ``unit``, ``timestamp``).
        """
        all_sensors = self._sensors.get_by_tenant(tenant_id)
        online_sensors = [s for s in all_sensors if s.is_online]

        # Fetch latest reading per sensor in a single query
        sensor_ids = [s.id for s in all_sensors]
        latest_map = self._readings.get_latest_by_sensors(sensor_ids)

        latest_readings: dict[str, dict] = {}
        for sensor in all_sensors:
            reading = latest_map.get(sensor.id)
            if reading is not None:
                latest_readings[str(sensor.id)] = {
                    "value": reading.value,
                    "unit": sensor.unit,
                    "timestamp": reading.timestamp.isoformat(),
                }

        return {
            "total_sensors": len(all_sensors),
            "online_sensors": len(online_sensors),
            "latest_readings": latest_readings,
        }
