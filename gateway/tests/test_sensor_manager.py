"""Tests del SensorManager."""

from gateway.src.sensor_manager import SensorManager
from gateway.src.hal import HAL


def test_sensor_manager_init():
    """Verificar inicialización del SensorManager."""
    hal = HAL(simulation_mode=True)
    manager = SensorManager(hal, polling_interval=60)
    assert manager.polling_interval == 60
    assert len(manager.sensors) == 0
