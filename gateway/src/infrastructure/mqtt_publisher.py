"""MQTT publisher — Concrete implementation of IMessagePublisher.

Publishes sensor data to a Mosquitto broker with structured topics.
"""

from __future__ import annotations

import json
import logging
import time

from gateway.src.domain.interfaces.publisher import IMessagePublisher

logger = logging.getLogger(__name__)

_RECONNECT_DELAY_BASE_S = 1
_RECONNECT_DELAY_MAX_S = 60


class MqttMessagePublisher(IMessagePublisher):
    """MQTT publisher with auto-reconnection and LWT support.

    Args:
        broker: MQTT broker hostname.
        port: MQTT broker port.
        gateway_id: Gateway identifier for topic namespacing.
        qos: Quality of Service level (0, 1, or 2).
    """

    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        gateway_id: str = "gw-001",
        qos: int = 1,
    ) -> None:
        self._broker = broker
        self._port = port
        self._gateway_id = gateway_id
        self._qos = qos
        self._client = None
        self._connected = False

    def connect(self) -> None:
        try:
            import paho.mqtt.client as mqtt

            self._client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"echosmart-{self._gateway_id}",
            )
            # Last Will and Testament — broker publishes if we disconnect unexpectedly
            lwt_topic = f"echosmart/{self._gateway_id}/status"
            self._client.will_set(lwt_topic, payload="offline", qos=1, retain=True)
            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            self._client.connect(self._broker, self._port, keepalive=60)
            self._client.loop_start()
            logger.info("MQTT connecting to %s:%d …", self._broker, self._port)
        except Exception as exc:
            logger.error("MQTT connection failed: %s", exc)

    def disconnect(self) -> None:
        if self._client:
            status_topic = f"echosmart/{self._gateway_id}/status"
            self._client.publish(status_topic, payload="offline", qos=1, retain=True)
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False
            logger.info("MQTT disconnected.")

    def publish(self, topic: str, payload: dict) -> bool:
        if not self._connected or self._client is None:
            logger.warning("MQTT not connected — message dropped for topic %s.", topic)
            return False
        full_topic = f"echosmart/{self._gateway_id}/{topic}"
        try:
            info = self._client.publish(
                full_topic,
                json.dumps(payload),
                qos=self._qos,
            )
            return info.rc == 0
        except Exception as exc:
            logger.error("MQTT publish error: %s", exc)
            return False

    def is_connected(self) -> bool:
        return self._connected

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_connect(self, client, userdata, flags, reason_code, properties=None) -> None:
        self._connected = True
        status_topic = f"echosmart/{self._gateway_id}/status"
        client.publish(status_topic, payload="online", qos=1, retain=True)
        logger.info("MQTT connected to %s:%d.", self._broker, self._port)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None) -> None:
        self._connected = False
        logger.warning("MQTT disconnected (rc=%s). Will auto-reconnect.", reason_code)
