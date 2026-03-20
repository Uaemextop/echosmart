"""Hardware Abstraction Layer (HAL) para Raspberry Pi."""

import logging

logger = logging.getLogger(__name__)


class HAL:
    """Capa de abstracción de hardware para GPIO, I2C, 1-Wire y UART."""

    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode
        if simulation_mode:
            logger.info("HAL inicializado en modo simulación.")
        else:
            logger.info("HAL inicializado con hardware real.")
            # TODO: Inicializar GPIO, I2C, 1-Wire, UART

    def read_gpio(self, pin: int):
        """Leer valor de un pin GPIO."""
        # TODO: Implementar lectura GPIO
        pass

    def read_i2c(self, address: int, register: int, length: int = 1):
        """Leer datos del bus I2C."""
        # TODO: Implementar lectura I2C
        pass

    def read_1wire(self, device_id: str):
        """Leer datos del bus 1-Wire."""
        # TODO: Implementar lectura 1-Wire
        pass

    def read_uart(self, port: str, baudrate: int = 9600):
        """Leer datos del puerto UART."""
        # TODO: Implementar lectura UART
        pass
