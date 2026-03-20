"""Publicador MQTT local."""

import logging

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """Publica lecturas de sensores en el broker MQTT local."""

    def __init__(self, broker: str = "localhost", port: int = 1883):
        self.broker = broker
        self.port = port
        self.client = None
        logger.info(f"MQTTPublisher inicializado — Broker: {broker}:{port}")

    def connect(self):
        """Conectar al broker MQTT."""
        # TODO: Implementar conexión con paho-mqtt
        pass

    def publish(self, topic: str, payload: dict):
        """Publicar un mensaje en un topic."""
        # TODO: Implementar publicación
        logger.debug(f"Publicando en {topic}: {payload}")

    def disconnect(self):
        """Desconectar del broker MQTT."""
        # TODO: Implementar desconexión
        pass
