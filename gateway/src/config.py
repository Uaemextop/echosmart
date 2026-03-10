import os


class Config:
    def __init__(self):
        self.gateway_id = os.environ.get("GATEWAY_ID", "gw-dev-01")
        self.gateway_name = os.environ.get("GATEWAY_NAME", "Development Gateway")
        self.cloud_api_url = os.environ.get("CLOUD_API_URL", "http://localhost:8000")
        self.cloud_api_key = os.environ.get("CLOUD_API_KEY", "dev-api-key")
        self.mqtt_broker = os.environ.get("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.environ.get("MQTT_PORT", "1883"))
        self.sensor_polling_interval = int(
            os.environ.get("SENSOR_POLLING_INTERVAL", "60")
        )
        self.cloud_sync_interval = int(os.environ.get("CLOUD_SYNC_INTERVAL", "300"))
        self.sqlite_path = os.environ.get("SQLITE_PATH", ":memory:")
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
