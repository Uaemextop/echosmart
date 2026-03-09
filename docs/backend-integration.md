# EchoSmart - Documentación de Software Backend y Gateway Integrado

## 1. Arquitectura General Completa

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAPA CLOUD                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Backend FastAPI/Node.js                                 │   │
│  │  • REST API v1                                          │   │
│  │  • WebSocket (tiempo real)                              │   │
│  │  • JWT Auth + RBAC                                      │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Microservicios                                          │   │
│  │  • Alert Service (procesar alertas)                     │   │
│  │  • Report Service (generar reportes async)              │   │
│  │  • Sync Service (reconciliación)                        │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Persistencia                                            │   │
│  │  • PostgreSQL (metadata, usuarios)                      │   │
│  │  • InfluxDB (time-series)                               │   │
│  │  • Redis (cache, sessions)                              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
                            ↓ WebSocket
                            ↓ MQTT
┌─────────────────────────────────────────────────────────────────┐
│                        CAPA GATEWAY (Edge)                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Raspberry Pi 4B (Orchestration)                         │   │
│  │  • main.py (orquestador)                                │   │
│  │  • Sincronización cloud                                 │   │
│  │  • Motor de alertas local                               │   │
│  │  • Descubrimiento SSDP                                  │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Capa de Drivers (sensor_drivers/)                       │   │
│  │  • DS18B20 (1-Wire)                                     │   │
│  │  • DHT22 (GPIO)                                         │   │
│  │  • BH1750 (I2C)                                         │   │
│  │  • Soil Moisture (ADC)                                  │   │
│  │  • MHZ-19C (UART)                                       │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Hardware Abstraction Layer (hal.py)                     │   │
│  │  • GPIO Manager                                         │   │
│  │  • I2C Manager                                          │   │
│  │  • 1-Wire Manager                                       │   │
│  │  • UART Manager                                         │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Persistencia Local                                      │   │
│  │  • SQLite (cache local)                                 │   │
│  │  • MQTT Broker local (Mosquitto)                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓ GPIO/I2C/1-Wire/UART
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA SENSORES (Hardware)                     │
│  • DS18B20, DHT22, BH1750, Soil Moisture, MHZ-19C, Relés      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Flujo de Datos End-to-End

### 2.1 Lectura y Sincronización

```
1. LECTURA LOCAL
   ├─ Scheduler trigger (cada 60s)
   ├─ SensorManager.read_all_sensors()
   │  ├─ DS18B20.read() → 25.3°C
   │  ├─ DHT22.read() → (26.2°C, 65%)
   │  └─ BH1750.read() → 8500 lux
   ├─ Guardar en SQLite local
   └─ Enqueue en MQTT local

2. PUBLICACIÓN LOCAL (MQTT)
   ├─ Publicar en:
   │  ├─ sensors/temp-interior/data → 25.3°C
   │  ├─ sensors/humidity-exterior/data → 65%
   │  └─ sensors/lux-invernadero/data → 8500 lux
   └─ Suscriptores internos reciben actualización

3. EVALUACIÓN DE ALERTAS
   ├─ AlertEngine.evaluate() por cada lectura
   ├─ Comparar contra reglas configuradas
   ├─ Si se triggeó:
   │  ├─ Guardar en alert_history (SQLite)
   │  ├─ Encolar para envío a cloud
   │  └─ Notificar vía MQTT local: alerts/critical
   └─ Si no triggeó → continue

4. SINCRONIZACIÓN CON CLOUD
   ├─ CloudSyncManager.sync_readings()
   │  ├─ Batch pending_readings (típicamente 5 minutos)
   │  ├─ POST /api/v1/gateways/{id}/readings
   │  │   ├─ Headers: Authorization, X-Gateway-ID
   │  │   └─ Body: { readings: [...], timestamp }
   │  ├─ Si 200 OK → clear queue
   │  └─ Si error → retry con backoff exponencial
   ├─ Sincronizar alertas:
   │  └─ POST /api/v1/gateways/{id}/alerts
   └─ Fetch actualización de config (cada 1 hora)

5. RECEPCIÓN EN CLOUD
   ├─ Backend API recibe POST
   ├─ Validar token + gateway_id
   ├─ Desnormalizar lecturas:
   │  ├─ Insertar en InfluxDB (time-series)
   │  ├─ Actualizar último valor en PostgreSQL
   │  └─ Invalidar cache Redis
   ├─ Procesar alertas:
   │  ├─ Guardar en PostgreSQL
   │  ├─ Evaluar reglas cloud (por si acaso)
   │  ├─ Disparar notificaciones (email, SMS, push)
   │  └─ Publicar a WebSocket subscribers
   └─ Return 200 OK

6. FRONTEND/MÓVIL RECIBEN ACTUALIZACIÓN
   ├─ WebSocket: on message → update Redux
   ├─ Charts re-renderean con nuevos datos
   ├─ Alertas mostradas en real-time
   └─ Historial actualizado en background
```

---

## 2.2 Ejemplo de Payload de Sincronización

```json
// REQUEST: POST /api/v1/gateways/echosmart-gw-001/readings

{
  "gateway_id": "echosmart-gw-001",
  "timestamp": "2024-03-09T15:30:00Z",
  "readings": [
    {
      "sensor_id": "temp-interior",
      "sensor_type": "ds18b20",
      "value": 25.3,
      "unit": "°C",
      "timestamp": "2024-03-09T15:30:00Z",
      "metadata": {
        "battery": 100,
        "signal_strength": -45,
        "location": "Centro invernadero"
      }
    },
    {
      "sensor_id": "humidity-exterior",
      "sensor_type": "dht22",
      "value": 65.0,
      "unit": "%",
      "timestamp": "2024-03-09T15:30:00Z",
      "metadata": {
        "temperature": 26.2
      }
    },
    {
      "sensor_id": "lux-invernadero",
      "sensor_type": "bh1750",
      "value": 8500.0,
      "unit": "lux",
      "timestamp": "2024-03-09T15:30:00Z",
      "metadata": {}
    }
  ]
}

// RESPONSE: 200 OK

{
  "status": "success",
  "readings_ingested": 3,
  "next_sync_interval": 300,
  "config_version": "v2.1.0"
}
```

---

## 3. Base de Datos - Esquema Completo

### 3.1 PostgreSQL (Metadata + Operacional)

```sql
-- Tabla de gateways
CREATE TABLE gateways (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    gateway_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255),
    location VARCHAR(255),
    ip_address INET,
    online_status BOOLEAN DEFAULT false,
    last_heartbeat TIMESTAMP,
    config_version VARCHAR(20),
    software_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de sensores
CREATE TABLE sensors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gateway_id UUID NOT NULL REFERENCES gateways(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    sensor_id VARCHAR(100) NOT NULL,
    name VARCHAR(255),
    sensor_type VARCHAR(50),  -- ds18b20, dht22, bh1750, soil_moisture, mhz19c
    device_id VARCHAR(100),   -- Para sensores 1-Wire
    gpio_pin INTEGER,         -- Para sensores GPIO
    i2c_address VARCHAR(10),  -- Para sensores I2C
    unit VARCHAR(20),
    location VARCHAR(255),
    enabled BOOLEAN DEFAULT true,
    polling_interval_seconds INTEGER DEFAULT 60,
    retention_days INTEGER DEFAULT 30,
    calibration_offset FLOAT DEFAULT 0.0,
    last_reading FLOAT,
    last_reading_timestamp TIMESTAMP,
    is_online BOOLEAN DEFAULT false,
    error_count INTEGER DEFAULT 0,
    UNIQUE(gateway_id, sensor_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de valores actuales (caché)
CREATE TABLE sensor_current_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_id UUID NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    value FLOAT,
    timestamp TIMESTAMP,
    is_valid BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_sensor_id ON sensor_current_values(sensor_id);
CREATE INDEX idx_timestamp ON sensor_current_values(timestamp DESC);

-- Tabla de reglas de alertas
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    sensor_id UUID NOT NULL REFERENCES sensors(id),
    name VARCHAR(255),
    description TEXT,
    condition VARCHAR(20),  -- gt, lt, eq, range
    threshold_value FLOAT,
    threshold_min FLOAT,    -- Para range
    threshold_max FLOAT,    -- Para range
    severity VARCHAR(20),   -- critical, high, medium, low
    enabled BOOLEAN DEFAULT true,
    cooldown_minutes INTEGER DEFAULT 30,
    action VARCHAR(255),    -- email, sms, webhook
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de alertas disparadas (historial)
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    rule_id UUID NOT NULL REFERENCES alert_rules(id),
    sensor_id UUID NOT NULL REFERENCES sensors(id),
    value FLOAT,
    severity VARCHAR(20),
    status VARCHAR(20),     -- new, acknowledged, resolved
    message TEXT,
    triggered_at TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    acknowledged_by UUID,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_tenant_id_triggered ON alerts(tenant_id, triggered_at DESC);
CREATE INDEX idx_status ON alerts(status);

-- Tabla de reportes
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255),
    description TEXT,
    report_type VARCHAR(50),  -- summary, detailed, export
    date_from TIMESTAMP,
    date_to TIMESTAMP,
    format VARCHAR(20),       -- pdf, csv, xlsx
    status VARCHAR(20),       -- queued, generating, ready, failed
    file_url VARCHAR(1000),
    file_size_bytes INTEGER,
    generated_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de usuarios
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(20),         -- admin, operator, viewer
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de tenants (multi-tenant)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    company_name VARCHAR(255),
    subscription_tier VARCHAR(50),  -- free, pro, enterprise
    api_key VARCHAR(100) UNIQUE,
    branding_logo_url VARCHAR(1000),
    branding_primary_color VARCHAR(7),
    branding_secondary_color VARCHAR(7),
    max_sensors INTEGER DEFAULT 50,
    max_gateways INTEGER DEFAULT 5,
    storage_gb INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Crear índices para queries frecuentes
CREATE INDEX idx_sensors_gateway ON sensors(gateway_id);
CREATE INDEX idx_sensors_tenant ON sensors(tenant_id);
CREATE INDEX idx_alert_rules_tenant ON alert_rules(tenant_id);
CREATE INDEX idx_alerts_tenant_timestamp ON alerts(tenant_id, triggered_at DESC);
CREATE INDEX idx_reports_tenant ON reports(tenant_id);
```

### 3.2 InfluxDB (Time-Series Data)

```
Database: echosmart_timeseries

Measurement: sensor_readings
Tags:
  - gateway_id
  - sensor_id
  - sensor_type
  - location
  - tenant_id

Fields:
  - value (float)
  - unit (string)
  - is_valid (boolean)

Retention Policies:
  - default: 30 días
  - archive: 2 años (downsampled)

Queries típicas:
  // Último valor
  SELECT last(value) FROM sensor_readings 
  WHERE sensor_id='temp-interior' AND time > now() - 1h

  // Promedio últimas 24h
  SELECT mean(value) FROM sensor_readings 
  WHERE sensor_id='temp-interior' AND time > now() - 24h
  GROUP BY time(1h)

  // Máximo/Mínimo
  SELECT max(value), min(value) FROM sensor_readings 
  WHERE sensor_id='lux-invernadero' AND time > now() - 7d
```

---

## 4. APIs del Backend

### 4.1 Autenticación

```
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "securepass123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "operator"
  }
}

POST /api/v1/auth/refresh
Response: { "access_token": "..." }

POST /api/v1/auth/logout
Response: { "status": "success" }
```

### 4.2 Sensores

```
GET /api/v1/sensors
Query params: gateway_id, type, search, limit=50, offset=0

POST /api/v1/sensors
Body: {
  "gateway_id": "uuid",
  "name": "Sensor 1",
  "sensor_type": "ds18b20",
  "device_id": "28-0516a42651ff",
  "unit": "°C",
  "location": "Centro"
}

GET /api/v1/sensors/{sensor_id}
GET /api/v1/sensors/{sensor_id}/readings
Query params: from, to, interval=60

PUT /api/v1/sensors/{sensor_id}
PATCH /api/v1/sensors/{sensor_id}
DELETE /api/v1/sensors/{sensor_id}
```

### 4.3 Alertas

```
GET /api/v1/alerts
Query params: severity, status, sensor_id, limit=100

POST /api/v1/alerts/{alert_id}/acknowledge
Body: { "notes": "Already fixed" }

GET /api/v1/alert-rules
POST /api/v1/alert-rules
Body: {
  "sensor_id": "uuid",
  "condition": "gt",
  "threshold_value": 35,
  "severity": "critical"
}

DELETE /api/v1/alert-rules/{rule_id}
```

### 4.4 Reportes

```
POST /api/v1/reports/generate
Body: {
  "date_from": "2024-03-01T00:00:00Z",
  "date_to": "2024-03-09T23:59:59Z",
  "sensors": ["uuid1", "uuid2"],
  "format": "pdf"
}

Response: { "report_id": "uuid", "status": "queued" }

GET /api/v1/reports/{report_id}
Response: { "status": "ready", "file_url": "https://..." }

GET /api/v1/reports
Response: [{ "id": "uuid", "status": "ready", ... }]
```

---

## 5. WebSocket (Tiempo Real)

```
// Cliente conecta
ws://api.echosmart.com/ws/sensors?token={jwt_token}

// Cliente subscribe a sensores
{
  "type": "subscribe",
  "sensors": ["temp-interior", "humidity-exterior"]
}

// Servidor envía actualizaciones
{
  "type": "sensor_update",
  "sensor_id": "temp-interior",
  "value": 25.3,
  "timestamp": "2024-03-09T15:35:00Z"
}

// Servidor envía alertas
{
  "type": "alert_triggered",
  "alert_id": "uuid",
  "severity": "critical",
  "message": "Temperatura muy alta!"
}

// Cliente unsubscribe
{
  "type": "unsubscribe",
  "sensors": ["temp-interior"]
}
```

---

## 6. Docker Compose para Desarrollo Local

```yaml
# docker-compose.yml

version: '3.8'

services:
  # Backend
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/echosmart
      REDIS_URL: redis://redis:6379
      MQTT_URL: mqtt://mosquitto:1883
    depends_on:
      - postgres
      - redis
      - mosquitto
    volumes:
      - ./backend:/app
    command: uvicorn src.main:app --reload --host 0.0.0.0

  # Base de datos PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: echosmart
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # InfluxDB (time-series)
  influxdb:
    image: influxdb:2.7-alpine
    environment:
      INFLUXDB_DB: echosmart_timeseries
      INFLUXDB_ADMIN_USER: admin
      INFLUXDB_ADMIN_PASSWORD: admin123
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb2

  # Redis (cache)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # MQTT Broker
  mosquitto:
    image: eclipse-mosquitto:latest
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - mosquitto_data:/mosquitto/data

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend
    command: npm run dev

volumes:
  postgres_data:
  influxdb_data:
  mosquitto_data:
```

---

## 7. Monitoreo y Logging

### 7.1 Prometheus Metrics

```yaml
# prometheus.yml

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'echosmart-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'echosmart-gateway'
    static_configs:
      - targets: ['192.168.1.100:9090']
```

### 7.2 Logging (ELK Stack Opcional)

```python
# Backend logging config

import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)
handler = logging.FileHandler('echosmart.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Logs JSON estructurados
logger.info("Sensor reading", extra={
    'sensor_id': 'temp-interior',
    'value': 25.3,
    'gateway_id': 'gw-001',
    'tenant_id': 'tenant-123'
})
```

