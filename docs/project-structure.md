# EchoSmart — Estructura del Proyecto

Descripción detallada de la organización de carpetas, módulos y dependencias del monorepo EchoSmart.

---

## Estructura General del Monorepo

```
echosmart/
│
├── README.md                          # Descripción del proyecto y enlaces a docs
├── LICENSE                            # Software propietario
├── CHANGELOG.md                       # Registro de cambios por versión
├── Makefile                           # Build, test, lint, deb, docker
├── docker-compose.yml                 # Orquestación de servicios para desarrollo
├── .gitignore                         # Archivos ignorados por Git
├── .env.example                       # Plantilla de variables de entorno
│
├── .github/                           # Configuración de GitHub
│   ├── workflows/                     # Pipelines CI/CD
│   │   ├── ci.yml                     # Tests y linting en cada push/PR
│   │   ├── deploy.yml                 # Build y despliegue a producción
│   │   ├── build-deb.yml              # Build .deb package para EchoPy
│   │   ├── mobile.yml                 # Build app mobile (EAS)
│   │   ├── iso.yml                    # Build ISO EchoPy + Servidor
│   │   └── demo.yml                   # Deploy demo a GitHub Pages
│   ├── dependabot.yml                 # Actualización automática de dependencias
│   ├── ISSUE_TEMPLATE/                # Plantillas de issues
│   │   ├── bug_report.md              # Reporte de bug
│   │   └── feature_request.md         # Solicitud de funcionalidad
│   ├── PULL_REQUEST_TEMPLATE.md       # Plantilla de Pull Request
│   └── CODEOWNERS                     # Asignación de revisores por área
│
├── docs/                              # Documentación técnica completa
│   ├── README.md                      # Índice de documentación
│   ├── getting-started.md             # Guía de inicio rápido
│   ├── app-functionality.md           # Funcionalidad de la aplicación
│   ├── project-structure.md           # Este archivo
│   ├── architecture.md                # Arquitectura de software
│   ├── communication-protocols.md     # Protocolos de comunicación
│   ├── roadmap.md                     # Roadmap ejecutivo
│   ├── backend-integration.md         # Integración backend
│   ├── backend-functions.md           # Funciones del backend
│   ├── api-testing-devops.md          # API, testing y DevOps
│   ├── frontend.md                    # Frontend React
│   ├── raspberry-pi-setup.md          # Configuración de Raspberry Pi OS
│   ├── gateway-edge-computing.md      # Gateway y edge computing
│   ├── sensors-hardware.md            # Sensores y hardware
│   ├── database-schema.md             # Esquema de base de datos
│   ├── environment-variables.md       # Variables de entorno
│   ├── cloud-deployment.md            # Despliegue en la nube
│   ├── deployment.md                  # Guía general de despliegue
│   ├── security.md                    # Seguridad
│   ├── troubleshooting.md             # Resolución de problemas
│   ├── features-roadmap.md            # Funcionalidades futuras
│   └── contributing.md                # Contribución al proyecto
│
├── backend/                           # API y servicios cloud
│   ├── main.py                        # Punto de entrada FastAPI
│   ├── requirements.txt               # Dependencias Python
│   ├── Dockerfile                     # Imagen Docker del backend
│   ├── alembic.ini                    # Configuración de migraciones
│   ├── .env.example                   # Variables de entorno del backend
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuración (env vars, constantes)
│   │   ├── database.py                # Conexión a PostgreSQL e InfluxDB
│   │   ├── dependencies.py            # Inyección de dependencias FastAPI
│   │   ├── routers/                   # Endpoints REST agrupados por recurso
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # /api/v1/auth/* (login, register con serial, admin login)
│   │   │   ├── serials.py             # /api/v1/serials/* (generar, validar, revocar)
│   │   │   ├── echopy.py              # /api/v1/echopy/* (bind, suspend, remote, diagnostics)
│   │   │   ├── updates.py             # /api/v1/updates/* (Cosmuodate: check, download, apply)
│   │   │   ├── gateways.py            # /api/v1/gateways/* (compatibilidad)
│   │   │   ├── sensors.py             # /api/v1/sensors/*
│   │   │   ├── alerts.py              # /api/v1/alerts/*
│   │   │   ├── reports.py             # /api/v1/reports/*
│   │   │   ├── users.py               # /api/v1/users/*
│   │   │   └── tenants.py             # /api/v1/tenants/*
│   │   ├── services/                  # Lógica de negocio
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py        # Autenticación JWT
│   │   │   ├── sensor_service.py      # Lecturas y agregaciones
│   │   │   ├── alert_service.py       # Motor de alertas cloud
│   │   │   ├── report_service.py      # Generación de reportes
│   │   │   ├── sync_service.py        # Reconciliación gateway-cloud
│   │   │   ├── notification_service.py # Email, SMS, push, webhooks
│   │   │   └── tenant_service.py      # Gestión multi-tenant
│   │   ├── models/                    # Modelos SQLAlchemy (ORM)
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # Usuario (con serial_number, role admin/user)
│   │   │   ├── tenant.py
│   │   │   ├── gateway.py             # Gateway (compatibilidad con EchoPy)
│   │   │   ├── echopy.py              # Dispositivo EchoPy (RPi del kit)
│   │   │   ├── serial.py              # Número de serie (ES-YYYYMM-XXXX)
│   │   │   ├── sensor.py
│   │   │   ├── reading.py
│   │   │   ├── alert.py
│   │   │   └── report.py
│   │   ├── schemas/                   # Esquemas Pydantic (validación)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── serial.py              # Validación y generación de seriales
│   │   │   ├── echopy.py              # Bind, diagnósticos, remote
│   │   │   ├── gateway.py
│   │   │   ├── sensor.py
│   │   │   ├── alert.py
│   │   │   └── report.py
│   │   ├── middleware/                # Middlewares FastAPI
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py     # Validación de JWT
│   │   │   ├── tenant_middleware.py   # Inyección de tenant_id
│   │   │   └── rate_limit.py         # Rate limiting
│   │   ├── workers/                   # Tareas asincrónicas
│   │   │   ├── __init__.py
│   │   │   ├── alert_worker.py       # Procesamiento de alertas
│   │   │   └── report_worker.py      # Generación de reportes
│   │   └── websocket/                 # WebSocket para tiempo real
│   │       ├── __init__.py
│   │       └── sensor_ws.py          # Canal de sensores en tiempo real
│   ├── migrations/                    # Migraciones Alembic
│   │   └── versions/
│   └── tests/                         # Tests del backend
│       ├── __init__.py
│       ├── conftest.py                # Fixtures compartidos
│       ├── test_auth.py
│       ├── test_sensors.py
│       ├── test_alerts.py
│       ├── test_gateways.py
│       └── test_reports.py
│
├── frontend/                          # Aplicación web React
│   ├── package.json                   # Dependencias Node.js
│   ├── vite.config.js                 # Configuración de Vite
│   ├── Dockerfile                     # Imagen Docker del frontend
│   ├── .env.example                   # Variables de entorno del frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── main.jsx                   # Punto de entrada React
│   │   ├── App.jsx                    # Componente raíz con rutas
│   │   ├── api/                       # Clientes HTTP
│   │   │   ├── client.js              # Axios configurado con JWT
│   │   │   ├── auth.js                # Endpoints de autenticación
│   │   │   ├── sensors.js             # Endpoints de sensores
│   │   │   ├── alerts.js              # Endpoints de alertas
│   │   │   └── reports.js             # Endpoints de reportes
│   │   ├── components/                # Componentes React por feature
│   │   │   ├── Dashboard/
│   │   │   ├── Charts/
│   │   │   ├── Sensors/
│   │   │   ├── Alerts/
│   │   │   ├── Reports/
│   │   │   ├── Admin/
│   │   │   └── Auth/
│   │   ├── hooks/                     # Custom hooks
│   │   │   ├── useReadings.js
│   │   │   ├── useWebSocket.js
│   │   │   └── useAuth.js
│   │   ├── store/                     # Redux Toolkit
│   │   │   ├── index.js
│   │   │   ├── slices/
│   │   │   │   ├── authSlice.js
│   │   │   │   ├── sensorSlice.js
│   │   │   │   └── alertSlice.js
│   │   │   └── api/                   # RTK Query
│   │   │       └── apiSlice.js
│   │   ├── i18n/                      # Internacionalización
│   │   │   ├── index.js
│   │   │   ├── es.json
│   │   │   └── en.json
│   │   ├── theme/                     # Theming dinámico
│   │   │   └── index.js
│   │   └── utils/                     # Utilidades
│   │       ├── formatters.js
│   │       └── validators.js
│   └── tests/                         # Tests del frontend
│       ├── setup.js
│       └── components/
│
├── gateway/                           # Software del gateway Raspberry Pi
│   ├── main.py                        # Orquestador principal
│   ├── requirements.txt               # Dependencias Python
│   ├── sensors.json                   # Configuración de sensores
│   ├── .env.example                   # Variables de entorno del gateway
│   ├── echosmart-gateway.service      # Servicio systemd
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuración del gateway
│   │   ├── hal.py                     # Hardware Abstraction Layer
│   │   ├── sensor_manager.py          # Gestión centralizada de sensores
│   │   ├── alert_engine.py            # Motor de alertas local
│   │   ├── cloud_sync.py              # Sincronización con backend
│   │   ├── mqtt_publisher.py          # Publicador MQTT local
│   │   ├── discovery.py               # Descubrimiento SSDP
│   │   ├── local_db.py                # Caché SQLite
│   │   └── sensor_drivers/            # Drivers por tipo de sensor
│   │       ├── __init__.py
│   │       ├── ds18b20.py             # Temperatura 1-Wire
│   │       ├── dht22.py               # Temperatura + humedad GPIO
│   │       ├── bh1750.py              # Luminosidad I2C
│   │       ├── soil_moisture.py       # Humedad de suelo ADC
│   │       └── mhz19c.py             # CO₂ UART
│   └── tests/                         # Tests del gateway
│       ├── __init__.py
│       ├── test_sensor_manager.py
│       ├── test_alert_engine.py
│       └── test_cloud_sync.py
│
├── mobile/                            # App móvil React Native
│   ├── package.json
│   ├── app.json                       # Configuración Expo
│   ├── App.js
│   ├── src/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── navigation/
│   │   └── services/
│   └── assets/
│
└── infra/                             # Infraestructura y configuración
    ├── docker/
    │   ├── backend.Dockerfile
    │   └── frontend.Dockerfile
    ├── k8s/                           # Manifiestos Kubernetes
    │   ├── backend-deployment.yaml
    │   ├── frontend-deployment.yaml
    │   ├── postgres-statefulset.yaml
    │   ├── influxdb-statefulset.yaml
    │   ├── redis-deployment.yaml
    │   └── ingress.yaml
    ├── nginx/
    │   └── nginx.conf                 # Reverse proxy
    ├── mosquitto/
    │   └── mosquitto.conf             # Configuración MQTT
    └── scripts/
        ├── setup-dev.sh               # Script de setup desarrollo
        ├── backup-db.sh               # Backup de bases de datos
        └── deploy.sh                  # Script de despliegue
```

---

## Descripción de Cada Capa

### `backend/` — API Cloud (FastAPI)

Contiene la API REST principal, los servicios de negocio, los modelos ORM y las tareas asincrónicas.

| Directorio | Responsabilidad |
|------------|----------------|
| `routers/` | Definición de endpoints REST agrupados por recurso |
| `services/` | Lógica de negocio (autenticación, alertas, reportes, sincronización) |
| `models/` | Modelos SQLAlchemy mapeados a tablas PostgreSQL |
| `schemas/` | Esquemas Pydantic para validación de request/response |
| `middleware/` | Middlewares de autenticación, tenant y rate limiting |
| `workers/` | Workers asincrónicos para alertas y reportes |
| `websocket/` | Canal WebSocket para actualizaciones en tiempo real |
| `migrations/` | Migraciones de base de datos con Alembic |
| `tests/` | Tests unitarios e integración con pytest |

### `frontend/` — Dashboard Web (React)

Aplicación single-page con React 18, Redux Toolkit y Recharts.

| Directorio | Responsabilidad |
|------------|----------------|
| `api/` | Clientes HTTP con Axios configurado y JWT |
| `components/` | Componentes React organizados por feature |
| `hooks/` | Custom hooks (`useReadings`, `useWebSocket`, `useAuth`) |
| `store/` | Redux Toolkit con slices y RTK Query |
| `i18n/` | Archivos de traducción (español, inglés) |
| `theme/` | Theming dinámico por tenant |
| `utils/` | Funciones de formato y validación |

### `gateway/` — Edge Computing (Raspberry Pi)

Software que se ejecuta en la Raspberry Pi para leer sensores, evaluar alertas locales y sincronizar con la nube.

| Directorio | Responsabilidad |
|------------|----------------|
| `src/hal.py` | Hardware Abstraction Layer (GPIO, I2C, 1-Wire, UART) |
| `src/sensor_drivers/` | Drivers individuales para cada tipo de sensor |
| `src/sensor_manager.py` | Orquestación de lecturas y polling |
| `src/alert_engine.py` | Evaluación local de reglas de alerta |
| `src/cloud_sync.py` | Sincronización batch con reintentos |
| `src/mqtt_publisher.py` | Publicación de lecturas en MQTT local |
| `src/discovery.py` | Auto-descubrimiento SSDP |
| `src/local_db.py` | Caché de lecturas en SQLite |

### `mobile/` — App Móvil (React Native)

Aplicación móvil con Expo para iOS y Android con capacidad offline.

### `infra/` — Infraestructura

Configuración de Docker, Kubernetes, Nginx y scripts de automatización.

---

## Dependencias Principales

### Backend (Python)

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| fastapi | 0.100+ | Framework web |
| uvicorn | 0.23+ | Servidor ASGI |
| sqlalchemy | 2.0+ | ORM para PostgreSQL |
| alembic | 1.12+ | Migraciones de BD |
| pydantic | 2.0+ | Validación de datos |
| influxdb-client | 1.36+ | Cliente InfluxDB |
| redis | 5.0+ | Cliente Redis |
| python-jose | 3.3+ | JWT tokens |
| bcrypt | 4.0+ | Hashing de contraseñas |
| celery | 5.3+ | Workers asíncronos |
| pytest | 7.4+ | Testing |

### Frontend (Node.js)

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| react | 18+ | Librería UI |
| react-dom | 18+ | Renderizado web |
| @reduxjs/toolkit | 1.9+ | State management |
| react-router-dom | 6+ | Routing |
| recharts | 2.10+ | Gráficas |
| axios | 1.5+ | Cliente HTTP |
| react-i18next | 13+ | Internacionalización |
| @mui/material | 5+ | Componentes UI (opción A) |
| tailwindcss | 3+ | CSS utilities (opción B) |
| jest | 29+ | Testing |

### Gateway (Python)

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| RPi.GPIO | 0.7+ | Control de pines GPIO |
| adafruit-circuitpython-dht | 3.7+ | Driver DHT22 |
| adafruit-circuitpython-bh1750 | 1.1+ | Driver BH1750 |
| adafruit-circuitpython-ads1x15 | 2.2+ | Driver ADC ADS1115 |
| paho-mqtt | 1.6+ | Cliente MQTT |
| requests | 2.28+ | Sincronización HTTP |

---

*Volver al [Índice de Documentación](README.md)*
