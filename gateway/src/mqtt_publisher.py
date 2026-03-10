import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """Publishes sensor data and alerts over MQTT."""

    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        gateway_id: str = "gw-001",
    ):
        self.broker = broker
        self.port = port
        self.gateway_id = gateway_id
        self.client = None
        self.connected = False

    def connect(self) -> bool:
        try:
            import paho.mqtt.client as mqtt

            self.client = mqtt.Client(client_id=f"echosmart-{self.gateway_id}")
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            self.connected = True
            return True
        except Exception as e:
            logger.warning("MQTT connection failed: %s", e)
            self.connected = False
            return False

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        self.connected = False

    def publish_reading(self, sensor_id: str, reading: dict) -> bool:
        topic = f"echosmart/{self.gateway_id}/sensors/{sensor_id}/data"
        return self._publish(topic, reading)

    def publish_alert(self, alert: dict) -> bool:
        alert_id = alert.get("rule_id", "unknown")
        topic = f"echosmart/{self.gateway_id}/alerts/{alert_id}"
        return self._publish(topic, alert)

    def publish_status(self, status: dict) -> bool:
        topic = f"echosmart/{self.gateway_id}/system/status"
        return self._publish(topic, status)

    def _publish(self, topic: str, payload: dict) -> bool:
        if not self.client:
            logger.warning("MQTT client not initialised — skipping publish to %s", topic)
            return False
        try:
            result = self.client.publish(topic, json.dumps(payload), qos=1)
            return result.rc == 0
        except Exception as e:
            logger.error("MQTT publish error on %s: %s", topic, e)
            return False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("MQTT connected to %s:%d", self.broker, self.port)
        else:
            logger.error("MQTT connection refused (rc=%d)", rc)

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning("MQTT disconnected (rc=%d)", rc)
