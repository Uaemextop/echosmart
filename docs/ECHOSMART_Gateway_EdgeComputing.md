# EchoSmart - Documentación del Gateway (Raspberry Pi)

## 1. Arquitectura del Gateway

### 1.1 Capas de Software

```
┌─────────────────────────────────────────┐
│      Aplicación Principal (main.py)     │ Layer 5: Orchestration
├─────────────────────────────────────────┤
│  • Discovery (SSDP)                     │
│  • Cloud Sync                           │
│  • Alert Engine                         │
├─────────────────────────────────────────┤
│  Sensor Drivers Layer                   │ Layer 4: Drivers
│  • DS18B20 (1-Wire)                     │
│  • DHT22 (GPIO)                         │
│  • BH1750 (I2C)                         │
│  • Soil Moisture (ADC)                  │
├─────────────────────────────────────────┤
│  Hardware Abstraction Layer             │ Layer 3: HAL
│  • GPIO Controller                      │
│  • I2C Bus Manager                      │
│  • 1-Wire Interface                     │
│  • ADC Reader                           │
├─────────────────────────────────────────┤
│  Database & Persistence Layer           │ Layer 2: Persistence
│  • SQLite Cache                         │
│  • MQTT Publisher                       │
├─────────────────────────────────────────┤
│  Operating System (Raspberry Pi OS)     │ Layer 1: OS
│  • Linux kernel                         │
│  • Device drivers                       │
└─────────────────────────────────────────┘
```

---

## 2. Módulos Principales

### 2.1 Hardware Abstraction Layer (HAL)

```python
# gateway/src/hal.py

"""
Hardware Abstraction Layer
Proporciona interfaz unificada para GPIO, I2C, 1-Wire, ADC
"""

from abc import ABC, abstractmethod
from typing import Optional, List

class HardwareInterface(ABC):
    """Base class para todos los interfaces de hardware"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Inicializar interfaz de hardware"""
        pass
    
    @abstractmethod
    def read(self) -> Optional[float]:
        """Leer valor del hardware"""
        pass
    
    @abstractmethod
    def write(self, value: float) -> bool:
        """Escribir valor al hardware"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Limpiar recursos"""
        pass


class GPIOManager:
    """Gestiona pines GPIO para Raspberry Pi"""
    
    def __init__(self):
        self.pins = {}
        self.initialized = False
    
    def setup_pin(self, pin: int, mode: str, initial: int = 0):
        """
        Configurar un pin GPIO
        
        Args:
            pin: Número de pin (BCM)
            mode: 'IN' o 'OUT'
            initial: Valor inicial para salidas
        """
        import RPi.GPIO as GPIO
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        if mode == 'OUT':
            GPIO.setup(pin, GPIO.OUT, initial=initial)
        else:
            GPIO.setup(pin, GPIO.IN)
        
        self.pins[pin] = { 'mode': mode, 'gpio': GPIO }
    
    def read_pin(self, pin: int) -> int:
        """Leer estado de un pin de entrada"""
        import RPi.GPIO as GPIO
        return GPIO.input(pin)
    
    def write_pin(self, pin: int, value: int):
        """Escribir a un pin de salida"""
        import RPi.GPIO as GPIO
        GPIO.output(pin, value)
    
    def cleanup(self):
        """Limpiar todos los pines"""
        import RPi.GPIO as GPIO
        GPIO.cleanup()


class I2CManager:
    """Gestiona comunicación I2C"""
    
    def __init__(self, bus: int = 1):
        try:
            import board
            import busio
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.bus_num = bus
        except:
            self.i2c = None
            self.bus_num = bus
    
    def write(self, address: int, data: bytes):
        """Escribir bytes a dispositivo I2C"""
        if not self.i2c:
            raise RuntimeError("I2C not initialized")
        
        self.i2c.writeto(address, data)
    
    def read(self, address: int, length: int) -> bytes:
        """Leer bytes de dispositivo I2C"""
        if not self.i2c:
            raise RuntimeError("I2C not initialized")
        
        buffer = bytearray(length)
        self.i2c.readfrom_into(address, buffer)
        return bytes(buffer)
    
    def scan(self) -> List[int]:
        """Escanear dispositivos I2C conectados"""
        if not self.i2c:
            return []
        
        addresses = []
        for addr in range(0x03, 0x78):
            try:
                self.i2c.writeto(addr, b'')
                addresses.append(addr)
            except:
                pass
        
        return addresses


class OneWireManager:
    """Gestiona sensores 1-Wire (DS18B20, etc)"""
    
    def __init__(self, base_path: str = '/sys/bus/w1/devices'):
        self.base_path = base_path
        self.devices = {}
    
    def scan_devices(self) -> List[str]:
        """
        Escanear dispositivos 1-Wire conectados
        
        Returns:
            Lista de IDs de dispositivos (ej: ['28-0516a42651ff'])
        """
        import os
        import glob
        
        devices = glob.glob(f'{self.base_path}/*/name')
        device_ids = [
            os.path.basename(os.path.dirname(d))
            for d in devices
        ]
        
        return device_ids
    
    def read_temperature(self, device_id: str) -> Optional[float]:
        """
        Leer temperatura de sensor DS18B20
        
        Args:
            device_id: ID del dispositivo (ej: '28-0516a42651ff')
        
        Returns:
            Temperatura en °C o None si error
        """
        try:
            with open(f'{self.base_path}/{device_id}/w1_slave', 'r') as f:
                lines = f.readlines()
            
            # Primera línea: CRC check (YES/NO)
            if lines[0].strip()[-3:] != 'YES':
                return None
            
            # Segunda línea: temperatuta
            pos = lines[1].find('t=')
            if pos != -1:
                temp_raw = int(lines[1][pos+2:])
                return temp_raw / 1000.0
        
        except Exception as e:
            print(f"Error reading {device_id}: {e}")
            return None
```

### 2.2 Drivers de Sensores

```python
# gateway/src/sensor_drivers/ds18b20.py

"""
Driver para sensor de temperatura DS18B20 (1-Wire)
"""

from gateway.src.hal import HardwareInterface, OneWireManager

class DS18B20(HardwareInterface):
    """Sensor DS18B20 digital de temperatura"""
    
    def __init__(self, device_id: str):
        """
        Args:
            device_id: ID del dispositivo en 1-Wire (ej: '28-0516a42651ff')
        """
        self.device_id = device_id
        self.onewire = OneWireManager()
        self.last_value = None
        self.error_count = 0
        self.MAX_ERRORS = 3
    
    def initialize(self) -> bool:
        """Verificar que el dispositivo existe"""
        devices = self.onewire.scan_devices()
        return self.device_id in devices
    
    def read(self) -> Optional[float]:
        """
        Leer temperatura del sensor
        
        Returns:
            Temperatura en °C
            
        Raises:
            RuntimeError si no se puede leer después de MAX_ERRORS intentos
        """
        try:
            temp = self.onewire.read_temperature(self.device_id)
            
            if temp is None:
                self.error_count += 1
                if self.error_count >= self.MAX_ERRORS:
                    raise RuntimeError(f"DS18B20 read failed {self.MAX_ERRORS} times")
            else:
                self.error_count = 0
                self.last_value = temp
            
            return temp
        
        except Exception as e:
            print(f"DS18B20 error: {e}")
            raise
    
    def write(self, value: float) -> bool:
        """No aplica para sensores de lectura"""
        return False
    
    def cleanup(self):
        """Limpiar recursos"""
        pass


# gateway/src/sensor_drivers/dht22.py

"""
Driver para sensor DHT22 (temperatura + humedad)
"""

import Adafruit_DHT

class DHT22(HardwareInterface):
    """Sensor DHT22 de temperatura y humedad relativa"""
    
    def __init__(self, gpio_pin: int):
        """
        Args:
            gpio_pin: Pin GPIO conectado a DATA del DHT22
        """
        self.gpio_pin = gpio_pin
        self.sensor = Adafruit_DHT.DHT22
        self.last_temp = None
        self.last_humidity = None
    
    def initialize(self) -> bool:
        """Verificar conexión"""
        try:
            humidity, temp = Adafruit_DHT.read_retry(self.sensor, self.gpio_pin)
            return humidity is not None and temp is not None
        except:
            return False
    
    def read(self) -> tuple[float, float]:
        """
        Leer temperatura y humedad
        
        Returns:
            Tupla (temperatura °C, humedad %)
        """
        humidity, temp = Adafruit_DHT.read_retry(
            self.sensor, 
            self.gpio_pin,
            retries=3
        )
        
        if temp is not None:
            self.last_temp = temp
        if humidity is not None:
            self.last_humidity = humidity
        
        return (self.last_temp, self.last_humidity)
    
    def write(self, value: float) -> bool:
        return False
    
    def cleanup(self):
        pass


# gateway/src/sensor_drivers/bh1750.py

"""
Driver para sensor BH1750 (luz/luminosidad)
Sensor I2C de precisión para medir lux
"""

class BH1750(HardwareInterface):
    """Sensor BH1750 de luminosidad (I2C)"""
    
    # Registro commands
    POWER_DOWN = 0x00
    POWER_ON = 0x01
    RESET = 0x07
    
    # Modos de medición
    CONTINUOUS_HIGH_RES_MODE = 0x10
    CONTINUOUS_HIGH_RES_MODE_2 = 0x11
    CONTINUOUS_LOW_RES_MODE = 0x13
    ONE_TIME_HIGH_RES_MODE = 0x20
    ONE_TIME_HIGH_RES_MODE_2 = 0x21
    ONE_TIME_LOW_RES_MODE = 0x23
    
    def __init__(self, i2c_bus, address: int = 0x23):
        """
        Args:
            i2c_bus: Instancia de I2CManager
            address: Dirección I2C del sensor (0x23 por defecto)
        """
        self.i2c = i2c_bus
        self.address = address
        self.mode = self.CONTINUOUS_HIGH_RES_MODE
    
    def initialize(self) -> bool:
        """Inicializar sensor"""
        try:
            self.i2c.write(self.address, bytes([self.POWER_ON]))
            self.i2c.write(self.address, bytes([self.RESET]))
            self.i2c.write(self.address, bytes([self.mode]))
            return True
        except:
            return False
    
    def read(self) -> Optional[float]:
        """
        Leer luminosidad en lux
        
        Returns:
            Luminosidad en lux
        """
        try:
            data = self.i2c.read(self.address, 2)
            lux = ((data[0] << 8) | data[1]) / 1.2
            return lux
        except Exception as e:
            print(f"BH1750 read error: {e}")
            return None
    
    def write(self, value: float) -> bool:
        return False
    
    def cleanup(self):
        try:
            self.i2c.write(self.address, bytes([self.POWER_DOWN]))
        except:
            pass
```

---

## 3. Sistema de Descubrimiento (SSDP)

```python
# gateway/src/discovery.py

"""
Service Discovery Protocol (SSDP)
Permite que clientes descubran el gateway automáticamente en la red local
"""

import socket
import threading
from datetime import datetime

class SSDPServer:
    """Servidor SSDP para anunciar el gateway en la red local"""
    
    # Multicast address y puerto SSDP
    SSDP_MX = 120           # Máximo tiempo de espera
    SSDP_TARGET = ('239.255.255.250', 1900)
    SSDP_ST = 'upnp:rootdevice'
    
    def __init__(self, gateway_id: str, gateway_name: str, local_ip: str):
        """
        Args:
            gateway_id: ID único del gateway
            gateway_name: Nombre amigable del gateway
            local_ip: IP local del Raspberry Pi
        """
        self.gateway_id = gateway_id
        self.gateway_name = gateway_name
        self.local_ip = local_ip
        self.running = False
    
    def get_device_description(self) -> str:
        """Generar descripción UPnP del dispositivo"""
        return f"""<?xml version="1.0"?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
  <specVersion>
    <major>1</major>
    <minor>0</minor>
  </specVersion>
  <device>
    <deviceType>urn:schemas-upnp-org:device:EchoSmartGateway:1</deviceType>
    <friendlyName>{self.gateway_name}</friendlyName>
    <manufacturer>EchoSmart</manufacturer>
    <manufacturerURL>https://echosmart.com</manufacturerURL>
    <modelDescription>IoT Environmental Monitoring Gateway</modelDescription>
    <modelName>EchoSmart-Gateway</modelName>
    <UDN>uuid:{self.gateway_id}</UDN>
    <serviceList>
      <service>
        <serviceType>urn:schemas-upnp-org:service:SensorAccess:1</serviceType>
        <serviceId>urn:schemas-upnp-org:serviceId:SensorAccess1</serviceId>
        <controlURL>/upnp/control/sensoraccess1</controlURL>
        <eventSubURL>/upnp/control/sensoraccess1</eventSubURL>
        <SCPDURL>/schemas/echosmart-sensors.xml</SCPDURL>
      </service>
    </serviceList>
  </device>
</root>"""
    
    def get_ssdp_announcement(self) -> str:
        """Generar notificación SSDP M-SEARCH"""
        return f"""NOTIFY * HTTP/1.1
HOST: 239.255.255.250:1900
CACHE-CONTROL: max-age=3600
LOCATION: http://{self.local_ip}:8080/device.xml
NT: {self.SSDP_ST}
NTS: ssdp:alive
SERVER: Linux/5.10 UPnP/1.0 EchoSmartGateway/1.0
USN: uuid:{self.gateway_id}::upnp:rootdevice

"""
    
    def start(self):
        """Iniciar anuncios SSDP periódicos"""
        self.running = True
        
        def announce():
            while self.running:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    
                    announcement = self.get_ssdp_announcement()
                    sock.sendto(
                        announcement.encode(),
                        self.SSDP_TARGET
                    )
                    
                    sock.close()
                    
                    # Anunciar cada 30 minutos
                    threading.Event().wait(1800)
                
                except Exception as e:
                    print(f"SSDP announcement error: {e}")
        
        thread = threading.Thread(target=announce, daemon=True)
        thread.start()
    
    def stop(self):
        """Detener anuncios SSDP"""
        self.running = False
```

---

## 4. Sistema de Sincronización con Cloud

```python
# gateway/src/cloud_sync.py

"""
Módulo de sincronización bidireccional con backend cloud
Maneja: lecturas de sensores, configuración, actualizaciones
"""

import requests
import json
from datetime import datetime, timedelta
import threading
import time

class CloudSyncManager:
    """Gestor de sincronización con cloud backend"""
    
    def __init__(self, 
                 cloud_api_url: str, 
                 gateway_id: str,
                 api_key: str,
                 sync_interval: int = 300):
        """
        Args:
            cloud_api_url: URL del backend (ej: https://api.echosmart.com)
            gateway_id: ID del gateway
            api_key: Clave API para autenticación
            sync_interval: Intervalo de sincronización en segundos
        """
        self.cloud_api_url = cloud_api_url
        self.gateway_id = gateway_id
        self.api_key = api_key
        self.sync_interval = sync_interval
        self.running = False
        
        # Queue local de lecturas pendientes
        self.pending_readings = []
        self.pending_alerts = []
    
    def get_headers(self) -> dict:
        """Headers HTTP para autenticación"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-Gateway-ID': self.gateway_id
        }
    
    def queue_reading(self, sensor_id: str, reading: dict):
        """Encolar una lectura para sincronizar"""
        self.pending_readings.append({
            'sensor_id': sensor_id,
            'value': reading['value'],
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': reading.get('metadata', {})
        })
    
    def sync_readings(self) -> bool:
        """Sincronizar lecturas pendientes al cloud"""
        if not self.pending_readings:
            return True
        
        try:
            payload = {
                'gateway_id': self.gateway_id,
                'readings': self.pending_readings,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                f'{self.cloud_api_url}/api/v1/gateways/{self.gateway_id}/readings',
                json=payload,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                # Limpiar queue solo si fue exitoso
                self.pending_readings = []
                print(f"[{datetime.now()}] Synced {len(payload['readings'])} readings")
                return True
            else:
                print(f"Sync error: {response.status_code} {response.text}")
                return False
        
        except Exception as e:
            print(f"Cloud sync error: {e}")
            return False
    
    def fetch_gateway_config(self) -> Optional[dict]:
        """Obtener configuración actualizada del gateway desde cloud"""
        try:
            response = requests.get(
                f'{self.cloud_api_url}/api/v1/gateways/{self.gateway_id}/config',
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
        
        except Exception as e:
            print(f"Config fetch error: {e}")
            return None
    
    def start(self):
        """Iniciar sincronización en background"""
        self.running = True
        
        def sync_worker():
            while self.running:
                try:
                    # Sincronizar lecturas
                    self.sync_readings()
                    
                    # Cada 1 hora: obtener config actualizada
                    if int(time.time()) % 3600 == 0:
                        config = self.fetch_gateway_config()
                        if config:
                            self.apply_gateway_config(config)
                    
                    time.sleep(self.sync_interval)
                
                except Exception as e:
                    print(f"Sync worker error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=sync_worker, daemon=True)
        thread.start()
    
    def stop(self):
        """Detener sincronización"""
        self.running = False
```

---

## 5. Motor de Alertas

```python
# gateway/src/alert_engine.py

"""
Motor de alertas local
Evalúa reglas de alertas contra lecturas de sensores
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Callable

class AlertSeverity(Enum):
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'

@dataclass
class AlertRule:
    """Regla de alerta"""
    sensor_id: str
    condition: str          # 'gt', 'lt', 'eq', 'range'
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 30  # Evitar spam de alertas

class AlertEngine:
    """Motor de evaluación de alertas"""
    
    def __init__(self, cloud_sync: 'CloudSyncManager'):
        self.cloud_sync = cloud_sync
        self.rules: List[AlertRule] = []
        self.alert_history = {}  # {rule_id: last_alert_timestamp}
    
    def add_rule(self, rule: AlertRule):
        """Agregar regla de alerta"""
        self.rules.append(rule)
    
    def evaluate(self, sensor_id: str, reading_value: float) -> Optional[dict]:
        """
        Evaluar lectura contra reglas aplicables
        
        Returns:
            Dict con detalles del alert o None si no se triggeó
        """
        applicable_rules = [
            r for r in self.rules 
            if r.sensor_id == sensor_id and r.enabled
        ]
        
        for rule in applicable_rules:
            if self._is_in_cooldown(rule.id):
                continue
            
            if self._matches_condition(reading_value, rule):
                alert = {
                    'sensor_id': sensor_id,
                    'rule_id': rule.id,
                    'value': reading_value,
                    'severity': rule.severity.value,
                    'timestamp': datetime.utcnow().isoformat(),
                    'message': f"Alert: {rule.description}"
                }
                
                # Marcar en cooldown
                self.alert_history[rule.id] = datetime.utcnow()
                
                # Queue para cloud
                self.cloud_sync.pending_alerts.append(alert)
                
                return alert
        
        return None
    
    def _matches_condition(self, value: float, rule: AlertRule) -> bool:
        """Verificar si lectura cumple la condición"""
        if rule.condition == 'gt':
            return value > rule.threshold
        elif rule.condition == 'lt':
            return value < rule.threshold
        elif rule.condition == 'eq':
            return abs(value - rule.threshold) < 0.1
        
        return False
    
    def _is_in_cooldown(self, rule_id: str) -> bool:
        """Verificar si regla está en cooldown"""
        if rule_id not in self.alert_history:
            return False
        
        last_alert = self.alert_history[rule_id]
        cooldown_expiry = last_alert + timedelta(minutes=30)
        
        return datetime.utcnow() < cooldown_expiry
```

