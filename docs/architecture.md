# EchoSmart Architecture

## System Overview

EchoSmart is a multi-tenant IoT greenhouse monitoring platform composed of four main layers: sensor devices, an edge gateway, a cloud backend, and a React frontend.

---

## 1. Auto-Discovery Flow

```mermaid
sequenceDiagram
    participant Sensor
    participant Gateway
    participant SQLite
    participant CloudBackend
    participant PostgreSQL

    Sensor->>Gateway: SSDP M-SEARCH response (UUID, type, capabilities)
    Gateway->>SQLite: Upsert sensor record (pending_cloud_sync=true)
    Gateway->>Gateway: mqtt_handler.create_topics(uuid)
    loop every 60s
        Gateway->>CloudBackend: POST /api/sensors/register
        CloudBackend->>PostgreSQL: INSERT/UPDATE sensors
        CloudBackend-->>Gateway: { sensor_id, tenant_id, mqtt_topic_data, mqtt_topic_config }
        Gateway->>SQLite: SET pending_cloud_sync=false, tenant_id
    end
```

---

## 2. Microservices Architecture

```mermaid
graph TD
    Browser["React Frontend\n(port 5173)"]
    Backend["Node/Express Backend\n(port 3000)"]
    Gateway["FastAPI Gateway\n(port 8000)"]
    MQTT["Mosquitto MQTT\n(port 1883)"]
    PG["PostgreSQL\n(port 5432)"]
    Redis["Redis\n(port 6379)"]
    InfluxDB["InfluxDB\n(port 8086)"]
    Sensors["IoT Sensors"]

    Browser -->|REST + cookies| Backend
    Backend -->|SQL| PG
    Backend -->|cache / queues| Redis
    Backend -->|time-series stub| InfluxDB
    Backend -->|pub/sub| MQTT
    Gateway -->|pub/sub| MQTT
    Gateway -->|register| Backend
    Sensors -->|SSDP discovery| Gateway
    Sensors -->|HTTP heartbeat + data| Gateway
```

---

## 3. Multi-Tenant Data Model

```mermaid
erDiagram
    tenants {
        UUID id PK
        VARCHAR name
        VARCHAR plan
        VARCHAR status
        INTEGER max_sensors
        INTEGER max_users
    }
    tenant_settings {
        UUID id PK
        UUID tenant_id FK
        TEXT logo_url
        VARCHAR primary_color
        VARCHAR secondary_color
        VARCHAR company_name
        TEXT email_signature_html
        VARCHAR timezone
    }
    users {
        UUID id PK
        UUID tenant_id FK
        VARCHAR email
        VARCHAR role
        BOOLEAN email_verified
    }
    sensors {
        UUID id PK
        UUID tenant_id FK
        VARCHAR uuid
        VARCHAR sensor_type
        JSONB capabilities
        VARCHAR status
        VARCHAR gateway_id
    }
    alert_rules {
        UUID id PK
        UUID tenant_id FK
        UUID sensor_id FK
        VARCHAR name
        JSONB conditions
        INTEGER hysteresis_count
        VARCHAR severity
    }
    alert_history {
        UUID id PK
        UUID tenant_id FK
        UUID alert_rule_id FK
        UUID sensor_id FK
        TIMESTAMPTZ triggered_at
        TEXT message
    }

    tenants ||--o{ tenant_settings : has
    tenants ||--o{ users : has
    tenants ||--o{ sensors : owns
    tenants ||--o{ alert_rules : defines
    tenants ||--o{ alert_history : records
    sensors ||--o{ alert_rules : targets
    alert_rules ||--o{ alert_history : generates
```

---

## 4. Tenant Isolation Strategy

- **Application layer**: `enforceTenantIsolation` middleware sets `req.tenantId` from the JWT. All DB queries include `WHERE tenant_id = $1`.
- **Database layer**: PostgreSQL Row Level Security (RLS) policies on all tenant-scoped tables read `app.current_tenant_id` session variable.
- **Superadmin bypass**: Superadmins may pass `tenantId` as a query parameter to operate across tenants.

---

## 5. Alert Rule Engine

Conditions are stored as JSONB trees supporting recursive `AND`/`OR`/`NOT` operators:

```json
{
  "operator": "AND",
  "conditions": [
    { "field": "temperature", "op": ">", "value": 30 },
    { "field": "humidity", "op": "<", "value": 20 }
  ]
}
```

Hysteresis prevents alert flapping – the condition must be true for N consecutive sensor readings before an alert is fired.
