# EchoSmart

**Plataforma IoT de agricultura de precisión para monitoreo ambiental inteligente en invernaderos.**

[![Documentación](https://img.shields.io/badge/docs-disponible-blue)](/docs/README.md)
[![Licencia](https://img.shields.io/badge/licencia-MIT-green)](#licencia)

---

## Descripción

EchoSmart es una solución empresarial de monitoreo ambiental que integra una arquitectura **edge-to-cloud** de tres capas: Gateway (Raspberry Pi), Backend Cloud (FastAPI) y Frontend (React). Diseñada para invernaderos de agricultura de precisión, la plataforma recopila datos de múltiples sensores, genera alertas en tiempo real y produce reportes automatizados, todo con soporte multi-tenant.

### Características Principales

- **Monitoreo en tiempo real** — Lectura continua de temperatura, humedad, luminosidad, humedad de suelo y CO₂ con actualización instantánea vía WebSocket.
- **Hot-plug de sensores** — Los dispositivos se auto-descubren y configuran al conectarse al gateway mediante SSDP.
- **Alertas configurables** — Reglas flexibles con evaluación local en el gateway y redundancia en la nube; notificaciones por email, SMS, push y webhooks.
- **Reportes automatizados** — Generación asincrónica de reportes PDF y Excel con gráficas embebidas.
- **Multi-tenancy** — Aislamiento completo de datos, branding personalizado y control de acceso basado en roles (RBAC).
- **Edge computing** — El gateway opera de forma autónoma con caché local, garantizando continuidad ante pérdida de conectividad.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Gateway (Edge)** | Raspberry Pi 4B · Python 3.9+ · SQLite · Mosquitto MQTT |
| **Backend (Cloud)** | FastAPI · PostgreSQL 14+ · InfluxDB 2.7+ · Redis 7+ · Docker |
| **Frontend (Web)** | React 18+ · Redux Toolkit · Recharts · Material-UI / Tailwind CSS |
| **Móvil** | React Native (Expo) · iOS y Android |

---

## Inicio Rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/Uaemextop/echosmart.git
cd echosmart

# 2. Levantar infraestructura
docker-compose up -d

# 3. Configurar y ejecutar el backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# 4. Configurar y ejecutar el frontend
cd ../frontend
npm install && npm run dev
```

Para instrucciones detalladas, consultar la guía de [Primeros Pasos](docs/getting-started.md).

---

## Sensores Soportados

| Sensor | Medición | Protocolo | Rango |
|--------|----------|-----------|-------|
| DS18B20 | Temperatura | 1-Wire | −55 °C a +125 °C (±0.5 °C) |
| DHT22 | Temperatura + Humedad | GPIO | −40 °C a +80 °C · 0-100 % HR |
| BH1750 | Luminosidad | I2C | 0–65 535 lux |
| Soil Moisture | Humedad de suelo | ADC (ADS1115) | Analógico 0–1023 |
| MHZ-19C | CO₂ | UART | 0–5000 ppm |

---

## Documentación

La documentación completa del proyecto se encuentra en el directorio [`docs/`](docs/README.md).

| Documento | Descripción |
|-----------|-------------|
| [Índice de Documentación](docs/README.md) | Punto de entrada y navegación de toda la documentación |
| [Primeros Pasos](docs/getting-started.md) | Instalación y configuración del entorno de desarrollo |
| [Funcionalidad de la Aplicación](docs/app-functionality.md) | Descripción detallada de todas las funciones del sistema |
| [Arquitectura de Software](docs/architecture.md) | Diseño de la arquitectura de 3 capas |
| [Roadmap Ejecutivo](docs/roadmap.md) | Fases de implementación, milestones y KPIs |
| [Integración Backend](docs/backend-integration.md) | Esquemas de base de datos, flujos E2E |
| [Funciones del Backend](docs/backend-functions.md) | Servicios y funciones del backend (FastAPI) |
| [API, Testing y DevOps](docs/api-testing-devops.md) | Especificación REST API, testing y CI/CD |
| [Frontend React](docs/frontend.md) | Componentes, Redux, hooks y testing |
| [Gateway y Edge Computing](docs/gateway-edge-computing.md) | Arquitectura del gateway, HAL y drivers |
| [Sensores y Hardware](docs/sensors-hardware.md) | Catálogo de sensores, conexión y calibración |
| [Despliegue](docs/deployment.md) | Docker, Kubernetes y producción |
| [Seguridad](docs/security.md) | Autenticación, autorización y protección de datos |

---

## Arquitectura

```
┌─────────────────┐     ┌─────────────────────────┐     ┌──────────────────┐
│   Sensores      │     │   Gateway (Edge)        │     │   Cloud Backend  │
│  DS18B20        │────▶│   Raspberry Pi 4B       │────▶│   FastAPI        │
│  DHT22          │     │   Python · SQLite       │     │   PostgreSQL     │
│  BH1750         │     │   MQTT · Alert Engine   │     │   InfluxDB       │
│  Soil Moisture  │     │                         │     │   Redis          │
│  MHZ-19C        │     └─────────────────────────┘     └────────┬─────────┘
└─────────────────┘                                              │
                                                        ┌────────▼─────────┐
                                                        │   Frontend       │
                                                        │   React · Redux  │
                                                        │   WebSocket      │
                                                        └──────────────────┘
```

---

## Licencia

Este proyecto está disponible bajo la licencia [MIT](LICENSE).
