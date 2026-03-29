"""Gateway configuration — Loads from environment and sensors.json.

Centralizes all configuration in a single module so that the rest of the
codebase never accesses ``os.getenv`` directly.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from gateway.src.domain.entities.gateway_config import GatewayConfig, SensorConfig

load_dotenv()

logger = logging.getLogger(__name__)

_SENSORS_JSON_PATH = Path(__file__).resolve().parent.parent / "sensors.json"


def load_config(sensors_path: str | Path | None = None) -> GatewayConfig:
    """Build a ``GatewayConfig`` from env vars and an optional sensors.json.

    Args:
        sensors_path: Path to the sensors configuration file.
                      Defaults to ``gateway/sensors.json``.

    Returns:
        A fully-populated ``GatewayConfig`` instance.
    """
    sensors_path = Path(sensors_path) if sensors_path else _SENSORS_JSON_PATH
    sensors: list[SensorConfig] = []

    if sensors_path.exists():
        try:
            data = json.loads(sensors_path.read_text(encoding="utf-8"))
            for idx, s in enumerate(data.get("sensors", [])):
                sensors.append(
                    SensorConfig(
                        sensor_type=s["type"],
                        name=s.get("name", f"sensor-{idx}"),
                        sensor_id=s.get("sensor_id", f"{s['type']}-{idx:02d}"),
                        params={
                            k: v
                            for k, v in s.items()
                            if k not in ("type", "name", "sensor_id")
                        },
                    )
                )
            logger.info("Loaded %d sensor(s) from %s.", len(sensors), sensors_path)
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Failed to parse %s: %s", sensors_path, exc)

    return GatewayConfig(
        gateway_id=os.getenv("GATEWAY_ID", "gw-001"),
        gateway_name=os.getenv("GATEWAY_NAME", "Invernadero Principal"),
        cloud_api_url=os.getenv("CLOUD_API_URL", "http://localhost:8000"),
        cloud_api_key=os.getenv("CLOUD_API_KEY", ""),
        mqtt_broker=os.getenv("MQTT_BROKER", "localhost"),
        mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
        polling_interval=int(os.getenv("POLLING_INTERVAL", "60")),
        sync_interval=int(os.getenv("SYNC_INTERVAL", "300")),
        simulation_mode=os.getenv("SIMULATION_MODE", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        sensors=sensors,
    )


# Module-level singleton (backwards-compatible with existing imports)
config = load_config()
