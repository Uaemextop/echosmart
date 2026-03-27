"""Sincronización con el backend cloud."""

import logging

logger = logging.getLogger(__name__)


class CloudSync:
    """Sincronización batch de lecturas con reintentos exponenciales."""

    def __init__(self, api_url: str, api_key: str, sync_interval: int = 300):
        self.api_url = api_url
        self.api_key = api_key
        self.sync_interval = sync_interval
        self.pending_readings = []
        logger.info(f"CloudSync inicializado — URL: {api_url}, Intervalo: {sync_interval}s")

    def queue_reading(self, reading: dict):
        """Agregar lectura a la cola de sincronización."""
        self.pending_readings.append(reading)

    def sync(self):
        """Enviar lecturas pendientes al backend."""
        if not self.pending_readings:
            return

        # TODO: Implementar envío batch con reintentos
        logger.info(f"Sincronizando {len(self.pending_readings)} lecturas...")
        self.pending_readings.clear()
