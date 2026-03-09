# EchoSmart REST API Specification

Base URL: `http://localhost:3000/api`

Authentication: JWT via `accessToken` httpOnly cookie or `Authorization: Bearer <token>` header.

---

## Auth Endpoints

### POST /api/auth/login

```bash
curl -c cookies.txt -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"secret123"}'
```

**Response 200**
```json
{
  "user": {
    "id": "uuid",
    "email": "admin@example.com",
    "role": "superadmin",
    "tenantId": null
  }
}
```

---

### POST /api/auth/logout

```bash
curl -b cookies.txt -X POST http://localhost:3000/api/auth/logout
```

**Response 200** `{ "message": "Logged out" }`

---

### POST /api/auth/refresh

Rotates the refresh token and issues a new access token.

```bash
curl -b cookies.txt -X POST http://localhost:3000/api/auth/refresh
```

---

### POST /api/auth/forgot-password

```bash
curl -X POST http://localhost:3000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"user@tenant.com"}'
```

---

### POST /api/auth/reset-password

```bash
curl -X POST http://localhost:3000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token":"<jwt>","password":"newpassword123"}'
```

---

### GET /api/auth/me

```bash
curl -b cookies.txt http://localhost:3000/api/auth/me
```

---

## Tenant Endpoints (Superadmin only)

### POST /api/tenants

```bash
curl -b cookies.txt -X POST http://localhost:3000/api/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "farm-north",
    "email": "admin@farmnorth.com",
    "password": "secure1234",
    "plan": "pro",
    "company_name": "Farm North Ltd",
    "max_sensors": 50,
    "max_users": 25
  }'
```

**Response 201**
```json
{
  "tenant": { "id": "uuid", "name": "farm-north", "plan": "pro", "status": "active" },
  "user": { "id": "uuid", "email": "admin@farmnorth.com", "role": "tenant_admin" }
}
```

---

### GET /api/tenants

Query params: `page`, `limit`, `search`, `plan`, `status`

```bash
curl -b cookies.txt "http://localhost:3000/api/tenants?page=1&plan=pro"
```

---

### GET /api/tenants/:id/health

```bash
curl -b cookies.txt http://localhost:3000/api/tenants/uuid/health
```

**Response 200**
```json
{ "tenant_id": "uuid", "sensors": 12, "users": 3, "active_alerts": 1 }
```

---

## Sensor Endpoints

### POST /api/sensors/register (Gateway → Backend)

```bash
curl -X POST http://localhost:3000/api/sensors/register \
  -H "Content-Type: application/json" \
  -d '{
    "uuid": "sensor-abc-123",
    "sensor_type": "climate",
    "capabilities": ["temperature","humidity","co2"],
    "gateway_id": "gateway-001",
    "ip_address": "192.168.1.50",
    "port": 8080
  }'
```

**Response 200**
```json
{
  "sensor_id": "uuid",
  "tenant_id": "uuid-or-null",
  "mqtt_topic_data": "/sensors/sensor-abc-123/data",
  "mqtt_topic_config": "/sensors/sensor-abc-123/config"
}
```

---

### GET /api/sensors

```bash
curl -b cookies.txt http://localhost:3000/api/sensors
```

---

### GET /api/sensors/:id/data

Query params: `start` (default `-24h`), `end` (default `now`), `field` (default `temperature`)

```bash
curl -b cookies.txt "http://localhost:3000/api/sensors/uuid/data?field=humidity&start=-6h"
```

---

## Alert Rule Endpoints

### POST /api/alerts

```bash
curl -b cookies.txt -X POST http://localhost:3000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Temperature",
    "sensor_id": "sensor-uuid",
    "conditions": {
      "operator": "AND",
      "conditions": [
        { "field": "temperature", "op": ">", "value": 30 }
      ]
    },
    "hysteresis_count": 3,
    "severity": "warning",
    "is_active": true,
    "notification_channels": []
  }'
```

---

### GET /api/alerts

```bash
curl -b cookies.txt http://localhost:3000/api/alerts
```

---

### PUT /api/alerts/:id

```bash
curl -b cookies.txt -X PUT http://localhost:3000/api/alerts/uuid \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

---

### DELETE /api/alerts/:id

Soft-deletes (sets `is_active = false`).

```bash
curl -b cookies.txt -X DELETE http://localhost:3000/api/alerts/uuid
```

---

## Error Responses

All error responses follow the shape:

```json
{ "error": "Human-readable message" }
```

| Status | Meaning |
|--------|---------|
| 400 | Validation error |
| 401 | Not authenticated / token expired |
| 403 | Insufficient role |
| 404 | Resource not found |
| 409 | Conflict (duplicate) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
