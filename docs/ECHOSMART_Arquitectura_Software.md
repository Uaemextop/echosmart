# EchoSmart - Documentación de Arquitectura de Software

## 1. Visión General de la Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA ECHOSMART v1.0                         │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ☁️ CLOUD
                    ┌───────────────────────────────────┐
                    │     Backend Service Mesh          │
                    │  ┌─────────────────────────────┐  │
                    │  │   API Gateway (REST)        │  │
                    │  │   WebSocket Server          │  │
                    │  │   Authentication Service    │  │
                    │  └─────────────────────────────┘  │
                    │                                   │
                    │  ┌─────────────────────────────┐  │
                    │  │   Core Services             │  │
                    │  │  • Sensor Service           │  │
                    │  │  • Alert Service            │  │
                    │  │  • Report Service           │  │
                    │  │  • User Service             │  │
                    │  │  • Tenant Service           │  │
                    │  └─────────────────────────────┘  │
                    │                                   │
                    │  ┌─────────────────────────────┐  │
                    │  │   Data Layer                │  │
                    │  │  • PostgreSQL (Relational) │  │
                    │  │  • TimescaleDB (TimeSeries)│  │
                    │  │  • Redis (Cache)           │  │
                    │  └─────────────────────────────┘  │
                    │                                   │
                    │  ┌─────────────────────────────┐  │
                    │  │   Message Queue             │  │
                    │  │  • RabbitMQ / Bull          │  │
                    │  │  • Async Workers            │  │
                    │  └─────────────────────────────┘  │
                    └───────────────────────────────────┘
                              ▲        ▲        ▲
                    HTTPS + JWT + TLS   WSS
                              │        │        │
        ┌─────────────────────┼────────┼────────┼──────────────────┐
        │                     │        │        │                  │
        ▼                     ▼        ▼        ▼                  ▼
    📱 Mobile          💻 Web Portal   🔧 Gateway        📊 Admin Panel
   (React Native)    (React + Redux) (Raspberry Pi)      (React.js)
```

---

## 2. Patrón de Diseño: Microservicios Modular

```
BACKEND MICROSERVICES (Modular Architecture)
════════════════════════════════════════════

┌─────────────────────────┐
│   API Gateway           │
│  (Rate Limit, Auth)     │
└────────────┬────────────┘
             │
    ┌────────┴────────┬───────────┬──────────┐
    │                 │           │          │
    ▼                 ▼           ▼          ▼
┌────────────┐  ┌─────────┐  ┌────────┐  ┌────────┐
│   Users    │  │ Sensors │  │ Alerts │  │Reports │
│  Service   │  │ Service │  │Service │  │Service │
└────────────┘  └─────────┘  └────────┘  └────────┘
    │               │           │          │
    ├───────────────┼───────────┼──────────┤
    │               │           │          │
    ▼               ▼           ▼          ▼
┌─────────────────────────────────────────────┐
│    Shared Services Layer                    │
│  • Authentication (JWT)                    │
│  • Authorization (RBAC)                    │
│  • Tenant Isolation (Row-Level Security)   │
│  • Error Handling                          │
│  • Logging & Monitoring                    │
└─────────────────────────────────────────────┘
```

---

## 3. Flujo de Datos (Data Flow Diagrams)

### 3.1 Flujo de Lectura de Sensor (End-to-End)

```
┌──────────────────────────────────────────────────────────────────┐
│              SENSOR READING DATA FLOW (End-to-End)              │
└──────────────────────────────────────────────────────────────────┘

STEP 1: SENSOR HARDWARE LEVEL
───────────────────────────────
[Sensor]
  ↓ (Analog Signal / Digital Protocol)
  └─→ [GPIO Pin]
       ↓
STEP 2: EDGE DEVICE (Gateway)
─────────────────────────────
[Sensor Driver]
  ↓ (Parse Signal)
  └─→ [Data Validator]
       ↓ (Validation Rules: Range Check, Sanity Check)
       └─→ [SQLite Buffer]
            ├─→ [Local MQTT Broker] (Real-time)
            └─→ [Sync Queue] (For Cloud)
                ↓
STEP 3: NETWORK TRANSMISSION
────────────────────────────
[Cloud Uplink Worker]
  ├─→ Check Internet Connectivity
  ├─→ Batch Readings (max 1000)
  ├─→ Compress with Gzip
  └─→ POST /api/v1/readings/batch
       ↓
STEP 4: BACKEND INGESTION
─────────────────────────
[API Endpoint]
  ├─→ JWT Validation
  ├─→ Tenant Isolation Check
  ├─→ Data Validation (Pydantic Schema)
  └─→ [Message Queue] (RabbitMQ)
       ↓
STEP 5: ASYNC PROCESSING
─────────────────────────
[Worker Process]
  ├─→ Store in TimescaleDB (Time-Series)
  ├─→ Update Redis Cache (Last Reading)
  ├─→ Check Alert Conditions
  ├─→ Generate Notifications (if alert)
  └─→ Mark as Processed
       ↓
STEP 6: USER CONSUMPTION
────────────────────────
[Frontend WebSocket]
  ├─→ Subscribe to /sensors/{id}/updates
  ├─→ Real-time JSON: {"value": 25.3, "timestamp": 1678901234}
  ├─→ Render in Chart
  └─→ Display Latest Reading Card

TOTAL LATENCY: 
  • Local: <100ms (sensor to MQTT)
  • Cloud (online): 1-5s (end-to-end)
  • Cloud (offline): Buffered locally, synced when online
```

### 3.2 Flujo de Generación de Alerta

```
┌──────────────────────────────────────────────────────────────────┐
│              ALERT TRIGGER & NOTIFICATION FLOW                  │
└──────────────────────────────────────────────────────────────────┘

[New Reading Arrives]
    ↓
[Alert Engine Process]
    ├─→ Load Alert Rules from Cache
    ├─→ Get Historical Data (last 10 readings)
    ├─→ Evaluate Condition:
    │    ├─ Temperature > 30°C? (simple)
    │    ├─ Temperature > 30°C for > 5 minutes? (duration)
    │    ├─ Humidity AND Light < threshold? (AND condition)
    │    └─ Apply Hysteresis (prevent flapping)
    ├─→ State Machine:
    │    ├─ NORMAL → ALERT (if condition met)
    │    ├─ ALERT → ESCALATION (if persists > 15 min)
    │    └─ ESCALATION → CRITICAL (if > 30 min)
    └─→ Trigger Actions:
         ├─→ Store Alert in DB
         ├─→ Create Notification Records
         └─→ Queue Messages:
              ├─→ EMAIL (via SendGrid)
              ├─→ WHATSAPP (via Twilio)
              ├─→ PUSH NOTIFICATION (FCM)
              ├─→ WEBHOOK (Custom Integration)
              └─→ IN-APP (WebSocket Broadcast)

[Notification Workers]
    ├─→ Email Worker: Send templated HTML email
    ├─→ SMS Worker: Send via SMS provider
    ├─→ WhatsApp Worker: Send via Business API
    ├─→ Push Worker: Send via FCM
    └─→ Each retries on failure (exponential backoff)

[User Receives Notification]
    ├─→ Email: "⚠️ Temperature Alert: 32°C in Zona A"
    ├─→ WhatsApp: "🌡️ Alerta: Temperatura crítica (32°C) en Zona A"
    ├─→ Mobile Push: Notification badge
    └─→ Web: In-app notification + banner
```

---

## 4. Patrón de Autenticación y Autorización

### 4.1 JWT Token Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    JWT AUTHENTICATION FLOW                       │
└──────────────────────────────────────────────────────────────────┘

[User Login Request]
    ↓
[POST /api/v1/auth/login]
    ├─→ Validate email + password
    ├─→ Query DB: users table
    ├─→ Compare password hash (bcrypt)
    ├─→ Load user permissions from DB
    └─→ Generate JWT Token
         {
           "sub": "user-123",
           "email": "user@company.com",
           "tenant_id": "tenant-abc",
           "role": "admin",
           "permissions": ["read:sensors", "write:alerts"],
           "exp": 1678987634,
           "iat": 1678901234,
           "iss": "echosmart.com"
         }

[Response Headers]
    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
    Set-Cookie: refresh_token=eyJ0eXAi...; HttpOnly; Secure

[Subsequent Requests]
    ├─→ Client sends: Authorization: Bearer {JWT}
    ├─→ Middleware verifies:
    │    ├─ Signature (secret key)
    │    ├─ Not expired (exp > now)
    │    ├─ Not revoked (check blacklist in Redis)
    │    └─ Extract claims (sub, tenant_id, role)
    └─→ Attach user_id, tenant_id to request context

[Token Refresh]
    ├─→ POST /api/v1/auth/refresh
    ├─→ Validate refresh token (from HttpOnly cookie)
    ├─→ Generate new Access Token (24h)
    ├─→ Generate new Refresh Token (30d)
    └─→ Update cookies
```

### 4.2 RBAC (Role-Based Access Control)

```
ROLE HIERARCHY:
════════════════

SUPERADMIN
    ├─ Manage Tenants (create, delete, update)
    ├─ Create Superadmins
    ├─ Monitor platform health
    └─ Access all data

TENANT_ADMIN (per tenant)
    ├─ Manage Users within tenant
    ├─ Manage Gateways
    ├─ Configure Sensors
    ├─ Set Alert Rules
    └─ View Tenant Reports

USER (end customer)
    ├─ View assigned Sensors
    ├─ Acknowledge Alerts
    ├─ Download Reports
    └─ Update Profile

VIEWER (read-only)
    ├─ View Dashboards
    └─ Read-only Reports


PERMISSION MATRIX:
════════════════

Resource: sensors
  SUPERADMIN: [CREATE, READ, UPDATE, DELETE, ADMIN]
  TENANT_ADMIN: [CREATE, READ, UPDATE, DELETE]
  USER: [READ]
  VIEWER: [READ]

Resource: alerts
  SUPERADMIN: [CREATE, READ, UPDATE, DELETE, ADMIN]
  TENANT_ADMIN: [CREATE, READ, UPDATE, DELETE]
  USER: [READ, ACKNOWLEDGE]
  VIEWER: [READ]

Resource: reports
  SUPERADMIN: [CREATE, READ, DELETE]
  TENANT_ADMIN: [CREATE, READ]
  USER: [READ]
  VIEWER: [READ]
```

---

## 5. Multi-Tenancy Architecture (Row-Level Security)

```
┌──────────────────────────────────────────────────────────────────┐
│              MULTI-TENANT DATA ISOLATION MODEL                  │
└──────────────────────────────────────────────────────────────────┘

DATABASE SCHEMA:
════════════════

tenants (Tenant Isolation)
  ├─ tenant_id (PK)
  ├─ company_name
  ├─ api_key
  └─ storage_quota_gb

users (Belongs to Tenant)
  ├─ user_id (PK)
  ├─ tenant_id (FK) ← KEY COLUMN
  ├─ email
  ├─ password_hash
  └─ role

sensors (Belongs to Tenant)
  ├─ sensor_id (PK)
  ├─ tenant_id (FK) ← KEY COLUMN
  ├─ gateway_id
  ├─ sensor_type
  └─ location

readings (Belongs to Tenant)
  ├─ reading_id (PK)
  ├─ tenant_id (FK) ← KEY COLUMN
  ├─ sensor_id (FK)
  ├─ value
  └─ timestamp

alerts (Belongs to Tenant)
  ├─ alert_id (PK)
  ├─ tenant_id (FK) ← KEY COLUMN
  ├─ sensor_id (FK)
  ├─ alert_condition
  └─ triggered_at


ROW-LEVEL SECURITY (RLS) POLICY:
═════════════════════════════════

Middleware Enforcement:
  ├─ Extract tenant_id from JWT
  ├─ Prepend WHERE clause: WHERE tenant_id = {extracted_tenant_id}
  ├─ Apply to every query automatically
  └─ No exceptions (even queries in migrations)

Example Query Transformation:
  Original:  SELECT * FROM sensors WHERE sensor_id = 123
  Enforced:  SELECT * FROM sensors 
             WHERE sensor_id = 123 AND tenant_id = 'tenant-abc'


ISOLATION GUARANTEE:
════════════════════

✓ User A cannot see User B's data (same platform)
✓ Tenant A cannot see Tenant B's data (different companies)
✓ Bulk operations respect RLS (UPDATE/DELETE)
✓ Cache keys include tenant_id: echosmart:{tenant_id}:{resource}
✓ MQTT topics segregated: sensors/{tenant_id}/{sensor_uuid}/data
```

---

## 6. Estructura de Directorios Física

### 6.1 Backend Directory Tree

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Entry point (FastAPI app)
│   │
│   ├── core/
│   │   ├── config.py                # Configuration (env vars)
│   │   ├── security.py              # JWT, password hashing
│   │   └── exceptions.py            # Custom exceptions
│   │
│   ├── api/
│   │   ├── v1/                      # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py          # POST /login, /refresh
│   │   │   │   ├── sensors.py       # CRUD /sensors
│   │   │   │   ├── readings.py      # POST /readings/batch
│   │   │   │   ├── alerts.py        # GET/POST /alerts
│   │   │   │   ├── reports.py       # POST /reports/generate
│   │   │   │   ├── users.py         # CRUD /users
│   │   │   │   ├── tenants.py       # CRUD /tenants (admin)
│   │   │   │   └── gateway.py       # GET /gateway/status
│   │   │   ├── dependencies.py      # Dependency injection
│   │   │   └── router.py            # Route aggregation
│   │   │
│   │   └── middleware/
│   │       ├── auth.py              # JWT validation
│   │       ├── tenant_isolation.py  # RLS enforcement
│   │       ├── error_handler.py     # Global error handling
│   │       └── logging.py           # Request logging
│   │
│   ├── db/
│   │   ├── base.py                  # Database session factory
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── migrations/              # Alembic migrations
│   │   │   ├── versions/
│   │   │   │   ├── 001_initial.py
│   │   │   │   └── 002_add_alerts.py
│   │   │   └── env.py
│   │   └── queries.py               # Raw SQL queries (complex)
│   │
│   ├── schemas/
│   │   ├── auth.py                  # Pydantic: LoginRequest, TokenResponse
│   │   ├── sensor.py                # Pydantic: SensorCreate, SensorUpdate
│   │   ├── reading.py               # Pydantic: ReadingCreate, ReadingList
│   │   ├── alert.py                 # Pydantic: AlertCreate, AlertTrigger
│   │   ├── user.py                  # Pydantic: UserCreate, UserUpdate
│   │   └── base.py                  # Base schema with timestamps
│   │
│   ├── services/
│   │   ├── sensor_service.py        # Business logic: CRUD + validation
│   │   ├── reading_service.py       # Reading aggregation, statistics
│   │   ├── alert_service.py         # Alert evaluation engine
│   │   ├── report_service.py        # PDF/Excel generation
│   │   ├── user_service.py          # User management
│   │   ├── auth_service.py          # Authentication logic
│   │   ├── email_service.py         # Email sending (SMTP)
│   │   ├── whatsapp_service.py      # WhatsApp integration
│   │   └── cache_service.py         # Redis operations
│   │
│   ├── workers/
│   │   ├── base_worker.py           # Base worker class
│   │   ├── sync_worker.py           # Cloud sync from edges
│   │   ├── report_worker.py         # Async report generation
│   │   ├── alert_worker.py          # Alert evaluation
│   │   ├── notification_worker.py   # Email/SMS/Push sending
│   │   └── cleanup_worker.py        # Data retention cleanup
│   │
│   ├── mqtt/
│   │   ├── client.py                # MQTT client connection
│   │   ├── topics.py                # Topic definitions
│   │   ├── handlers.py              # Message handlers
│   │   └── payloads.py              # Payload schemas
│   │
│   └── utils/
│       ├── validators.py            # Custom Pydantic validators
│       ├── formatters.py            # Data formatting
│       ├── decorators.py            # Custom decorators (@retry, @async)
│       └── constants.py             # App-wide constants
│
├── tests/
│   ├── conftest.py                  # Pytest fixtures
│   ├── unit/
│   │   ├── services/
│   │   │   ├── test_sensor_service.py
│   │   │   └── test_alert_service.py
│   │   ├── utils/
│   │   │   └── test_validators.py
│   │   └── __init__.py
│   ├── integration/
│   │   ├── test_api_endpoints.py
│   │   ├── test_auth_flow.py
│   │   └── test_multi_tenancy.py
│   └── e2e/
│       ├── test_sensor_to_dashboard.py
│       └── test_alert_flow.py
│
├── migrations/
│   └── env.py
│
├── requirements.txt                 # Python dependencies
├── requirements-dev.txt             # Development only
├── Dockerfile                       # Containerization
├── docker-compose.yml               # Local dev environment
├── pytest.ini                       # Pytest config
├── .env.example                     # Environment template
└── README.md                        # Backend README
```

---

## 7. Modelos de Base de Datos (Entity-Relationship)

### 7.1 Schema PostgreSQL

```sql
-- MULTI-TENANCY CORE
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    email_domain VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'basic', -- basic, professional, enterprise
    max_sensors INT DEFAULT 50,
    max_users INT DEFAULT 10,
    storage_quota_gb INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- USERS & AUTHENTICATION
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user', -- superadmin, tenant_admin, user, viewer
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tenant_id, email)
);

-- GATEWAYS (Edge Devices)
CREATE TABLE gateways (
    gateway_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    api_key VARCHAR(255) UNIQUE,
    firmware_version VARCHAR(50),
    is_online BOOLEAN DEFAULT FALSE,
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SENSORS
CREATE TABLE sensors (
    sensor_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    gateway_id UUID NOT NULL REFERENCES gateways(gateway_id),
    sensor_uuid VARCHAR(255) NOT NULL, -- Hardware UUID
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- temperature, humidity, light, co2, moisture
    location VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    calibration_offset FLOAT DEFAULT 0,
    last_reading FLOAT,
    last_reading_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tenant_id, sensor_uuid)
);

-- ALERTS CONFIGURATION
CREATE TABLE alert_configs (
    alert_config_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    sensor_id UUID NOT NULL REFERENCES sensors(sensor_id),
    name VARCHAR(255) NOT NULL,
    condition VARCHAR(50), -- gt, lt, eq, between
    threshold_value FLOAT,
    threshold_duration_minutes INT DEFAULT 5,
    hysteresis FLOAT DEFAULT 1.0,
    enabled BOOLEAN DEFAULT TRUE,
    notification_channels TEXT[], -- ['email', 'whatsapp', 'push']
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ALERT TRIGGERS (Log of triggered alerts)
CREATE TABLE alert_triggers (
    alert_trigger_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    alert_config_id UUID NOT NULL REFERENCES alert_configs(alert_config_id),
    sensor_id UUID NOT NULL REFERENCES sensors(sensor_id),
    triggered_value FLOAT NOT NULL,
    severity VARCHAR(50), -- low, medium, high, critical
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by UUID REFERENCES users(user_id),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_sensors_tenant_id ON sensors(tenant_id);
CREATE INDEX idx_sensors_gateway_id ON sensors(gateway_id);
CREATE INDEX idx_alert_triggers_tenant_id ON alert_triggers(tenant_id);
CREATE INDEX idx_alert_triggers_triggered_at ON alert_triggers(triggered_at DESC);
```

### 7.2 Schema TimescaleDB (Time-Series)

```sql
-- TIME-SERIES HYPERTABLE
CREATE TABLE sensor_readings (
    time TIMESTAMP NOT NULL,
    sensor_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50) NOT NULL,
    gateway_id UUID
);

-- Convert to hypertable
SELECT create_hypertable(
    'sensor_readings',
    'time',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- Compression policy (datos > 7 dias)
ALTER TABLE sensor_readings
    SET (timescaledb.compress, timescaledb.compress_orderby = 'time DESC');

SELECT add_compression_policy(
    'sensor_readings',
    INTERVAL '7 days'
);

-- Retention policy (30 dias)
SELECT add_retention_policy('sensor_readings', INTERVAL '30 days');

-- CONTINUOUS AGGREGATE (1-hour aggregation)
CREATE MATERIALIZED VIEW sensor_readings_1h_agg
WITH (timescaledb.continuous) AS
  SELECT
    time_bucket('1 hour', time) as hour,
    sensor_id,
    tenant_id,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    STDDEV(value) as stddev_value,
    COUNT(*) as count
  FROM sensor_readings
  GROUP BY hour, sensor_id, tenant_id;

-- Auto-refresh policy
SELECT add_continuous_aggregate_policy(
    'sensor_readings_1h_agg',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '10 minutes',
    schedule_interval => INTERVAL '10 minutes'
);

-- INDEXES
CREATE INDEX idx_sensor_readings_sensor_id ON sensor_readings(sensor_id, time DESC);
CREATE INDEX idx_sensor_readings_tenant_id ON sensor_readings(tenant_id, time DESC);
```

