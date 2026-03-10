# EchoSmart — Protocolos de Comunicación

Especificación de los protocolos de comunicación utilizados entre las capas del sistema EchoSmart.

---

## 1. MQTT (Message Queuing Telemetry Transport)

### 1.1 Descripción General

MQTT es el protocolo principal de mensajería dentro del gateway y, opcionalmente, entre el gateway y la nube. EchoSmart utiliza un broker **Mosquitto** local en cada Raspberry Pi.

| Parámetro | Valor |
|-----------|-------|
| Broker | Mosquitto 2.0+ |
| Puerto | 1883 (sin TLS) · 8883 (con TLS) |
| QoS utilizado | QoS 1 (al menos una entrega) |
| Versión del protocolo | MQTT 3.1.1 |

### 1.2 Estructura de Topics

```
echosmart/{gateway_id}/sensors/{sensor_id}/data      # Lecturas de sensores
echosmart/{gateway_id}/sensors/{sensor_id}/status     # Estado del sensor (online/offline)
echosmart/{gateway_id}/alerts/{alert_id}              # Alertas generadas
echosmart/{gateway_id}/system/status                  # Estado del gateway
echosmart/{gateway_id}/system/config                  # Configuración remota
```

### 1.3 Payload de Lectura de Sensor

```json
{
  "sensor_id": "temp-interior",
  "type": "DS18B20",
  "value": 25.3,
  "unit": "°C",
  "timestamp": "2026-03-09T21:00:00Z",
  "quality": "good"
}
```

### 1.4 Payload de Alerta

```json
{
  "alert_id": "alert-001",
  "sensor_id": "temp-interior",
  "rule_id": "rule-temp-high",
  "severity": "high",
  "condition": "value > 35",
  "current_value": 36.2,
  "threshold": 35.0,
  "message": "Temperatura interior excede el umbral máximo",
  "timestamp": "2026-03-09T21:05:00Z"
}
```

---

## 2. Protocolo 1-Wire (Dallas)

### 2.1 Descripción

Protocolo de un solo cable utilizado por el sensor **DS18B20** para la lectura de temperatura. La Raspberry Pi lo expone a través del sistema de archivos virtual en `/sys/bus/w1/devices/`.

| Parámetro | Valor |
|-----------|-------|
| Pin de datos | GPIO4 (configurable) |
| Resistor pull-up | 4.7 kΩ entre VDD y DQ |
| Velocidad | Estándar (~16 kbps) |
| Alimentación | Parásita o externa (3.3 V) |

### 2.2 Secuencia de Lectura

1. El master (Raspberry Pi) envía un pulso de reset.
2. El sensor responde con un pulso de presencia.
3. El master emite el comando `Convert T` (0x44).
4. Esperar hasta 750 ms para la conversión.
5. Leer el scratchpad con el comando `Read Scratchpad` (0xBE).
6. Decodificar los 2 bytes de temperatura.

### 2.3 Lectura desde el Sistema de Archivos

```bash
# Listar dispositivos 1-Wire
ls /sys/bus/w1/devices/
# Ejemplo: 28-0516a42651ff

# Leer temperatura
cat /sys/bus/w1/devices/28-0516a42651ff/w1_slave
# Salida:
# 73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
# 73 01 4b 46 7f ff 0d 10 41 t=23187
# Temperatura = 23187 / 1000 = 23.187 °C
```

---

## 3. Protocolo I2C

### 3.1 Descripción

Bus de comunicación serial de 2 hilos utilizado por el sensor **BH1750** (luminosidad) y el ADC **ADS1115** (lectura de sensores analógicos).

| Parámetro | Valor |
|-----------|-------|
| SDA | GPIO2 (Pin 3) |
| SCL | GPIO3 (Pin 5) |
| Velocidad | 100 kHz (estándar) |
| Direcciones utilizadas | `0x23` (BH1750) · `0x48` (ADS1115) |

### 3.2 Escaneo del Bus I2C

```bash
i2cdetect -y 1
```

Salida esperada con BH1750 y ADS1115 conectados:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- 23 -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

### 3.3 Comunicación con BH1750

1. Enviar comando de encendido: `0x01`.
2. Enviar modo de medición continua de alta resolución: `0x10`.
3. Esperar 180 ms.
4. Leer 2 bytes del sensor.
5. Calcular lux: `(byte_alto << 8 | byte_bajo) / 1.2`.

---

## 4. Protocolo UART / Serial

### 4.1 Descripción

Comunicación serial utilizada por el sensor de CO₂ **MHZ-19C**.

| Parámetro | Valor |
|-----------|-------|
| Puerto | `/dev/serial0` |
| Baudrate | 9600 |
| Data bits | 8 |
| Stop bits | 1 |
| Paridad | Ninguna |
| TX | GPIO14 (Pin 8) |
| RX | GPIO15 (Pin 10) |

### 4.2 Comando de Lectura de CO₂

Enviar 9 bytes al sensor:

```
Byte:  [0xFF] [0x01] [0x86] [0x00] [0x00] [0x00] [0x00] [0x00] [0x79]
       Start   Cmd    Read   Reserved...                          Checksum
```

### 4.3 Respuesta del Sensor

```
Byte:  [0xFF] [0x86] [HIGH] [LOW] [Temp] [...] [Checksum]
CO₂ (ppm) = HIGH × 256 + LOW
```

### 4.4 Cálculo de Checksum

```python
def calculate_checksum(data: bytes) -> int:
    """Calcula checksum para protocolo MHZ-19C"""
    checksum = sum(data[1:8])
    checksum = (~checksum & 0xFF) + 1
    return checksum & 0xFF
```

---

## 5. Protocolo GPIO (DHT22)

### 5.1 Descripción

El sensor **DHT22** utiliza un protocolo propietario de un solo cable sobre GPIO para transmitir temperatura y humedad.

| Parámetro | Valor |
|-----------|-------|
| Pin de datos | GPIO17 (configurable) |
| Resistor pull-up | 10 kΩ entre VDD y DATA |
| Intervalo mínimo entre lecturas | 2 segundos |
| Voltaje | 3.3 V – 5.5 V |

### 5.2 Secuencia de Comunicación

1. **Inicio** — El host baja la línea 1–10 ms, luego la libera.
2. **Respuesta** — El sensor baja la línea 80 µs, luego la sube 80 µs.
3. **Datos** — 40 bits (5 bytes):
   - Byte 1–2: Humedad relativa (entero + decimal).
   - Byte 3–4: Temperatura (entero + decimal).
   - Byte 5: Checksum (suma de los 4 bytes anteriores).

### 5.3 Decodificación

```python
# Ejemplo de decodificación
humidity = ((data[0] << 8) + data[1]) / 10.0       # % HR
temperature = (((data[2] & 0x7F) << 8) + data[3]) / 10.0  # °C
if data[2] & 0x80:
    temperature = -temperature  # Valor negativo
```

---

## 6. Protocolo HTTP REST (Gateway → Cloud)

### 6.1 Sincronización de Lecturas

```
POST /api/v1/gateways/{gateway_id}/readings
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "gateway_id": "gw-001",
  "batch": [
    {
      "sensor_id": "temp-interior",
      "value": 25.3,
      "unit": "°C",
      "timestamp": "2026-03-09T21:00:00Z"
    },
    {
      "sensor_id": "hum-interior",
      "value": 65.2,
      "unit": "%",
      "timestamp": "2026-03-09T21:00:00Z"
    }
  ],
  "sync_timestamp": "2026-03-09T21:05:00Z"
}
```

### 6.2 Estrategia de Reintento

| Intento | Espera | Descripción |
|---------|--------|-------------|
| 1 | 0 s | Envío inmediato |
| 2 | 5 s | Primer reintento |
| 3 | 15 s | Backoff exponencial |
| 4 | 45 s | Backoff exponencial |
| 5+ | 120 s | Máximo entre reintentos |

Si tras 5 intentos no se logra la sincronización, las lecturas permanecen en la cola local (SQLite) y se reintentan en el próximo ciclo de sincronización.

---

## 7. WebSocket (Backend → Frontend)

### 7.1 Conexión

```
WS /ws/sensors?token=<jwt_access_token>
```

### 7.2 Suscripción a un Sensor

```json
{
  "action": "subscribe",
  "sensor_id": "temp-interior"
}
```

### 7.3 Evento de Actualización

```json
{
  "event": "sensor_update",
  "data": {
    "sensor_id": "temp-interior",
    "value": 25.3,
    "unit": "°C",
    "timestamp": "2026-03-09T21:00:05Z"
  }
}
```

### 7.4 Evento de Alerta

```json
{
  "event": "alert",
  "data": {
    "alert_id": "alert-001",
    "severity": "high",
    "message": "Temperatura interior excede el umbral máximo",
    "sensor_id": "temp-interior",
    "timestamp": "2026-03-09T21:05:00Z"
  }
}
```

---

*Volver al [Índice de Documentación](README.md)*
