"""Configuración del gateway EchoSmart."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class GatewayConfig:
    """Configuración cargada desde variables de entorno."""

    gateway_id: str = os.getenv("GATEWAY_ID", "gw-001")
    gateway_name: str = os.getenv("GATEWAY_NAME", "Invernadero Principal")
    cloud_api_url: str = os.getenv("CLOUD_API_URL", "http://localhost:8000")
    cloud_api_key: str = os.getenv("CLOUD_API_KEY", "")
    mqtt_broker: str = os.getenv("MQTT_BROKER", "localhost")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    polling_interval: int = int(os.getenv("POLLING_INTERVAL", "60"))
    sync_interval: int = int(os.getenv("SYNC_INTERVAL", "300"))
    simulation_mode: bool = os.getenv("SIMULATION_MODE", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


config = GatewayConfig()
