"""Domain entities — Pure dataclasses with no external dependencies."""

from .sensor_reading import SensorReading
from .alert import Alert, AlertSeverity
from .gateway_config import GatewayConfig

__all__ = ["SensorReading", "Alert", "AlertSeverity", "GatewayConfig"]
