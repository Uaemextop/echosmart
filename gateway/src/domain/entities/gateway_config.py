"""Gateway configuration entity — Pure domain object."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SensorConfig:
    """Configuration for a single sensor.

    Attributes:
        sensor_type: Driver type key (ds18b20, dht22, bh1750, soil_moisture, mhz19c).
        name: Human-readable name for the sensor.
        sensor_id: Unique identifier (auto-generated if not provided).
        params: Driver-specific parameters (pin, address, channel, etc.).
    """

    sensor_type: str
    name: str
    sensor_id: str = ""
    params: dict = field(default_factory=dict)


@dataclass
class GatewayConfig:
    """Top-level gateway configuration.

    Attributes:
        gateway_id: Unique identifier for this gateway instance.
        gateway_name: Human-readable name.
        cloud_api_url: URL of the backend cloud API.
        cloud_api_key: API key for cloud authentication.
        mqtt_broker: MQTT broker hostname.
        mqtt_port: MQTT broker port.
        polling_interval: Seconds between sensor polling cycles.
        sync_interval: Seconds between cloud sync attempts.
        simulation_mode: If True, drivers generate simulated data.
        log_level: Python logging level name.
        sensors: List of sensor configurations.
    """

    gateway_id: str = "gw-001"
    gateway_name: str = "Invernadero Principal"
    cloud_api_url: str = "http://localhost:8000"
    cloud_api_key: str = ""
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    polling_interval: int = 60
    sync_interval: int = 300
    simulation_mode: bool = True
    log_level: str = "INFO"
    sensors: list[SensorConfig] = field(default_factory=list)
