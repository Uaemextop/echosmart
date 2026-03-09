# EchoSmart - Documentación Detallada de Sensores

## 1. Catálogo Completo de Sensores Soportados

### 1.1 DS18B20 - Sensor Digital de Temperatura

**Especificaciones Técnicas:**
```
Sensor:           DS18B20 (Dallas Semiconductor)
Protocolo:        1-Wire (Dallas OneWire)
Rango:            -55°C a +125°C
Precisión:        ±0.5°C
Resolución:       0.0625°C (configurable: 9-12 bits)
Tiempo lectura:   750ms máximo
Voltaje:          3.3V - 5.5V
Corriente:        Máx 1.5mA durante conversión
Interfaz:         1 pin digital (GND, DQ, VDD)
```

**Diagrama de Conexión (Raspberry Pi):**
```
DS18B20
┌─────────────┐
│  1  2  3    │
│GND DQ VDD   │
└─────────────┘
 │  │  │
 │  │  └──→ Pin 1 (3.3V)
 │  │       + Resistor Pull-up 4.7kΩ
 │  │
 │  └──→ GPIO4 (Pin 7) - 1-Wire Data
 │
 └──→ GND

Conexión Pull-up:
    3.3V ─┬─ R(4.7kΩ) ─┬─ GPIO4
          │            │
       DS18B20 VDD   DS18B20 DQ
```

**Configuración en Linux:**
```bash
# 1. Habilitar 1-Wire en /boot/firmware/config.txt
dtoverlay=w1-gpio,gpiopin=4

# 2. Rebootear
sudo reboot

# 3. Verificar módulo cargado
lsmod | grep w1_

# 4. Listar dispositivos 1-Wire
ls -la /sys/bus/w1/devices/ | grep 28-

# Ejemplo de salida:
# lrwxrwxrwx  28-0516a42651ff (ID serial)
```

**Lectura de Temperatura:**
```bash
# Leer archivo del sensor
cat /sys/bus/w1/devices/28-0516a42651ff/w1_slave

Ejemplo de salida:
f7 01 4b 46 7f ff 00 10 c4 : crc=c4 YES
3d 01 4b 46 7f ff 00 10 c4 t=19250

# Significado:
# t=19250 → 19.250°C = 19250 / 1000
```

**Código Python de Lectura:**
```python
def read_ds18b20(device_id: str) -> float:
    """
    Leer temperatura de DS18B20
    
    Args:
        device_id: ID del dispositivo (ej: '28-0516a42651ff')
    
    Returns:
        Temperatura en °C
    """
    path = f'/sys/bus/w1/devices/{device_id}/w1_slave'
    
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
        
        # Verificar CRC
        if lines[0].strip()[-3:] != 'YES':
            raise ValueError("CRC check failed")
        
        # Extraer temperatura
        pos = lines[1].find('t=')
        if pos == -1:
            raise ValueError("Temperature value not found")
        
        temp_raw = int(lines[1][pos+2:])
        return temp_raw / 1000.0
    
    except Exception as e:
        print(f"Error reading {device_id}: {e}")
        raise
```

**Configuración de Resolución:**
```python
# Set 12-bit (0.0625°C resolution)
def set_resolution(device_id: str, bits: int = 12):
    """
    Configurar resolución del sensor
    
    bits:  9 = 0.5°C, 93.75ms
           10 = 0.25°C, 187.5ms
           11 = 0.125°C, 375ms
           12 = 0.0625°C, 750ms
    """
    path = f'/sys/bus/w1/devices/{device_id}/resolution'
    with open(path, 'w') as f:
        f.write(str(bits))
```

---

### 1.2 DHT22 - Sensor Análogo de Temperatura y Humedad

**Especificaciones Técnicas:**
```
Sensor:           DHT22 (Digital Humidity & Temperature)
Protocolo:        Propietario digital (DHT Protocol)
Rango Temp:       -40°C a +80°C
Precisión Temp:   ±0.5°C
Rango Humedad:    0% a 100%
Precisión Humedad: ±2% (típico)
Tiempo lectura:   2 segundos (completo)
Voltaje:          3.3V - 5.5V (típicamente 3.3V en RPI)
Interfaz:         1 pin digital (GND, DATA, VCC)
Requiere:         Librería software para timing crítico
```

**Diagrama de Conexión:**
```
DHT22
┌─────────────┐
│  1  2  3  4 │
│GND - DATA VCC│
└─────────────┘
 │     │    │
 │     │    └──→ 3.3V
 │     │
 │     ├──→ GPIO17 (Pull-up 10kΩ incluida en módulo)
 │     │       + Resistor Pull-up 10kΩ (externa recomendada)
 │
 └──→ GND

Conexión Pull-up (opcional pero recomendada):
    3.3V ─┬─ R(10kΩ) ─┬─ GPIO17
          │            │
        DHT22 VCC   DHT22 DATA
```

**Instalación de Librería:**
```bash
pip install Adafruit-DHT

# Alternativa: Compilar desde source
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python3 setup.py install
```

**Código Python de Lectura:**
```python
import Adafruit_DHT

# Sensor: DHT22, GPIO pin
sensor = Adafruit_DHT.DHT22
pin = 17

# Lectura simple
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

if humidity is not None and temperature is not None:
    print(f"Temperatura: {temperature:.1f}°C")
    print(f"Humedad: {humidity:.1f}%")
else:
    print("Error de lectura")

# Con reintentos (recomendado)
humidity, temp = Adafruit_DHT.read_retry(
    sensor, 
    pin,
    retries=5,          # Intentos
    delay_seconds=1     # Espera entre intentos
)
```

**Clase Wrapper Robusta:**
```python
class DHT22Reader:
    """Lector DHT22 con error handling"""
    
    def __init__(self, gpio_pin: int):
        self.pin = gpio_pin
        self.sensor = Adafruit_DHT.DHT22
        self.last_temp = None
        self.last_humidity = None
        self.error_count = 0
        self.max_errors = 5
    
    def read(self) -> tuple:
        """
        Leer temperatura y humedad
        
        Returns:
            (temperatura, humedad) o (None, None) si error
        """
        try:
            humidity, temperature = Adafruit_DHT.read_retry(
                self.sensor,
                self.pin,
                retries=3
            )
            
            if temperature is None or humidity is None:
                self.error_count += 1
                if self.error_count >= self.max_errors:
                    raise RuntimeError("Sensor no responde después de 5 intentos")
                return (self.last_temp, self.last_humidity)
            
            self.error_count = 0
            self.last_temp = temperature
            self.last_humidity = humidity
            
            return (temperature, humidity)
        
        except Exception as e:
            print(f"DHT22 error: {e}")
            return (None, None)
```

---

### 1.3 BH1750 - Sensor de Luminosidad (I2C)

**Especificaciones Técnicas:**
```
Sensor:           BH1750 (ROHM)
Protocolo:        I2C
Rango:            1 - 65535 lux
Precisión:        ±15% (típico)
Resolución:       0.5 lux a 1 lux (depende modo)
Voltaje:          2.4V - 3.6V (típicamente 3.3V)
Corriente:        Standby 1μA, Active 120-190μA
Interfaz:         SDA, SCL (I2C), GND, VCC
Dirección I2C:    0x23 (default) o 0x5C (con ADDR=HIGH)
```

**Diagrama de Conexión:**
```
BH1750
┌──────────────────┐
│ VCC GND ADDR SDA SCL │
└──────────────────┘
  │   │    │   │   │
  │   │    │   │   └──→ GPIO3 (SCL - I2C Clock)
  │   │    │   └──────→ GPIO2 (SDA - I2C Data)
  │   │    │
  │   │    └──────────→ GND (selecciona 0x23 como dirección)
  │   │
  │   └──────────────→ GND
  │
  └──────────────────→ 3.3V

Pull-ups I2C (típicamente ya en Raspberry Pi):
    3.3V ─┬─ R(1.8kΩ) ─┬─ SDA (GPIO2)
          │            │
       RPi               │
          │
    3.3V ─┬─ R(1.8kΩ) ─┬─ SCL (GPIO3)
          │            │
       RPi
```

**Verificación de I2C:**
```bash
# Instalar herramientas I2C
sudo apt install -y i2c-tools

# Habilitar I2C en raspi-config
sudo raspi-config
# Interfacing Options → I2C → Enable

# Detectar direcciones I2C disponibles
i2cdetect -y 1

Salida esperada:
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- 23 -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
...

El 23 indica BH1750 en dirección 0x23
```

**Código Python de Lectura:**
```python
import board
import busio
import adafruit_bh1750

# Crear objeto I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Crear sensor
sensor = adafruit_bh1750.Adafruit_BH1750(i2c)

# Leer luminosidad
lux = sensor.lux

print(f"Luminosidad: {lux} lux")

# Modos de medición
# CONTINUOUS_HIGH_RES_MODE (default): 1 lux resolution, 180ms
# CONTINUOUS_HIGH_RES_MODE_2: 0.5 lux resolution, 180ms
# CONTINUOUS_LOW_RES_MODE: 4 lux resolution, 24ms
# ONE_TIME_HIGH_RES_MODE: single measurement
```

**Clase Wrapper:**
```python
class BH1750Reader:
    """Lector BH1750 con estadísticas"""
    
    def __init__(self, i2c_bus):
        self.i2c = i2c_bus
        self.address = 0x23
        self.readings_history = []
        self.max_history = 100
    
    def initialize(self) -> bool:
        """Inicializar sensor"""
        try:
            # Power ON
            self.i2c.writeto(self.address, bytes([0x01]))
            
            # Set measurement mode: High Resolution Mode
            self.i2c.writeto(self.address, bytes([0x10]))
            
            return True
        except:
            return False
    
    def read_lux(self) -> float:
        """
        Leer luminosidad en lux
        
        Returns:
            Valor en lux
        """
        try:
            data = self.i2c.readfrom(self.address, 2)
            
            # Convertir bytes a lux
            raw = (data[0] << 8) | data[1]
            lux = raw / 1.2  # Factor de conversión
            
            # Guardar en historial
            self.readings_history.append(lux)
            if len(self.readings_history) > self.max_history:
                self.readings_history.pop(0)
            
            return lux
        
        except Exception as e:
            print(f"BH1750 read error: {e}")
            return None
    
    def get_average(self, window: int = 10) -> float:
        """Obtener promedio de últimas N lecturas"""
        if not self.readings_history:
            return None
        
        recent = self.readings_history[-window:]
        return sum(recent) / len(recent)
```

---

### 1.4 Sensor de Humedad del Suelo (Análogo + ADC)

**Especificaciones Técnicas:**
```
Sensor:           Capacitivo (típicamente)
Salida:           Análoga 0-3.3V
Rango Humedad:    0% - 100% (calibrable)
Resolución:       12-bit con ADS1115 (0.1% típico)
Interfaz:         Análoga → ADC (I2C) → Raspberry Pi
Requiere:         Convertidor ADC externo (ADS1115 o similar)
Voltaje:          3.3V - 5V
Corriente:        ~5-10mA
```

**Diagrama de Conexión:**
```
Sensor Humedad Suelo       ADS1115 (I2C ADC)      Raspberry Pi
┌─────────────────┐        ┌──────────────┐       ┌──────────┐
│ GND  Análogo VCC│        │ GND  VCC SCL SDA ADDR│  SCL SDA │
└─────────────────┘        └──────────────┘       └──────────┘
  │    │     │               │    │   │   │   │      │   │
  │    └─────┼───────────────┼────┤ A0│   │   │      │   │
  │          │               │    │   │   │   │      │   │
  └──────────┼───────────────┼────┤GND│   │   │      │   │
             │               │    │   │   │   │      │   │
             └───────────────┼────┤ A3│   │   │      │   │
                             │    │   │   │   │      │   │
                             └────┼───┼───┼───┴──────┴───┘
                                  │   │   │
                                  │   │   └─ GPIO3 (SDA)
                                  │   └───── GPIO2 (SCL)
                                  └──────── GND
```

**Código Python con ADS1115:**
```python
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Crear I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Crear ADC
ads = ADS.ADS1115(i2c, address=0x48)

# Entrada análoga en A0
channel = AnalogIn(ads, ADS.P0)

# Leer valor
voltage = channel.voltage
value = channel.value  # 0-32767 (16-bit)

print(f"Voltaje: {voltage:.2f}V")
print(f"Valor ADC: {value}")

# Convertir a porcentaje de humedad
# Calibración necesaria:
# - Sensor en aire seco: ~3.3V (lectura máxima)
# - Sensor en agua: ~0V (lectura mínima)

def voltage_to_humidity(voltage: float, 
                       dry_voltage: float = 3.3,
                       wet_voltage: float = 0.0) -> float:
    """
    Convertir voltaje a porcentaje de humedad
    
    Args:
        voltage: Voltaje leído
        dry_voltage: Voltaje en aire seco (calibración)
        wet_voltage: Voltaje en agua (calibración)
    
    Returns:
        Porcentaje de humedad 0-100%
    """
    humidity = 100 * ((dry_voltage - voltage) / (dry_voltage - wet_voltage))
    return max(0, min(100, humidity))
```

**Script de Calibración:**
```python
def calibrate_soil_sensor():
    """Script interactivo para calibración"""
    
    input("Coloca el sensor en aire seco. Presiona Enter...")
    dry_readings = [read_adc() for _ in range(10)]
    dry_voltage = sum(dry_readings) / 10
    print(f"Voltaje en aire seco: {dry_voltage:.2f}V")
    
    input("Coloca el sensor en agua. Presiona Enter...")
    wet_readings = [read_adc() for _ in range(10)]
    wet_voltage = sum(wet_readings) / 10
    print(f"Voltaje en agua: {wet_voltage:.2f}V")
    
    print(f"\nGuarda estos valores en config:")
    print(f"DRY_VOLTAGE = {dry_voltage}")
    print(f"WET_VOLTAGE = {wet_voltage}")
```

---

### 1.5 MHZ-19C - Sensor de CO2 (UART)

**Especificaciones Técnicas:**
```
Sensor:           MHZ-19C (NDIR)
Protocolo:        UART Serial
Rango:            0 - 5000 ppm CO2
Precisión:        ±50ppm + 5% del reading
Tiempo lectura:   1 segundo
Voltaje:          5V ± 0.5V (tolerancia 4.5-5.5V)
Corriente:        ~50mA promedio
Interfaz:         TX, RX, GND, VCC
Pre-calentamiento: ~3 minutos (recomendado)
```

**Diagrama de Conexión:**
```
MHZ-19C                          Raspberry Pi
┌─────────────────────┐          ┌──────────┐
│ 1  2  3  4  5  6    │          │          │
│GND VCC TX RX - -    │          │ GPIO14   │
└─────────────────────┘          │ GPIO15   │
  │   │   │  │                   │          │
  │   │   │  └───────────────────┼─ RX(15) │
  │   │   └───────────────────────┼─ TX(14) │
  │   │                           │          │
  │   └───────────────────────────┼─ 5V     │
  │                               │          │
  └───────────────────────────────┼─ GND    │
                                  └──────────┘
                                  
Nota: Raspberry Pi UART está en 3.3V
      MHZ-19C espera 5V en entrada RX
      Usar divisor de voltaje o Level Shifter
```

**Nivel Shifter para UART:**
```
     5V from MHZ19C ─┬─ R1(10kΩ) ─┬─ GPIO15 (RX 3.3V)
                     │            │
                   R2(10kΩ)       GND
```

**Código Python con UART:**
```python
import serial
import time

class MHZ19C:
    """Lector de sensor MHZ-19C CO2"""
    
    def __init__(self, port: str = '/dev/ttyAMA0', baudrate: int = 9600):
        """
        Args:
            port: Puerto serial (UART0 en RPi: /dev/ttyAMA0)
            baudrate: Velocidad en baudios (9600 o 2400)
        """
        self.ser = serial.Serial(port, baudrate, timeout=2)
        self.warmup_time = 180  # 3 minutos
    
    def get_co2(self) -> int:
        """
        Obtener lectura de CO2 en ppm
        
        Returns:
            Concentración CO2 en ppm
        """
        # Comando para lectura
        command = bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
        
        try:
            self.ser.write(command)
            time.sleep(0.1)
            
            response = self.ser.read(9)
            
            if len(response) < 9:
                return None
            
            # Verificar checksum
            if not self._verify_checksum(response):
                return None
            
            # Extraer CO2: bytes 2-3
            co2 = (response[2] << 8) | response[3]
            
            return co2
        
        except Exception as e:
            print(f"MHZ19C read error: {e}")
            return None
    
    def _verify_checksum(self, data: bytes) -> bool:
        """Verificar checksum del mensaje"""
        checksum = sum(data[1:8]) & 0xFF
        return checksum == data[8]
    
    def calibrate_zero_point(self):
        """
        Calibración de punto cero (aire fresco)
        Realizado después de 24 horas en aire fresco
        """
        command = bytes([0xFF, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78])
        self.ser.write(command)
        print("Sensor calibrado al punto cero")
```

---

## 2. Integración Múltiple de Sensores

### 2.1 Gestor Centralizado de Sensores

```python
# gateway/src/sensor_manager.py

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

@dataclass
class SensorReading:
    """Estructura de lectura de sensor"""
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    is_valid: bool
    error_message: Optional[str] = None

class SensorManager:
    """Gestor centralizado de todos los sensores"""
    
    def __init__(self, config_path: str = '/etc/echosmart/sensors.json'):
        self.config_path = config_path
        self.sensors = {}  # {sensor_id: SensorInstance}
        self.config = self._load_config()
        self._initialize_sensors()
    
    def _load_config(self) -> dict:
        """Cargar configuración de sensores desde JSON"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _initialize_sensors(self):
        """Inicializar todos los sensores desde configuración"""
        for sensor_config in self.config.get('sensors', []):
            sensor_id = sensor_config['id']
            sensor_type = sensor_config['type']
            
            try:
                if sensor_type == 'ds18b20':
                    from gateway.src.sensor_drivers.ds18b20 import DS18B20
                    self.sensors[sensor_id] = DS18B20(
                        device_id=sensor_config['device_id']
                    )
                
                elif sensor_type == 'dht22':
                    from gateway.src.sensor_drivers.dht22 import DHT22
                    self.sensors[sensor_id] = DHT22(
                        gpio_pin=sensor_config['pin']
                    )
                
                elif sensor_type == 'bh1750':
                    from gateway.src.sensor_drivers.bh1750 import BH1750
                    self.sensors[sensor_id] = BH1750(
                        i2c_bus=self.i2c,
                        address=sensor_config.get('address', 0x23)
                    )
                
                # Inicializar sensor
                if self.sensors[sensor_id].initialize():
                    print(f"✓ Sensor {sensor_id} ({sensor_type}) inicializado")
                else:
                    print(f"✗ Error inicializando {sensor_id}")
            
            except Exception as e:
                print(f"✗ Error creando sensor {sensor_id}: {e}")
    
    def read_sensor(self, sensor_id: str) -> SensorReading:
        """
        Leer un sensor individual
        
        Returns:
            SensorReading con resultado
        """
        if sensor_id not in self.sensors:
            return SensorReading(
                sensor_id=sensor_id,
                sensor_type='unknown',
                value=None,
                unit='',
                timestamp=datetime.utcnow().isoformat(),
                is_valid=False,
                error_message="Sensor no encontrado"
            )
        
        sensor_config = next(
            (s for s in self.config['sensors'] if s['id'] == sensor_id),
            None
        )
        
        try:
            sensor_instance = self.sensors[sensor_id]
            value = sensor_instance.read()
            
            return SensorReading(
                sensor_id=sensor_id,
                sensor_type=sensor_config['type'],
                value=value,
                unit=sensor_config.get('unit', ''),
                timestamp=datetime.utcnow().isoformat(),
                is_valid=True
            )
        
        except Exception as e:
            return SensorReading(
                sensor_id=sensor_id,
                sensor_type=sensor_config['type'],
                value=None,
                unit='',
                timestamp=datetime.utcnow().isoformat(),
                is_valid=False,
                error_message=str(e)
            )
    
    def read_all_sensors(self) -> List[SensorReading]:
        """Leer todos los sensores"""
        readings = []
        for sensor_id in self.sensors.keys():
            reading = self.read_sensor(sensor_id)
            readings.append(reading)
        return readings
    
    def store_readings(self, readings: List[SensorReading], db):
        """
        Guardar lecturas en base de datos local (SQLite)
        
        Args:
            readings: Lista de SensorReading
            db: Conexión SQLite
        """
        cursor = db.cursor()
        
        for reading in readings:
            cursor.execute("""
                INSERT INTO sensor_readings 
                (sensor_id, sensor_type, value, unit, timestamp, is_valid, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                reading.sensor_id,
                reading.sensor_type,
                reading.value,
                reading.unit,
                reading.timestamp,
                reading.is_valid,
                reading.error_message
            ))
        
        db.commit()
```

### 2.2 Archivo de Configuración de Sensores

```json
// /etc/echosmart/sensors.json

{
  "gateway_id": "echosmart-gw-001",
  "gateway_name": "Invernadero A",
  "timezone": "America/Mexico_City",
  
  "sensors": [
    {
      "id": "temp-interior",
      "name": "Temperatura Interior",
      "type": "ds18b20",
      "device_id": "28-0516a42651ff",
      "unit": "°C",
      "location": "Centro del invernadero",
      "enabled": true,
      "polling_interval_seconds": 60,
      "retention_days": 30
    },
    {
      "id": "temp-humidity-exterior",
      "name": "Temperatura y Humedad Exterior",
      "type": "dht22",
      "pin": 17,
      "unit_temp": "°C",
      "unit_humidity": "%",
      "location": "Exterior, sombreado",
      "enabled": true,
      "polling_interval_seconds": 120,
      "retention_days": 30
    },
    {
      "id": "luz-invernadero",
      "name": "Luminosidad",
      "type": "bh1750",
      "address": "0x23",
      "unit": "lux",
      "location": "Centro superior",
      "enabled": true,
      "polling_interval_seconds": 300,
      "retention_days": 7
    },
    {
      "id": "humedad-suelo-1",
      "name": "Humedad Suelo Sector 1",
      "type": "soil_moisture",
      "adc_channel": 0,
      "dry_voltage": 3.3,
      "wet_voltage": 0.0,
      "unit": "%",
      "location": "Sector 1 - Tomates",
      "enabled": true,
      "polling_interval_seconds": 600,
      "retention_days": 30
    }
  ],
  
  "alerts": [
    {
      "sensor_id": "temp-interior",
      "condition": "gt",
      "threshold": 35,
      "severity": "critical",
      "enabled": true,
      "cooldown_minutes": 30,
      "description": "Temperatura muy alta en invernadero"
    },
    {
      "sensor_id": "humedad-suelo-1",
      "condition": "lt",
      "threshold": 20,
      "severity": "warning",
      "enabled": true,
      "cooldown_minutes": 120,
      "description": "Humedad del suelo baja"
    }
  ]
}
```

