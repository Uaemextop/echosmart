# EchoSmart – IoT Greenhouse Monitoring Platform

A multi-tenant, edge-to-cloud IoT platform for precision agriculture. Sensors auto-discover via SSDP, register through an edge gateway, and stream time-series data to a cloud backend with per-tenant isolation.

---

## Features

- 🌿 **Auto-discovery** – Sensors announce themselves via SSDP; the gateway registers them automatically
- 🏢 **Multi-tenancy** – Full PostgreSQL RLS isolation per tenant with RBAC (superadmin / tenant_admin / user)
- 📡 **MQTT messaging** – All sensor data flows through Mosquitto; backend listens and evaluates alert rules
- 🚨 **Smart alerts** – Recursive AND/OR/NOT conditions, hysteresis, time windows, email + WhatsApp notifications
- 📊 **React dashboard** – Live sensor monitoring, heatmaps, charts, tenant management wizard
- 🔐 **Secure auth** – JWT access + refresh tokens, httpOnly cookies, token rotation

---

## Architecture (text)

```
Browser (React :5173)
  └─► Backend (Node/Express :3000)
        ├─► PostgreSQL :5432  (tenants, users, sensors, alerts)
        ├─► Redis :6379        (rate-limiting, email queue)
        ├─► InfluxDB :8086     (time-series data)
        └─► MQTT :1883
              └─► Gateway (FastAPI :8000)
                    ├─► SQLite (local sensor registry)
                    └─► IoT Sensors (SSDP, HTTP)
```

---

## Quick Start

```bash
git clone <repo>
cd echosmart
cp .env.example .env   # edit secrets
docker-compose up -d
```

Open [http://localhost:5173](http://localhost:5173).

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://echosmart:echosmart@postgres:5432/echosmart` | PostgreSQL connection |
| `REDIS_URL` | `redis://redis:6379` | Redis connection |
| `INFLUXDB_URL` | `http://influxdb:8086` | InfluxDB connection |
| `MQTT_BROKER` | `mqtt://mosquitto:1883` | MQTT broker URL |
| `JWT_SECRET` | `changeme-in-production` | **Change in production** |
| `JWT_REFRESH_SECRET` | `changeme-refresh-in-production` | **Change in production** |
| `SENDGRID_API_KEY` | – | SendGrid API key for emails |
| `TWILIO_ACCOUNT_SID` | – | Twilio SID for WhatsApp fallback |
| `TWILIO_AUTH_TOKEN` | – | Twilio auth token |
| `GATEWAY_ID` | `gateway-001` | Unique gateway identifier |
| `CLOUD_BACKEND_URL` | `http://backend:3000` | Backend URL for gateway sync |

---

## Development Setup

### Backend

```bash
cd backend
npm install
DATABASE_URL=... REDIS_URL=... JWT_SECRET=dev npm run dev
```

### Gateway

```bash
cd gateway
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
CLOUD_BACKEND_URL=http://localhost:3000 GATEWAY_ID=local-001 uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## API Overview

See [`docs/api-spec.md`](docs/api-spec.md) for full API documentation.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | Authenticate user |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/tenants` | Create tenant (superadmin) |
| GET | `/api/sensors` | List sensors for tenant |
| GET | `/api/sensors/:id/data` | Get time-series readings |
| POST | `/api/alerts` | Create alert rule |
| POST | `/api/sensors/register` | Register sensor (gateway) |

---

## Documentation

- [`docs/architecture.md`](docs/architecture.md) – System architecture with Mermaid diagrams
- [`docs/mqtt-topics.md`](docs/mqtt-topics.md) – MQTT topic schemas
- [`docs/api-spec.md`](docs/api-spec.md) – REST API reference
