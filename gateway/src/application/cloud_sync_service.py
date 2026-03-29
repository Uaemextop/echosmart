"""Cloud sync service — Application-layer orchestration for data synchronization.

Coordinates between the storage repository and the sync client to
batch-send unsynced readings and alerts.
"""

from __future__ import annotations

import logging

from gateway.src.domain.constants import DEFAULT_SYNC_BATCH_SIZE
from gateway.src.domain.interfaces.storage import IStorageRepository
from gateway.src.domain.interfaces.sync_client import ISyncClient

logger = logging.getLogger(__name__)


class CloudSyncService:
    """Periodically syncs unsynced readings and alerts to the cloud backend.

    Args:
        storage: Local storage repository.
        sync_client: HTTP client for cloud communication.
        batch_size: Maximum number of records per sync batch.
    """

    def __init__(
        self,
        storage: IStorageRepository,
        sync_client: ISyncClient,
        batch_size: int = DEFAULT_SYNC_BATCH_SIZE,
    ) -> None:
        self._storage = storage
        self._client = sync_client
        self._batch_size = batch_size

    def sync(self) -> dict:
        """Execute one sync cycle. Return counts of synced records."""
        readings_synced = self._sync_readings()
        alerts_synced = self._sync_alerts()
        return {
            "readings_synced": readings_synced,
            "alerts_synced": alerts_synced,
        }

    def _sync_readings(self) -> int:
        unsynced = self._storage.get_unsynced_readings(limit=self._batch_size)
        if not unsynced:
            return 0
        synced_ids = self._client.sync_readings(unsynced)
        if synced_ids:
            self._storage.mark_readings_synced(synced_ids)
        return len(synced_ids)

    def _sync_alerts(self) -> int:
        unsynced = self._storage.get_unsynced_alerts(limit=self._batch_size)
        if not unsynced:
            return 0
        synced_ids = self._client.sync_alerts(unsynced)
        if synced_ids:
            self._storage.mark_alerts_synced(synced_ids)
        return len(synced_ids)
