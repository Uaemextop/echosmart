import json
import logging
import threading
from typing import Optional

import paho.mqtt.client as mqtt

from config import settings

logger = logging.getLogger(__name__)


class MQTTHandler:
    def __init__(self) -> None:
        self._client: Optional[mqtt.Client] = None
        self._connected = False

    def connect(self) -> None:
        self._client = mqtt.Client(client_id=f"gateway-{settings.gateway_id}")
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        self._client.connect(
            settings.mqtt_broker_host,
            settings.mqtt_broker_port,
            keepalive=60,
        )
        thread = threading.Thread(target=self._client.loop_forever, daemon=True)
        thread.start()

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc: int) -> None:
        if rc == 0:
            self._connected = True
            logger.info("MQTT connected to %s:%s", settings.mqtt_broker_host, settings.mqtt_broker_port)
            client.subscribe("/sensors/+/config")
            logger.info("Subscribed to /sensors/+/config")
        else:
            logger.error("MQTT connection failed with code %d", rc)

    def _on_disconnect(self, client: mqtt.Client, userdata, rc: int) -> None:
        self._connected = False
        logger.warning("MQTT disconnected (rc=%d)", rc)

    def _on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage) -> None:
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            logger.info("Config update on %s: %s", message.topic, payload)
        except json.JSONDecodeError:
            logger.warning("Non-JSON message on %s", message.topic)

    def publish_sensor_data(self, uuid: str, data_dict: dict) -> None:
        if not self._connected or self._client is None:
            logger.warning("MQTT not connected; cannot publish data for %s", uuid)
            return
        topic = f"/sensors/{uuid}/data"
        self._client.publish(topic, json.dumps(data_dict), qos=1)
        logger.debug("Published to %s", topic)

    def create_topics(self, uuid: str) -> None:
        if not self._connected or self._client is None:
            logger.warning("MQTT not connected; cannot create topics for %s", uuid)
            return
        for suffix in ("data", "config"):
            topic = f"/sensors/{uuid}/{suffix}"
            self._client.publish(topic, b"", retain=True)
            logger.debug("Created retained topic %s", topic)

    def subscribe_to_sensor(self, uuid: str) -> None:
        if not self._connected or self._client is None:
            logger.warning("MQTT not connected; cannot subscribe for %s", uuid)
            return
        topic = f"/sensors/{uuid}/config"
        self._client.subscribe(topic)
        logger.debug("Subscribed to %s", topic)

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.disconnect()
            self._connected = False
