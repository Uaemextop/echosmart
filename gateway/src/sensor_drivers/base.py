from abc import ABC, abstractmethod
from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)


class SensorDriver(ABC):
    """Abstract base class for all sensor drivers."""

    def __init__(self, sensor_id: str, config: dict = None):
        self.sensor_id = sensor_id
        self.config = config or {}
        self.last_value = None
        self.last_read_time = None

    @abstractmethod
    def initialize(self) -> bool:
        ...

    @abstractmethod
    def read(self) -> Optional[dict]:
        """Read sensor data.

        Returns dict with keys: value, unit, quality
        """
        ...

    @abstractmethod
    def validate_reading(self, value: float) -> bool:
        ...

    def cleanup(self):
        logger.debug("Cleanup for sensor %s", self.sensor_id)

    def _update_state(self, value: float):
        self.last_value = value
        self.last_read_time = time.time()
