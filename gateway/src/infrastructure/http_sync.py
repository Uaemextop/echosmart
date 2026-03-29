"""Adaptador HTTP para sincronización con backend cloud."""
import logging
from typing import List

from ..domain.entities.sensor import SensorReading

logger = logging.getLogger(__name__)


class HTTPSyncAdapter:
    """Envía lecturas al backend mediante HTTP con reintentos exponenciales."""

    MAX_RETRIES = 3

    def __init__(self, api_url: str, api_key: str) -> None:
        self.api_url = api_url
        self.api_key = api_key

    def send_batch(self, readings: List[SensorReading]) -> int:
        """Enviar un lote de lecturas. Retorna número enviadas."""
        # TODO: implementar con requests + backoff exponencial
        logger.info("Enviando lote de %d lecturas a %s", len(readings), self.api_url)
        return len(readings)
