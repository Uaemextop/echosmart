import json
import pytest
from unittest.mock import patch, MagicMock

from src.mqtt_publisher import MQTTPublisher


@pytest.fixture
def publisher():
    return MQTTPublisher(broker="localhost", port=1883, gateway_id="gw-test")


class TestMQTTPublisher:
    @patch("paho.mqtt.client.Client")
    def test_connect_success(self, MockClient):
        """Test connection with a mocked paho client."""
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance

        pub = MQTTPublisher(gateway_id="gw-test")
        result = pub.connect()
        assert result is True
        assert pub.connected is True
        mock_instance.connect.assert_called_once()

    def test_publish_reading_no_client(self, publisher):
        result = publisher.publish_reading("t1", {"value": 22.5})
        assert result is False

    def test_publish_alert_no_client(self, publisher):
        result = publisher.publish_alert({"rule_id": "r1", "severity": "high"})
        assert result is False

    def test_publish_status_no_client(self, publisher):
        result = publisher.publish_status({"uptime": 100})
        assert result is False

    def test_publish_reading_with_client(self, publisher):
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.rc = 0
        mock_client.publish.return_value = mock_result

        publisher.client = mock_client
        publisher.connected = True

        result = publisher.publish_reading("t1", {"value": 22.5})
        assert result is True
        mock_client.publish.assert_called_once()
        topic = mock_client.publish.call_args[0][0]
        assert topic == "echosmart/gw-test/sensors/t1/data"

    def test_publish_alert_with_client(self, publisher):
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.rc = 0
        mock_client.publish.return_value = mock_result

        publisher.client = mock_client
        publisher.connected = True

        result = publisher.publish_alert({"rule_id": "r1", "severity": "high"})
        assert result is True
        topic = mock_client.publish.call_args[0][0]
        assert topic == "echosmart/gw-test/alerts/r1"

    def test_publish_status_with_client(self, publisher):
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.rc = 0
        mock_client.publish.return_value = mock_result

        publisher.client = mock_client

        result = publisher.publish_status({"uptime": 3600})
        assert result is True
        topic = mock_client.publish.call_args[0][0]
        assert topic == "echosmart/gw-test/system/status"

    def test_disconnect(self, publisher):
        mock_client = MagicMock()
        publisher.client = mock_client
        publisher.connected = True
        publisher.disconnect()
        assert publisher.connected is False
        mock_client.disconnect.assert_called_once()
