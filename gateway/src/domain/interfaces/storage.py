"""Storage repository interface — Contract for reading persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.entities.alert import Alert


class IStorageRepository(ABC):
    """Abstract repository for persisting sensor readings and alerts.

    Implementations may use SQLite (gateway), PostgreSQL (backend), etc.
    """

    @abstractmethod
    def save_reading(self, reading: SensorReading) -> None:
        """Persist a single sensor reading."""

    @abstractmethod
    def save_alert(self, alert: Alert) -> None:
        """Persist a single alert."""

    @abstractmethod
    def get_readings(
        self,
        sensor_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[SensorReading]:
        """Retrieve readings, optionally filtered by sensor and time window."""

    @abstractmethod
    def get_unsynced_readings(self, limit: int = 100) -> list[dict]:
        """Return readings that have not yet been synced to the cloud."""

    @abstractmethod
    def mark_readings_synced(self, reading_ids: list[int]) -> None:
        """Mark the given reading IDs as successfully synced."""

    @abstractmethod
    def get_unsynced_alerts(self, limit: int = 50) -> list[dict]:
        """Return alerts that have not yet been synced to the cloud."""

    @abstractmethod
    def mark_alerts_synced(self, alert_ids: list[str]) -> None:
        """Mark the given alert IDs as successfully synced."""

    @abstractmethod
    def get_stats(self) -> dict:
        """Return storage statistics (counts, disk usage, pending sync)."""

    @abstractmethod
    def apply_retention(self, max_age_days: int = 7) -> int:
        """Delete readings older than *max_age_days*. Return count deleted."""

    @abstractmethod
    def close(self) -> None:
        """Release underlying database resources."""
