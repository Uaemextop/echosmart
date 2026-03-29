"""Sensor management feature module.

Handles the full lifecycle of IoT sensors and their readings:

- CRUD operations on :class:`~src.models.sensor.Sensor` entities.
- Ingestion and retrieval of :class:`~src.models.reading.Reading` data.
- Dashboard aggregations for tenant-level overviews.

Public surface re-exported for convenience::

    from src.sensors import SensorService, SensorRepository, ReadingRepository
    from src.sensors.router import router as sensors_router
"""

from src.sensors.repository import ReadingRepository, SensorRepository
from src.sensors.service import SensorService

__all__ = [
    "SensorRepository",
    "ReadingRepository",
    "SensorService",
]
