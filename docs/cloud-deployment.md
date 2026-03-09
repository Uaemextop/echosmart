# EchoSmart — Despliegue en la Nube

Guía detallada para desplegar el backend y el frontend de EchoSmart en proveedores cloud reales (AWS, DigitalOcean).

---

## 1. Arquitectura de Producción

```
                         Internet
                            │
                    ┌───────▼────────┐
                    │ CloudFront CDN │  ← Frontend estático (React)
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │  ALB / Nginx   │  ← Balanceador de carga
                    │  HTTPS (443)   │
                    └───────┬────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                 ▼
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │  Backend #1  │ │  Backend #2  │ │  Backend #N  │
   │  FastAPI     │ │  FastAPI     │ │  FastAPI     │
   │  Docker      │ │  Docker      │ │  Docker      │
   └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
          │                │                 │
  ┌───────▼─────────────────▼─────────────────▼───────┐
  │                    VPC Privada                      │
  │                                                     │
  │  ┌─────────────┐  ┌──────────┐  ┌───────────────┐ │
  │  │ PostgreSQL   │  │ InfluxDB │  │ Redis         │ │
  │  │ RDS/Managed  │  │ Cloud    │  │ ElastiCache   │ │
  │  └─────────────┘  └──────────┘  └───────────────┘ │
  └─────────────────────────────────────────────────────┘
```

---

## 2. Opción A: Despliegue en AWS

### 2.1 Servicios Utilizados

| Servicio AWS | Propósito | Tier Estimado |
|-------------|-----------|---------------|
| EC2 | Backend FastAPI (Docker) | t3.medium ($30/mes) |
| RDS PostgreSQL | Base de datos relacional | db.t3.small ($25/mes) |
| InfluxDB Cloud | Time-series (SaaS externo) | Free tier / $49/mes |
| ElastiCache Redis | Caché y sesiones | cache.t3.micro ($12/mes) |
| S3 | Almacenamiento de reportes PDF | ~$1/mes |
| CloudFront | CDN para frontend | ~$5/mes |
| Route 53 | DNS | $0.50/zona |
| ACM | Certificados TLS | Gratis |
| **Total estimado** | | **~$75–125/mes** |

### 2.2 Paso a Paso: EC2 + Docker

#### Crear la Instancia EC2

```bash
# Usar Amazon Linux 2023 o Ubuntu 22.04 LTS
# Tipo: t3.medium (2 vCPU, 4 GB RAM)
# Storage: 30 GB gp3
# Security Group: Abrir puertos 22 (SSH), 80, 443, 8000
```

#### Instalar Docker en EC2

```bash
# Amazon Linux 2023
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Clonar y Configurar

```bash
cd /opt
sudo git clone https://github.com/Uaemextop/echosmart.git
cd echosmart

# Crear archivo de producción
sudo cp .env.example .env.production
sudo nano .env.production
```

#### Variables de Entorno para Producción

```bash
# .env.production
NODE_ENV=production
DATABASE_URL=postgresql://echosmart:PASSWORD@rds-endpoint:5432/echosmart
INFLUXDB_URL=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=echosmart
INFLUXDB_BUCKET=sensors
REDIS_URL=redis://elasticache-endpoint:6379
JWT_SECRET_KEY=your-256-bit-random-secret
CORS_ORIGINS=https://app.echosmart.io
SENTRY_DSN=https://your-sentry-dsn
```

#### Desplegar con Docker Compose

```yaml
# docker-compose.production.yml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file: .env.production
    ports:
      - "8000:8000"
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infra/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
    restart: always
```

```bash
sudo docker-compose -f docker-compose.production.yml up -d
```

### 2.3 Configurar RDS PostgreSQL

1. Crear instancia RDS PostgreSQL 14 (db.t3.small).
2. Habilitar Multi-AZ para alta disponibilidad (producción).
3. Configurar Security Group para permitir acceso solo desde EC2.
4. Ejecutar migraciones desde EC2:

```bash
docker exec -it echosmart-backend alembic upgrade head
```

### 2.4 Configurar HTTPS con Let's Encrypt

```bash
# Instalar certbot en EC2
sudo yum install -y certbot
sudo certbot certonly --standalone -d api.echosmart.io

# Renovación automática
sudo crontab -e
# Agregar: 0 0 1 * * certbot renew --quiet
```

### 2.5 Desplegar Frontend en S3 + CloudFront

```bash
cd frontend
npm run build

# Subir a S3
aws s3 sync dist/ s3://echosmart-frontend --delete

# Invalidar caché de CloudFront
aws cloudfront create-invalidation \
  --distribution-id EXXXXXXX \
  --paths "/*"
```

---

## 3. Opción B: Despliegue en DigitalOcean

### 3.1 Servicios Utilizados

| Servicio DO | Propósito | Costo |
|------------|-----------|-------|
| Droplet | Backend (Docker) | $24/mes (4 GB RAM) |
| Managed PostgreSQL | Base de datos | $15/mes |
| Spaces | Almacenamiento de reportes | $5/mes |
| App Platform | Frontend estático | Gratis (sitios estáticos) |
| **Total estimado** | | **~$45–65/mes** |

### 3.2 Paso a Paso

#### Crear Droplet

```bash
# Ubuntu 22.04 LTS
# Plan: Basic, 4 GB RAM, 2 vCPUs
# Región: Más cercana a los gateways
# Autenticación: SSH key
```

#### Configurar el Servidor

```bash
# Conectar por SSH
ssh root@your-droplet-ip

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin

# Configurar firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Clonar y desplegar
cd /opt
git clone https://github.com/Uaemextop/echosmart.git
cd echosmart
cp .env.example .env.production
nano .env.production
docker compose -f docker-compose.production.yml up -d
```

---

## 4. Despliegue del Gateway en Raspberry Pi

### 4.1 Prerrequisitos

- Raspberry Pi configurada según [Configuración de Raspberry Pi OS](raspberry-pi-setup.md).
- Conexión a Internet estable (Ethernet recomendado).
- Backend cloud desplegado y accesible.

### 4.2 Instalar el Software del Gateway

```bash
# Crear directorio de instalación
sudo mkdir -p /opt/echosmart
sudo chown $USER:$USER /opt/echosmart
cd /opt/echosmart

# Clonar el repositorio
git clone https://github.com/Uaemextop/echosmart.git
cd echosmart/gateway

# Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 Configurar Variables de Entorno

```bash
cp .env.example .env
nano .env
```

```bash
# .env del gateway
GATEWAY_ID=gw-invernadero-01
GATEWAY_NAME=Invernadero Principal
CLOUD_API_URL=https://api.echosmart.io
CLOUD_API_KEY=your-gateway-api-key
MQTT_BROKER=localhost
MQTT_PORT=1883
SENSOR_POLLING_INTERVAL=60
CLOUD_SYNC_INTERVAL=300
LOG_LEVEL=INFO
```

### 4.4 Registrar el Gateway en el Backend

```bash
# Desde cualquier máquina con acceso a la API
curl -X POST https://api.echosmart.io/api/v1/gateways \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "gw-invernadero-01",
    "name": "Invernadero Principal",
    "location": "Zona A",
    "description": "Gateway principal del invernadero A"
  }'
```

### 4.5 Configurar Sensores

Editar `sensors.json`:

```json
{
  "sensors": [
    {
      "id": "temp-interior",
      "type": "DS18B20",
      "device_id": "28-0516a42651ff",
      "name": "Temperatura Interior",
      "location": "Centro del invernadero",
      "unit": "°C",
      "polling_interval": 60,
      "enabled": true
    },
    {
      "id": "hum-interior",
      "type": "DHT22",
      "gpio_pin": 17,
      "name": "Humedad Interior",
      "location": "Centro del invernadero",
      "unit": "%",
      "polling_interval": 60,
      "enabled": true
    },
    {
      "id": "luz-interior",
      "type": "BH1750",
      "i2c_address": "0x23",
      "name": "Luminosidad Interior",
      "location": "Techo del invernadero",
      "unit": "lux",
      "polling_interval": 120,
      "enabled": true
    },
    {
      "id": "suelo-zona-a",
      "type": "SOIL_MOISTURE",
      "adc_channel": 0,
      "name": "Humedad Suelo Zona A",
      "location": "Zona de cultivo A",
      "unit": "%",
      "polling_interval": 300,
      "enabled": true
    },
    {
      "id": "co2-interior",
      "type": "MHZ19C",
      "serial_port": "/dev/serial0",
      "name": "CO2 Interior",
      "location": "Centro del invernadero",
      "unit": "ppm",
      "polling_interval": 120,
      "enabled": true
    }
  ]
}
```

### 4.6 Configurar como Servicio del Sistema

```bash
# Copiar el archivo de servicio
sudo cp echosmart-gateway.service /etc/systemd/system/

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable echosmart-gateway
sudo systemctl start echosmart-gateway

# Verificar
sudo systemctl status echosmart-gateway
journalctl -u echosmart-gateway -f
```

### 4.7 Verificar Conectividad con la Nube

```bash
# Verificar que el gateway puede alcanzar el backend
curl -s https://api.echosmart.io/health
# Debe responder: {"status": "ok"}

# Verificar logs de sincronización
journalctl -u echosmart-gateway | grep "sync"
```

---

## 5. Configurar Dominio y DNS

### Estructura de Dominios Recomendada

| Subdominio | Servicio | Destino |
|-----------|---------|---------|
| `app.echosmart.io` | Frontend web | CloudFront / Vercel |
| `api.echosmart.io` | Backend API | EC2 / Droplet |
| `mqtt.echosmart.io` | Broker MQTT cloud (opcional) | EC2 / Droplet |

### Configuración DNS (Route 53 / Cloudflare)

```
app.echosmart.io    A     → IP del CDN o servidor frontend
api.echosmart.io    A     → IP del servidor backend
```

---

## 6. Monitoreo en Producción

### Configurar Sentry (Error Tracking)

```bash
# En .env.production
SENTRY_DSN=https://xxxx@sentry.io/yyyy
```

### Configurar Prometheus + Grafana

```yaml
# Agregar a docker-compose.production.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana-data:/var/lib/grafana
```

### Dashboards Recomendados en Grafana

- **API Performance**: Latencia p50/p95/p99, requests/segundo, errores.
- **Gateway Status**: Número de gateways conectados, última sincronización.
- **Sensor Health**: Sensores activos, tasa de lecturas fallidas.
- **Database**: Conexiones activas, queries lentos, tamaño de almacenamiento.

---

## 7. Backups Automatizados

### PostgreSQL

```bash
#!/bin/bash
# /opt/echosmart/scripts/backup-postgres.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/echosmart/backups/postgres

mkdir -p $BACKUP_DIR
pg_dump -h $DB_HOST -U echosmart -d echosmart | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Subir a S3/Spaces
aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.sql.gz s3://echosmart-backups/postgres/

# Eliminar backups locales de más de 7 días
find $BACKUP_DIR -mtime +7 -delete
```

Agregar al crontab:

```bash
0 2 * * * /opt/echosmart/scripts/backup-postgres.sh
```

---

## 8. Checklist de Despliegue

### Backend Cloud
- [ ] Servidor provisionado (EC2/Droplet)
- [ ] Docker y Docker Compose instalados
- [ ] PostgreSQL configurado y accesible
- [ ] InfluxDB configurado con bucket y token
- [ ] Redis configurado
- [ ] Variables de entorno de producción configuradas
- [ ] Backend desplegado y respondiendo en `/health`
- [ ] HTTPS habilitado con certificado válido
- [ ] Migraciones de base de datos ejecutadas
- [ ] Sentry configurado para error tracking

### Frontend
- [ ] Build de producción generado (`npm run build`)
- [ ] Archivos estáticos desplegados en CDN/S3
- [ ] Dominio configurado y apuntando al CDN
- [ ] HTTPS activo

### Gateway (Raspberry Pi)
- [ ] Raspberry Pi OS instalado y actualizado
- [ ] Interfaces de hardware habilitadas (I2C, 1-Wire, UART)
- [ ] Mosquitto instalado y activo
- [ ] Software del gateway instalado
- [ ] Sensores configurados en `sensors.json`
- [ ] Gateway registrado en el backend
- [ ] Servicio systemd activo y habilitado
- [ ] Conectividad con el backend verificada
- [ ] Lecturas de sensores visibles en el dashboard

---

*Volver al [Índice de Documentación](README.md)*
