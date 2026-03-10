# EchoSmart — Guía de Despliegue

Instrucciones para desplegar la plataforma EchoSmart en entornos de desarrollo, staging y producción.

---

## Arquitectura de Despliegue

```
                    ┌──────────────────────┐
                    │   CDN (CloudFront)   │
                    │   Frontend estático  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Load Balancer      │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │  Backend #1  │ │  Backend #2  │ │  Backend #N  │
      │  (FastAPI)   │ │  (FastAPI)   │ │  (FastAPI)   │
      └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                 │
     ┌───────▼────────────────▼─────────────────▼───────┐
     │              Capa de Datos                        │
     │  PostgreSQL  │  InfluxDB  │  Redis  │  RabbitMQ  │
     └──────────────────────────────────────────────────┘
```

---

## 1. Despliegue Local (Desarrollo)

### Docker Compose

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: echosmart
      POSTGRES_USER: echosmart
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  influxdb:
    image: influxdb:2.7
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: dev_password
      DOCKER_INFLUXDB_INIT_ORG: echosmart
      DOCKER_INFLUXDB_INIT_BUCKET: sensors
    ports:
      - "8086:8086"
    volumes:
      - influxdata:/var/lib/influxdb2

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  mosquitto:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
    volumes:
      - ./infra/mosquitto.conf:/mosquitto/config/mosquitto.conf

volumes:
  pgdata:
  influxdata:
```

```bash
docker-compose up -d
```

---

## 2. Despliegue en Producción

### 2.1 Backend (Docker)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```bash
docker build -t echosmart-backend:latest ./backend
docker run -d --name echosmart-api \
  --env-file .env.production \
  -p 8000:8000 \
  echosmart-backend:latest
```

### 2.2 Frontend (Build Estático)

```bash
cd frontend
npm run build
# Subir contenido de dist/ a CDN o servidor estático
```

### 2.3 Gateway (Raspberry Pi)

```bash
# En el Raspberry Pi
cd /opt/echosmart/gateway
source venv/bin/activate
pip install -r requirements.txt

# Configurar como servicio systemd
sudo cp echosmart-gateway.service /etc/systemd/system/
sudo systemctl enable echosmart-gateway
sudo systemctl start echosmart-gateway
```

---

## 3. Despliegue con Kubernetes

### Manifiesto de ejemplo

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echosmart-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: echosmart-backend
  template:
    metadata:
      labels:
        app: echosmart-backend
    spec:
      containers:
        - name: backend
          image: echosmart-backend:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: echosmart-secrets
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: echosmart-backend
spec:
  selector:
    app: echosmart-backend
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

```bash
kubectl apply -f k8s/
```

---

## 4. Pipeline CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: echosmart-backend:${{ github.sha }}
```

---

## 5. Monitoreo en Producción

| Herramienta | Propósito |
|-------------|-----------|
| Prometheus | Métricas de aplicación y sistema |
| Grafana | Dashboards de monitoreo |
| Sentry | Rastreo de errores |
| CloudTrail | Auditoría de acceso a la API |

### Métricas Clave

- Latencia p99 de la API < 200 ms
- Uptime del backend ≥ 99.9 %
- Tiempo de sincronización gateway → cloud < 5 min
- Tasa de errores < 0.1 %

---

## 6. Backups

| Componente | Estrategia | Frecuencia |
|------------|-----------|-----------|
| PostgreSQL | `pg_dump` automatizado | Diario |
| InfluxDB | Backup de buckets | Diario |
| Redis | Snapshot RDB | Cada 6 horas |
| Gateway SQLite | Copia a almacenamiento cloud | Diario |

---

*Volver al [Índice de Documentación](README.md)*
