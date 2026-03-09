# EchoSmart — Variables de Entorno

Referencia completa de todas las variables de entorno utilizadas por cada componente de la plataforma.

---

## 1. Backend (FastAPI)

| Variable | Requerida | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `DATABASE_URL` | Sí | Cadena de conexión a PostgreSQL | `postgresql://user:pass@localhost:5432/echosmart` |
| `INFLUXDB_URL` | Sí | URL del servidor InfluxDB | `http://localhost:8086` |
| `INFLUXDB_TOKEN` | Sí | Token de autenticación de InfluxDB | `my-influxdb-token` |
| `INFLUXDB_ORG` | Sí | Nombre de la organización en InfluxDB | `echosmart` |
| `INFLUXDB_BUCKET` | Sí | Bucket para lecturas de sensores | `sensors` |
| `REDIS_URL` | Sí | Cadena de conexión a Redis | `redis://localhost:6379` |
| `JWT_SECRET_KEY` | Sí | Clave secreta para firmar JWT (mín. 256 bits) | `super-secret-key-change-me` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | Expiración del access token (default: 1440 = 24 h) | `1440` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | No | Expiración del refresh token (default: 30) | `30` |
| `CORS_ORIGINS` | No | Orígenes permitidos, separados por coma | `http://localhost:3000,https://app.echosmart.io` |
| `SENTRY_DSN` | No | DSN de Sentry para rastreo de errores | `https://xxx@sentry.io/yyy` |
| `LOG_LEVEL` | No | Nivel de logging (default: INFO) | `INFO` |
| `SMTP_HOST` | No | Servidor SMTP para envío de emails | `smtp.sendgrid.net` |
| `SMTP_PORT` | No | Puerto SMTP | `587` |
| `SMTP_USER` | No | Usuario SMTP | `apikey` |
| `SMTP_PASSWORD` | No | Contraseña SMTP | `SG.xxxxx` |
| `TWILIO_ACCOUNT_SID` | No | SID de cuenta Twilio (SMS) | `ACxxxxx` |
| `TWILIO_AUTH_TOKEN` | No | Token de autenticación Twilio | `token` |
| `TWILIO_PHONE_NUMBER` | No | Número de teléfono Twilio | `+1234567890` |
| `FIREBASE_CREDENTIALS` | No | Ruta al archivo de credenciales Firebase | `/app/firebase.json` |
| `S3_BUCKET_REPORTS` | No | Bucket S3 para reportes PDF/Excel | `echosmart-reports` |
| `AWS_ACCESS_KEY_ID` | No | Clave de acceso AWS (para S3) | `AKIAxxxxx` |
| `AWS_SECRET_ACCESS_KEY` | No | Clave secreta AWS | `xxxxx` |
| `AWS_REGION` | No | Región AWS | `us-east-1` |

---

## 2. Frontend (React)

| Variable | Requerida | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `VITE_API_URL` | Sí | URL base de la API backend | `http://localhost:8000` |
| `VITE_WS_URL` | Sí | URL del WebSocket | `ws://localhost:8000/ws` |
| `VITE_SENTRY_DSN` | No | DSN de Sentry para el frontend | `https://xxx@sentry.io/yyy` |
| `VITE_DEFAULT_LANGUAGE` | No | Idioma por defecto (default: `es`) | `es` |

> **Nota:** En Vite, las variables deben tener el prefijo `VITE_` para estar disponibles en el cliente.

---

## 3. Gateway (Raspberry Pi)

| Variable | Requerida | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `GATEWAY_ID` | Sí | Identificador único del gateway | `gw-invernadero-01` |
| `GATEWAY_NAME` | No | Nombre legible del gateway | `Invernadero Principal` |
| `CLOUD_API_URL` | Sí | URL del backend cloud | `https://api.echosmart.io` |
| `CLOUD_API_KEY` | Sí | API key para autenticar el gateway | `gw-api-key-xxxxx` |
| `MQTT_BROKER` | No | Host del broker MQTT (default: localhost) | `localhost` |
| `MQTT_PORT` | No | Puerto del broker MQTT (default: 1883) | `1883` |
| `MQTT_USERNAME` | No | Usuario MQTT (si auth habilitado) | `echosmart` |
| `MQTT_PASSWORD` | No | Contraseña MQTT | `mqtt-password` |
| `SENSOR_POLLING_INTERVAL` | No | Intervalo de lectura en segundos (default: 60) | `60` |
| `CLOUD_SYNC_INTERVAL` | No | Intervalo de sincronización en segundos (default: 300) | `300` |
| `SQLITE_PATH` | No | Ruta de la base de datos SQLite (default: `./data/readings.db`) | `./data/readings.db` |
| `LOG_LEVEL` | No | Nivel de logging (default: INFO) | `INFO` |
| `LOG_FILE` | No | Archivo de log (default: stdout) | `/var/log/echosmart/gateway.log` |

---

## 4. Docker Compose (Infraestructura)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `POSTGRES_DB` | Nombre de la base de datos | `echosmart` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `echosmart` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | `dev_password` |
| `DOCKER_INFLUXDB_INIT_USERNAME` | Usuario inicial de InfluxDB | `admin` |
| `DOCKER_INFLUXDB_INIT_PASSWORD` | Contraseña inicial de InfluxDB | `dev_password` |
| `DOCKER_INFLUXDB_INIT_ORG` | Organización inicial | `echosmart` |
| `DOCKER_INFLUXDB_INIT_BUCKET` | Bucket inicial | `sensors` |

---

## 5. Archivo `.env.example`

Plantilla para copiar como `.env`:

```bash
# ===== Backend =====
DATABASE_URL=postgresql://echosmart:dev_password@localhost:5432/echosmart
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=dev-token
INFLUXDB_ORG=echosmart
INFLUXDB_BUCKET=sensors
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=change-me-in-production
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=DEBUG

# ===== Gateway =====
GATEWAY_ID=gw-dev-01
CLOUD_API_URL=http://localhost:8000
CLOUD_API_KEY=dev-api-key
MQTT_BROKER=localhost
MQTT_PORT=1883
SENSOR_POLLING_INTERVAL=60
CLOUD_SYNC_INTERVAL=300

# ===== Frontend =====
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

---

*Volver al [Índice de Documentación](README.md)*
