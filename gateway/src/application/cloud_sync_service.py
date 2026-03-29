"""Caso de uso: Sincronización con backend cloud."""
import logging
from typing import List

from ..domain.entities.sensor import SensorReading

logger = logging.getLogger(__name__)


class CloudSyncService:
    """Gestiona la cola de lecturas y delega el envío al adaptador HTTP."""

    def __init__(self, http_adapter, sync_interval: int = 300) -> None:
        self._http = http_adapter
        self.sync_interval = sync_interval
        self._queue: List[SensorReading] = []
        logger.info("CloudSyncService inicializado con intervalo=%ds", sync_interval)

    def enqueue(self, reading: SensorReading) -> None:
        """Agregar lectura a la cola de sincronización."""
        self._queue.append(reading)

    def flush(self) -> int:
        """Enviar lecturas pendientes al backend. Retorna número enviadas."""
        if not self._queue:
            return 0
        batch = list(self._queue)
        try:
            sent = self._http.send_batch(batch)
            self._queue.clear()
            logger.info("Sincronizadas %d lecturas al backend", sent)
            return sent
        except Exception as exc:
            logger.error("Error al sincronizar %d lecturas: %s", len(batch), exc)
            raise

    @property
    def pending_count(self) -> int:
        """Número de lecturas pendientes de sincronización."""
        return len(self._queue)
