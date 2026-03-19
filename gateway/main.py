"""EchoSmart Gateway — Orquestador principal."""

import logging
import sys

from src.config import config

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("echosmart-gateway")


def main():
    """Punto de entrada del gateway."""
    logger.info("Iniciando EchoSmart Gateway v1.0.0")
    logger.info(f"Gateway ID: {config.gateway_id}")
    logger.info(f"Modo simulación: {config.simulation_mode}")

    # TODO: Inicializar SensorManager, AlertEngine, CloudSync, MQTT
    logger.info("Gateway iniciado correctamente.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Gateway detenido por el usuario.")
        sys.exit(0)
