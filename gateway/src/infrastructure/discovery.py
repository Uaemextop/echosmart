"""Auto-descubrimiento de sensores vía SSDP."""
import logging

logger = logging.getLogger(__name__)


class SensorDiscovery:
    """Descubre automáticamente sensores conectados al gateway."""

    def __init__(self):
        logger.info("SensorDiscovery inicializado.")

    def scan(self) -> list:
        """Escanear sensores conectados."""
        # TODO: Implementar escaneo de buses I2C, 1-Wire, GPIO, UART
        discovered = []
        logger.info(f"Descubiertos {len(discovered)} sensores.")
        return discovered
