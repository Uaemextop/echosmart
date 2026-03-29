"""Message publisher interface — Contract for MQTT or similar brokers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class IMessagePublisher(ABC):
    """Abstract publisher for broadcasting sensor data to a message broker."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the message broker."""

    @abstractmethod
    def disconnect(self) -> None:
        """Cleanly disconnect from the message broker."""

    @abstractmethod
    def publish(self, topic: str, payload: dict) -> bool:
        """Publish a JSON payload to the given topic. Return True on success."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Return True if currently connected to the broker."""
