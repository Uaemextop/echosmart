from abc import ABC, abstractmethod
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class HardwareInterface(ABC):
    @abstractmethod
    def initialize(self) -> bool:
        ...

    @abstractmethod
    def read(self) -> Optional[float]:
        ...

    @abstractmethod
    def cleanup(self):
        ...


class GPIOManager:
    """GPIO abstraction. Falls back to simulation when RPi.GPIO is unavailable."""

    def __init__(self):
        self._pins = {}
        self._simulation = False
        try:
            import RPi.GPIO as GPIO  # type: ignore

            self._gpio = GPIO
            self._gpio.setmode(GPIO.BCM)
            self._gpio.setwarnings(False)
        except (ImportError, RuntimeError):
            self._gpio = None
            self._simulation = True
            logger.info("GPIO: running in simulation mode")

    def setup_pin(self, pin: int, mode: str) -> None:
        if self._gpio:
            gpio_mode = (
                self._gpio.OUT if mode == "output" else self._gpio.IN
            )
            self._gpio.setup(pin, gpio_mode)
        self._pins[pin] = {"mode": mode, "value": 0}

    def read_pin(self, pin: int) -> int:
        if self._gpio:
            return self._gpio.input(pin)
        return self._pins.get(pin, {}).get("value", 0)

    def write_pin(self, pin: int, value: int) -> None:
        if self._gpio:
            self._gpio.output(pin, value)
        if pin in self._pins:
            self._pins[pin]["value"] = value

    def cleanup(self):
        if self._gpio:
            self._gpio.cleanup()
        self._pins.clear()


class I2CManager:
    """I2C bus abstraction. Falls back to simulation when smbus2 is unavailable."""

    def __init__(self, bus: int = 1):
        self._bus_number = bus
        self._simulation = False
        self._sim_data = {}
        try:
            from smbus2 import SMBus  # type: ignore

            self._bus = SMBus(bus)
        except (ImportError, FileNotFoundError, OSError):
            self._bus = None
            self._simulation = True
            logger.info("I2C: running in simulation mode")

    def write(self, address: int, data: bytes) -> None:
        if self._bus:
            for byte in data:
                self._bus.write_byte(address, byte)
        else:
            self._sim_data[address] = data

    def read(self, address: int, length: int) -> bytes:
        if self._bus:
            return bytes(self._bus.read_i2c_block_data(address, 0, length))
        return bytes(length)

    def close(self):
        if self._bus:
            self._bus.close()


class OnewireManager:
    """1-Wire bus abstraction for temperature sensors."""

    DEVICES_PATH = "/sys/bus/w1/devices/"

    def read_temperature(self, device_id: str) -> float:
        try:
            path = f"{self.DEVICES_PATH}{device_id}/w1_slave"
            with open(path, "r") as f:
                lines = f.readlines()
            if lines[0].strip().endswith("YES"):
                temp_pos = lines[1].find("t=")
                if temp_pos != -1:
                    return int(lines[1][temp_pos + 2 :]) / 1000.0
        except (FileNotFoundError, IndexError, ValueError) as e:
            logger.warning("1-Wire read failed for %s: %s", device_id, e)
        raise IOError(f"Failed to read temperature from {device_id}")

    def list_devices(self) -> List[str]:
        try:
            import os

            entries = os.listdir(self.DEVICES_PATH)
            return [d for d in entries if d.startswith("28-")]
        except FileNotFoundError:
            return []


class UARTManager:
    """UART serial abstraction. Falls back to simulation when serial port unavailable."""

    def __init__(self, port: str = "/dev/serial0", baudrate: int = 9600):
        self._port_name = port
        self._baudrate = baudrate
        self._simulation = False
        try:
            import serial  # type: ignore

            self._serial = serial.Serial(port, baudrate, timeout=1)
        except (ImportError, OSError):
            self._serial = None
            self._simulation = True
            logger.info("UART: running in simulation mode")

    def read(self, bytes_count: int) -> bytes:
        if self._serial:
            return self._serial.read(bytes_count)
        return bytes(bytes_count)

    def write(self, data: bytes) -> None:
        if self._serial:
            self._serial.write(data)

    def close(self):
        if self._serial:
            self._serial.close()
