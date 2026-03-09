# EchoSmart — Esquema de Base de Datos

Documentación de los esquemas de PostgreSQL (datos relacionales) e InfluxDB (series de tiempo) utilizados por EchoSmart.

---

## 1. PostgreSQL — Modelo Relacional

### Diagrama de Entidad-Relación

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   tenants    │       │    users     │       │   gateways   │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │◄──┐   │ id (PK)      │   ┌──▶│ id (PK)      │
│ name         │   ├───│ tenant_id(FK)│   │   │ tenant_id(FK)│
│ slug         │   │   │ email        │   │   │ name         │
│ branding     │   │   │ password     │   │   │ location     │
│ plan         │   │   │ role         │   │   │ status       │
│ created_at   │   │   │ is_active    │   │   │ last_sync    │
└──────────────┘   │   └──────────────┘   │   └──────┬───────┘
                   │                       │          │
                   │   ┌──────────────┐   │   ┌──────▼───────┐
                   │   │ alert_rules  │   │   │   sensors    │
                   │   ├──────────────┤   │   ├──────────────┤
                   ├───│ tenant_id(FK)│   │   │ id (PK)      │
                   │   │ sensor_id(FK)│───┘   │ gateway_id(FK│
                   │   │ condition    │       │ tenant_id(FK)│
                   │   │ threshold    │       │ type         │
                   │   │ severity     │       │ name         │
                   │   │ cooldown     │       │ config       │
                   │   └──────────────┘       │ status       │
                   │                           └──────┬───────┘
                   │   ┌──────────────┐               │
                   │   │   alerts     │       ┌───────▼──────┐
                   │   ├──────────────┤       │  readings    │
                   ├───│ tenant_id(FK)│       ├──────────────┤
                       │ sensor_id(FK)│       │ id (PK)      │
                       │ rule_id (FK) │       │ sensor_id(FK)│
                       │ severity     │       │ value        │
                       │ message      │       │ unit         │
                       │ acknowledged │       │ timestamp    │
                       │ created_at   │       │ synced       │
                       └──────────────┘       └──────────────┘
```

### 1.1 Tabla `tenants`

Organizaciones o clientes que utilizan la plataforma.

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    max_gateways INTEGER DEFAULT 5,
    max_users INTEGER DEFAULT 10,
    branding JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
```

Campo `branding` (JSONB):

```json
{
  "logo_url": "https://cdn.example.com/logo.png",
  "primary_color": "#1E3A8A",
  "secondary_color": "#2D5A3D",
  "company_name": "AgriTech S.A."
}
```

### 1.2 Tabla `users`

Usuarios con acceso a la plataforma, asociados a un tenant.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_role CHECK (role IN ('admin', 'operator', 'viewer'))
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
```

### 1.3 Tabla `gateways`

Dispositivos Raspberry Pi registrados.

```sql
CREATE TABLE gateways (
    id VARCHAR(100) PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    status VARCHAR(50) DEFAULT 'offline',
    firmware_version VARCHAR(50),
    ip_address INET,
    last_sync_at TIMESTAMPTZ,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_status CHECK (status IN ('online', 'offline', 'error'))
);

CREATE INDEX idx_gateways_tenant ON gateways(tenant_id);
CREATE INDEX idx_gateways_status ON gateways(status);
```

### 1.4 Tabla `sensors`

Sensores conectados a un gateway.

```sql
CREATE TABLE sensors (
    id VARCHAR(100) PRIMARY KEY,
    gateway_id VARCHAR(100) NOT NULL REFERENCES gateways(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    unit VARCHAR(20) NOT NULL,
    polling_interval INTEGER DEFAULT 60,
    status VARCHAR(50) DEFAULT 'offline',
    config JSONB DEFAULT '{}',
    last_reading_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_type CHECK (type IN ('DS18B20', 'DHT22', 'BH1750', 'SOIL_MOISTURE', 'MHZ19C'))
);

CREATE INDEX idx_sensors_gateway ON sensors(gateway_id);
CREATE INDEX idx_sensors_tenant ON sensors(tenant_id);
CREATE INDEX idx_sensors_type ON sensors(type);
```

### 1.5 Tabla `alert_rules`

Reglas configurables para generar alertas.

```sql
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    sensor_id VARCHAR(100) NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    threshold DECIMAL(10, 2) NOT NULL,
    threshold_max DECIMAL(10, 2),
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    cooldown_minutes INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT true,
    notification_channels JSONB DEFAULT '["email"]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_condition CHECK (condition IN ('gt', 'lt', 'eq', 'range')),
    CONSTRAINT chk_severity CHECK (severity IN ('critical', 'high', 'medium', 'low'))
);

CREATE INDEX idx_alert_rules_sensor ON alert_rules(sensor_id);
CREATE INDEX idx_alert_rules_tenant ON alert_rules(tenant_id);
```

### 1.6 Tabla `alerts`

Alertas generadas cuando se cumple una regla.

```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    rule_id UUID NOT NULL REFERENCES alert_rules(id),
    sensor_id VARCHAR(100) NOT NULL REFERENCES sensors(id),
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    current_value DECIMAL(10, 2),
    threshold DECIMAL(10, 2),
    is_acknowledged BOOLEAN DEFAULT false,
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_alert_severity CHECK (severity IN ('critical', 'high', 'medium', 'low'))
);

CREATE INDEX idx_alerts_tenant ON alerts(tenant_id);
CREATE INDEX idx_alerts_sensor ON alerts(sensor_id);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX idx_alerts_acknowledged ON alerts(is_acknowledged) WHERE NOT is_acknowledged;
```

### 1.7 Tabla `reports`

Reportes generados de forma asincrónica.

```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    requested_by UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    format VARCHAR(10) NOT NULL DEFAULT 'pdf',
    status VARCHAR(20) DEFAULT 'pending',
    date_from TIMESTAMPTZ NOT NULL,
    date_to TIMESTAMPTZ NOT NULL,
    sensors JSONB NOT NULL,
    file_url TEXT,
    file_size BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT chk_format CHECK (format IN ('pdf', 'excel')),
    CONSTRAINT chk_report_status CHECK (status IN ('pending', 'processing', 'completed', 'error'))
);

CREATE INDEX idx_reports_tenant ON reports(tenant_id);
CREATE INDEX idx_reports_status ON reports(status);
```

---

## 2. InfluxDB — Series de Tiempo

### 2.1 Configuración

| Parámetro | Valor |
|-----------|-------|
| Organización | `echosmart` |
| Bucket | `sensors` |
| Retención por defecto | 90 días |

### 2.2 Estructura de Mediciones

```
measurement: sensor_readings

tags:
  - tenant_id    (string)  → Aislamiento multi-tenant
  - gateway_id   (string)  → Identificador del gateway
  - sensor_id    (string)  → Identificador del sensor
  - sensor_type  (string)  → DS18B20, DHT22, BH1750, etc.
  - location     (string)  → Ubicación del sensor

fields:
  - value        (float)   → Valor de la lectura
  - unit         (string)  → Unidad de medida
  - quality      (string)  → good, warning, error
```

### 2.3 Ejemplo de Escritura

```python
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

point = (
    Point("sensor_readings")
    .tag("tenant_id", "tenant-001")
    .tag("gateway_id", "gw-001")
    .tag("sensor_id", "temp-interior")
    .tag("sensor_type", "DS18B20")
    .tag("location", "Invernadero A")
    .field("value", 25.3)
    .field("unit", "°C")
    .field("quality", "good")
)

write_api.write(bucket="sensors", record=point)
```

### 2.4 Consultas Comunes (Flux)

**Última lectura de un sensor:**

```flux
from(bucket: "sensors")
  |> range(start: -1h)
  |> filter(fn: (r) => r.sensor_id == "temp-interior")
  |> last()
```

**Promedio por hora en las últimas 24 horas:**

```flux
from(bucket: "sensors")
  |> range(start: -24h)
  |> filter(fn: (r) => r.sensor_id == "temp-interior")
  |> filter(fn: (r) => r._field == "value")
  |> aggregateWindow(every: 1h, fn: mean)
```

**Mínimo y máximo del día:**

```flux
from(bucket: "sensors")
  |> range(start: -1d)
  |> filter(fn: (r) => r.sensor_id == "temp-interior")
  |> filter(fn: (r) => r._field == "value")
  |> min()

from(bucket: "sensors")
  |> range(start: -1d)
  |> filter(fn: (r) => r.sensor_id == "temp-interior")
  |> filter(fn: (r) => r._field == "value")
  |> max()
```

### 2.5 Políticas de Retención

| Bucket | Retención | Datos |
|--------|-----------|-------|
| `sensors` | 90 días | Lecturas crudas a resolución completa |
| `sensors_hourly` | 1 año | Agregaciones por hora (downsampled) |
| `sensors_daily` | 5 años | Agregaciones por día |

---

## 3. Redis — Caché y Sesiones

### 3.1 Uso por Categoría

| Clave | Tipo | TTL | Propósito |
|-------|------|-----|-----------|
| `session:{user_id}` | String | 30 días | Refresh token |
| `sensor:latest:{sensor_id}` | Hash | 5 min | Última lectura del sensor |
| `gateway:status:{gateway_id}` | String | 2 min | Estado del gateway |
| `rate_limit:{ip}:{endpoint}` | String | 1 min | Contador de rate limiting |
| `report:status:{report_id}` | String | 1 hora | Estado de generación de reporte |

---

## 4. SQLite — Caché Local del Gateway

### 4.1 Tabla `readings`

```sql
CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    synced INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_readings_synced ON readings(synced) WHERE synced = 0;
CREATE INDEX idx_readings_sensor ON readings(sensor_id);
```

### 4.2 Tabla `alert_history`

```sql
CREATE TABLE alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    sensor_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    current_value REAL,
    synced INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
```

---

*Volver al [Índice de Documentación](README.md)*
