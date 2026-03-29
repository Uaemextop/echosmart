"""Cloud sync client interface — Contract for backend synchronization."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ISyncClient(ABC):
    """Abstract client for synchronizing data with the cloud backend."""

    @abstractmethod
    def sync_readings(self, readings: list[dict]) -> list[int]:
        """Send a batch of readings. Return IDs that were synced successfully."""

    @abstractmethod
    def sync_alerts(self, alerts: list[dict]) -> list[str]:
        """Send a batch of alerts. Return IDs that were synced successfully."""

    @abstractmethod
    def register_gateway(self, info: dict) -> bool:
        """Register or update this gateway with the cloud. Return True on success."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the cloud backend is reachable."""
