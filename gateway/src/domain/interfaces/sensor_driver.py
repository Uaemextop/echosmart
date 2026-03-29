"""Interfaz abstracta para drivers de sensores."""
from abc import ABC, abstractmethod
from ..entities.sensor import SensorReading


class BaseSensorDriver(ABC):
    """Contrato que todo driver de sensor debe implementar."""

    @property
    @abstractmethod
    def sensor_id(self) -> str:
        """Identificador único del sensor."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre descriptivo del sensor."""

    @property
    @abstractmethod
    def sensor_type(self) -> str:
        """Tipo: temperature, humidity, co2, light, soil_moisture."""

    @property
    @abstractmethod
    def unit(self) -> str:
        """Unidad de medida: °C, %, ppm, lux."""

    @abstractmethod
    def read(self) -> SensorReading:
        """Leer el sensor y retornar una SensorReading."""

    @abstractmethod
    def is_available(self) -> bool:
        """Verificar que el sensor está conectado y responde."""
