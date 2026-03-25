# EchoSmart — Lista de Tareas de Desarrollo Multiplataforma

> Proyecto IoT de agricultura de precisión para monitoreo ambiental inteligente en invernaderos.

---

## Fase 0: Estructura del Proyecto y Assets de Diseño ✅

### 0.1 Estructura Multiplataforma
- [x] Crear TASK_LIST.md con plan de desarrollo completo
- [x] Scaffolding del backend FastAPI (`backend/`)
- [x] Scaffolding del frontend React + Vite (`frontend/`)
- [x] Scaffolding del gateway Raspberry Pi (`gateway/`)
- [x] Scaffolding de la app móvil React Native/Expo (`mobile/`)
- [x] Scaffolding de la app de escritorio Electron (`desktop/`)
- [x] Módulo compartido (`shared/`)
- [x] Infraestructura Docker/K8s/Nginx/Mosquitto (`infra/`)
- [x] `docker-compose.yml` para orquestación
- [x] README.md actualizado con toda la documentación

### 0.2 Diagramas y Documentación Técnica (6 SVG)
- [x] Diagrama de arquitectura general (3 capas: Edge → Cloud → Clientes)
- [x] Diagrama de flujo de datos E2E (Sensor → HAL → Manager → Cloud → Frontend)
- [x] Diagrama ER (PostgreSQL: tenants, users, gateways, sensors, readings, alerts, reports)
- [x] Diagrama de despliegue (Docker/K8s, CDN, RPi)
- [x] Diagrama de flujo de autenticación (JWT + RBAC)
- [x] Diagrama de red de sensores (topología + protocolos: 1-Wire, GPIO, I2C, ADC, UART)

### 0.3 Wireframes y Bocetos (6 SVG)
- [x] Wireframe — Dashboard web
- [x] Wireframe — Login
- [x] Wireframe — App móvil
- [x] Wireframe — Admin panel
- [x] Wireframe — Mapa del invernadero
- [x] Wireframe — Centro de alertas

### 0.4 Mockups 4K — Plataforma Web (10 PNG 3840×2160 + 5 SVG)
- [x] `mockup-web-dashboard.png` — Dashboard principal con métricas y gráficas
- [x] `mockup-web-login.png` — Página de inicio de sesión
- [x] `mockup-web-sensors.png` — Lista/grid de sensores
- [x] `mockup-web-sensor-detail.png` — Detalle de sensor individual
- [x] `mockup-web-alerts.png` — Centro de alertas
- [x] `mockup-web-map.png` — Mapa del invernadero
- [x] `mockup-web-reports.png` — Generador de reportes
- [x] `mockup-web-settings.png` — Configuración
- [x] `mockup-web-users.png` — Gestión de usuarios
- [x] `mockup-web-gateway-detail.png` — Detalle de gateway
- [x] 5 mockups SVG vectoriales (dashboard, sensors, alerts, map, settings)

### 0.5 Mockups 4K — App Móvil (10 PNG 1290×2796)
- [x] `mockup-mobile-home.png` — Pantalla principal
- [x] `mockup-mobile-sensors.png` — Lista de sensores
- [x] `mockup-mobile-sensor-detail.png` — Detalle de sensor
- [x] `mockup-mobile-alerts.png` — Alertas
- [x] `mockup-mobile-map.png` — Mapa del invernadero
- [x] `mockup-mobile-settings.png` — Configuración/perfil
- [x] `mockup-mobile-notifications.png` — Centro de notificaciones
- [x] `mockup-mobile-add-sensor.png` — Agregar sensor
- [x] `mockup-mobile-chart-fullscreen.png` — Gráfica a pantalla completa
- [x] `mockup-mobile-login.png` — Login móvil

### 0.6 Mockups 4K — App de Escritorio (8 PNG 3840×2160)
- [x] `mockup-desktop-dashboard.png` — Dashboard principal
- [x] `mockup-desktop-sensors.png` — Gestión de sensores
- [x] `mockup-desktop-sensor-detail.png` — Detalle de sensor
- [x] `mockup-desktop-alerts.png` — Centro de alertas
- [x] `mockup-desktop-map.png` — Mapa del invernadero
- [x] `mockup-desktop-reports.png` — Reportes
- [x] `mockup-desktop-settings.png` — Configuración
- [x] `mockup-desktop-system-monitor.png` — Monitor del sistema

### 0.7 Iconos y Logos — Sin Fondo (Transparentes)
- [x] 133 iconos PNG sin fondo (tamaños: 16, 32, 48, 64, 96, 128, 192, 256, 384, 512, 1024, 2048, 4096px)
  - [x] App icon cuadrado + circular en 13 tamaños (hasta 4096px)
  - [x] 9 sensor icons (temperature, humidity, light, soil, co2, satellite, greenhouse, alert, gateway) × 6 tamaños
  - [x] 7 navigation icons (dashboard, sensors, alerts, map, reports, settings, users) × 5 tamaños
- [x] 35 iconos JPG con fondo negro (tamaños: 512, 1024, 2048, 4096px)
- [x] 32 iconos SVG de interfaz (`assets/icons/ui/`) — sensor, nav, acciones, estados
- [x] 2 archivos ICO multi-resolución (favicon.ico: 16/32/48/64px, app.ico: 16/32/48/64/128/256px)

### 0.8 Logos de Marca (SVG + PNG + JPG)
- [x] `echosmart-icon.svg` — Ícono de hoja+señal (sin fondo)
- [x] `echosmart-logo-full.svg` — Logo horizontal completo
- [x] `echosmart-logo-dark.svg` — Para fondos oscuros
- [x] `echosmart-logo-light.svg` — Para fondos claros
- [x] `echosmart-logo-horizontal.svg` — Variante horizontal ancha
- [x] `echosmart-logo-stacked.svg` — Ícono arriba, texto abajo
- [x] `echosmart-wordmark.svg` — Solo texto "EchoSmart"
- [x] 8 logos PNG sin fondo (256, 512, 1024, 2048px — icon, horizontal, stacked)
- [x] 4 logos JPG (1024, 2048px)

### 0.9 Assets por Plataforma
- [x] **Android**: feature graphic (1024×500), adaptive icon (foreground + background + round), splash xxhdpi + xxxhdpi
- [x] **iOS**: app icon (1024×1024), preview header (1284×628), splash 2x + 3x + Super Retina
- [x] **Desktop**: DMG background (660×400), installer banner NSIS (500×314), macOS icon (1024), tray icons (32/64/128)
- [x] **Web**: Open Graph PNG + JPG (1200×630), PWA icons (192/512), maskable icon (512), apple-touch-icon (180)
- [x] **Social**: Twitter card (1200×600), Instagram post (1080×1080), LinkedIn banner (1584×396)

### 0.10 Splash Screens (6 resoluciones)
- [x] `splash-750x1334.png` — iOS 2x
- [x] `splash-1080x1920.png` — Android xxhdpi
- [x] `splash-1242x2208.png` — iOS Plus
- [x] `splash-1290x2796.png` — iOS Pro Max / Super Retina
- [x] `splash-1440x2560.png` — Android xxxhdpi / QHD
- [x] `splash-2160x3840.png` — 4K

### 0.11 Ilustraciones SVG (8 archivos)
- [x] Empty states: sensors vacíos, alertas vacías, sin datos
- [x] Onboarding: conectar gateway, monitorear, configurar alertas
- [x] Errores: conexión perdida, 404

### 0.12 Elementos de App Design (6 SVG)
- [x] `status-online.svg`, `status-offline.svg`, `status-warning.svg` — Indicadores de estado
- [x] `card-sensor.svg` — Template de tarjeta de sensor
- [x] `card-alert.svg` — Template de tarjeta de alerta
- [x] `nav-sidebar.svg` — Template de navegación lateral

### 0.13 Esquema de Colores — Tema Puro Negro (Starlink-style)
- [x] Fondo: `#000000` (negro puro, sin tono verdoso)
- [x] Superficies/cards: `#111111` (gris oscuro neutro)
- [x] Elevados: `#1A1A1A`
- [x] Sidebar: `#0A0A0A`
- [x] Acento verde: `#00E676`, Acento cyan: `#00BCD4`
- [x] Sin líneas de grid, sin franjas verdes, sin patrones decorativos

---

## Fase 1: MVP — Gateway Local (Semanas 1–3)

### 1.1 Configuración del Hardware
- [ ] Provisionar Raspberry Pi 4B con Raspberry Pi OS 64-bit
- [ ] Configurar interfaces GPIO, I2C, 1-Wire y UART
- [ ] Conectar sensores: DS18B20, DHT22, BH1750
- [ ] Conectar sensores: Soil Moisture (ADS1115), MHZ-19C (CO₂)
- [ ] Calibrar cada sensor y verificar lecturas de prueba

### 1.2 Software del Gateway
- [x] Implementar Hardware Abstraction Layer (`gateway/src/hal.py`)
- [x] Desarrollar drivers de sensores en `gateway/src/sensor_drivers/`
  - [x] `ds18b20.py` — Temperatura (1-Wire)
  - [x] `dht22.py` — Temperatura + Humedad (GPIO)
  - [x] `bh1750.py` — Luminosidad (I2C)
  - [x] `soil_moisture.py` — Humedad de suelo (ADC)
  - [x] `mhz19c.py` — CO₂ (UART)
- [x] Implementar `sensor_manager.py` con polling configurable
- [x] Implementar caché local en SQLite (`local_db.py`)
- [ ] Configurar broker MQTT local (Mosquitto)
- [x] Implementar `mqtt_publisher.py` para publicación local
- [x] Implementar `discovery.py` con auto-descubrimiento SSDP
- [x] Implementar `alert_engine.py` — Motor de alertas local
- [x] Implementar `cloud_sync.py` — Sincronización batch con reintentos
- [x] Escribir tests unitarios para cada driver y módulo
- [ ] Configurar servicio systemd (`echosmart-gateway.service`)

---

## Fase 2: Backend Cloud (Semanas 4–7)

### 2.1 Infraestructura
- [ ] Provisionar servidor cloud (AWS EC2 / DigitalOcean)
- [ ] Instalar y configurar PostgreSQL 14+
- [ ] Instalar y configurar InfluxDB 2.7+
- [ ] Instalar y configurar Redis 7+
- [x] Configurar Docker y docker-compose para desarrollo

### 2.2 API Backend (FastAPI)
- [x] Crear punto de entrada FastAPI (`backend/src/main.py`)
- [x] Configurar conexión a bases de datos (`backend/src/database.py`)
- [x] Implementar configuración centralizada (`backend/src/config.py`)
- [x] Implementar modelos ORM con SQLAlchemy en `backend/src/models/`
  - [x] `user.py`, `tenant.py`, `gateway.py`, `sensor.py`
  - [x] `reading.py`, `alert.py`, `report.py`
- [x] Implementar esquemas Pydantic en `backend/src/schemas/`
- [x] Implementar middlewares en `backend/src/middleware/`
  - [x] `auth_middleware.py` — Validación JWT
  - [x] `tenant_middleware.py` — Inyección de tenant_id
  - [x] `rate_limit.py` — Rate limiting
- [x] Implementar routers REST en `backend/src/routers/`
  - [x] `auth.py` — `/api/v1/auth/*`
  - [x] `gateways.py` — `/api/v1/gateways/*`
  - [x] `sensors.py` — `/api/v1/sensors/*`
  - [x] `alerts.py` — `/api/v1/alerts/*`
  - [x] `reports.py` — `/api/v1/reports/*`
  - [x] `users.py` — `/api/v1/users/*`
  - [x] `tenants.py` — `/api/v1/tenants/*`
- [x] Implementar servicios de negocio en `backend/src/services/`
  - [x] `auth_service.py` — Autenticación JWT + RBAC
  - [x] `sensor_service.py` — Lecturas y agregaciones
  - [x] `alert_service.py` — Motor de alertas cloud
  - [x] `report_service.py` — Generación de reportes PDF/Excel
  - [x] `sync_service.py` — Reconciliación gateway-cloud
  - [x] `notification_service.py` — Email, SMS, push, webhooks
  - [x] `tenant_service.py` — Gestión multi-tenant
- [x] Implementar workers asíncronos (`backend/src/workers/`)
- [x] Implementar WebSocket para tiempo real (`backend/src/websocket/`)
- [ ] Configurar migraciones con Alembic
- [x] Escribir tests (pytest) para cada endpoint y servicio

---

## Fase 3: Frontend Web — React (Semanas 8–10)

### 3.1 Configuración del Proyecto
- [x] Inicializar proyecto React 18 con Vite en `frontend/`
- [x] Configurar Redux Toolkit, React Router, i18n
- [ ] Configurar Tailwind CSS / Material-UI
- [x] Configurar cliente HTTP (Axios) con JWT
- [ ] Configurar ESLint + Prettier

### 3.2 Componentes y Páginas
- [x] Implementar autenticación (Login, Forgot Password, ProtectedRoute)
- [x] Implementar layout principal (Header, Sidebar, Footer, Breadcrumb)
- [x] Implementar Dashboard con gráficas en tiempo real (Recharts)
- [x] Implementar gestión de sensores (CRUD, detalle, estado)
- [x] Implementar centro de alertas (reglas, historial, acknowledgment)
- [x] Implementar generador de reportes (PDF/Excel)
- [x] Implementar panel de administración (usuarios, tenants, gateways)
- [ ] Implementar theming dinámico por tenant
- [x] Implementar internacionalización (español/inglés)

### 3.3 Optimización y Testing
- [ ] Implementar code splitting con lazy loading
- [ ] Implementar memoización y virtualización de listas
- [ ] Conectar WebSocket para actualizaciones en tiempo real
- [ ] Escribir tests unitarios (Vitest + React Testing Library)
- [ ] Lograr 90+ en Lighthouse score

---

## Fase 4: Aplicación Móvil — React Native (Semanas 11–16)

### 4.1 Android
- [x] Configurar proyecto Expo en `mobile/`
- [ ] Implementar pantallas principales (Dashboard, Sensores, Alertas)
- [ ] Implementar navegación con React Navigation
- [ ] Implementar push notifications (Firebase Cloud Messaging)
- [ ] Implementar modo offline con almacenamiento local
- [ ] Implementar dark/light mode
- [ ] Configurar build para Android (`eas build --platform android`)
- [ ] Pruebas en dispositivos Android reales
- [ ] Publicar en Google Play Store

### 4.2 iOS
- [ ] Configurar build para iOS (`eas build --platform ios`)
- [ ] Adaptar UI para convenciones iOS (Safe Area, gestos)
- [ ] Implementar login biométrico (Face ID / Touch ID)
- [ ] Pruebas en dispositivos iOS reales
- [ ] Publicar en App Store

### 4.3 Componentes Compartidos (Mobile)
- [ ] Implementar servicios API compartidos (`mobile/src/services/`)
- [ ] Implementar componentes reutilizables (`mobile/src/components/`)
- [ ] Implementar store (Redux Toolkit / Zustand)
- [ ] Implementar hooks personalizados
- [ ] Escribir tests unitarios

---

## Fase 5: Aplicación de Escritorio — Electron (Semanas 17–20)

### 5.1 Windows
- [x] Configurar proyecto Electron en `desktop/`
- [ ] Empaquetar frontend React como app de escritorio
- [ ] Implementar menú nativo de Windows y bandeja del sistema
- [ ] Implementar notificaciones nativas del sistema
- [ ] Implementar auto-update (electron-updater)
- [ ] Generar instalador `.exe` / `.msi` con electron-builder
- [ ] Firmar el ejecutable con certificado de código
- [ ] Pruebas en Windows 10/11

### 5.2 macOS
- [ ] Configurar build para macOS (`.dmg` / `.app`)
- [ ] Adaptar menú nativo para macOS
- [ ] Implementar integración con barra de menú (menubar)
- [ ] Firmar la app con Apple Developer certificate
- [ ] Notarización de la app para distribución
- [ ] Pruebas en macOS

### 5.3 Linux
- [ ] Configurar build para Linux (`.AppImage` / `.deb` / `.snap`)
- [ ] Adaptar notificaciones para entorno de escritorio Linux
- [ ] Pruebas en Ubuntu/Debian

### 5.4 Funcionalidades Compartidas (Desktop)
- [x] Implementar main process de Electron (`desktop/src/main/`)
- [x] Implementar preload scripts seguros (`desktop/src/preload/`)
- [x] Integrar frontend React como renderer (`desktop/src/renderer/`)
- [ ] Implementar IPC entre main y renderer
- [ ] Implementar almacenamiento local (electron-store)
- [ ] Implementar conexión directa al gateway vía red local
- [ ] Escribir tests

---

## Fase 6: Infraestructura y DevOps (Continuo)

### 6.1 Docker
- [ ] Crear Dockerfile para backend (`infra/docker/backend.Dockerfile`)
- [ ] Crear Dockerfile para frontend (`infra/docker/frontend.Dockerfile`)
- [x] Crear `docker-compose.yml` para orquestación de desarrollo
- [ ] Crear `docker-compose.prod.yml` para producción

### 6.2 Kubernetes
- [x] Crear manifiestos en `infra/k8s/`
  - [x] `backend-deployment.yaml`
  - [ ] `frontend-deployment.yaml`
  - [ ] `postgres-statefulset.yaml`
  - [ ] `influxdb-statefulset.yaml`
  - [ ] `redis-deployment.yaml`
  - [x] `ingress.yaml`

### 6.3 CI/CD (GitHub Actions)
- [ ] Pipeline CI: lint + tests en cada push/PR
- [ ] Pipeline CD: build y despliegue a producción
- [ ] Pipeline para builds móviles (EAS Build)
- [ ] Pipeline para builds de escritorio (Electron)

### 6.4 Scripts de Automatización
- [ ] `infra/scripts/setup-dev.sh` — Configuración de entorno de desarrollo
- [ ] `infra/scripts/backup-db.sh` — Backup de bases de datos
- [ ] `infra/scripts/deploy.sh` — Script de despliegue

---

## Fase 7: Features Avanzadas (Semanas 21+)

### 7.1 Control de Actuadores
- [ ] Implementar control de relés (riego, ventilación, iluminación)
- [ ] Implementar programación horaria de actuadores
- [ ] Implementar automatización por reglas (si temp > 35°C → activar ventilación)

### 7.2 Analítica Predictiva (ML)
- [ ] Implementar predicción de temperatura
- [ ] Implementar detección de anomalías
- [ ] Implementar recomendaciones de riego

### 7.3 Integraciones
- [ ] WhatsApp Business API
- [ ] Slack / Microsoft Teams
- [ ] Telegram Bot
- [ ] API meteorológica (OpenWeatherMap)

### 7.4 Administración Avanzada
- [ ] Audit log completo
- [ ] SSO (Google, Microsoft, SAML)
- [ ] 2FA (TOTP)
- [ ] Sistema de suscripciones y facturación

---

## Resumen de Plataformas

| Plataforma | Tecnología | Directorio | Estado |
|------------|-----------|------------|--------|
| **Backend (Cloud)** | FastAPI · PostgreSQL · InfluxDB · Redis | `backend/` | 🟡 Scaffolding completo |
| **Frontend (Web)** | React 18 · Vite · Redux Toolkit · Recharts | `frontend/` | 🟡 Scaffolding completo |
| **Gateway (Edge)** | Python · Raspberry Pi · SQLite · MQTT | `gateway/` | 🟡 Scaffolding completo |
| **Móvil (Android)** | React Native · Expo | `mobile/` | 🟠 Estructura inicial |
| **Móvil (iOS)** | React Native · Expo | `mobile/` | 🟠 Estructura inicial |
| **Escritorio (Windows)** | Electron · React | `desktop/` | 🟠 Estructura inicial |
| **Escritorio (macOS)** | Electron · React | `desktop/` | 🟠 Estructura inicial |
| **Escritorio (Linux)** | Electron · React | `desktop/` | 🟠 Estructura inicial |
| **Infraestructura** | Docker · Kubernetes · GitHub Actions | `infra/` | 🟡 Docker + K8s parcial |
| **Assets / Diseño** | SVG · PNG · JPG · ICO | `assets/` | 🟢 312 archivos generados |
| **Documentación** | Markdown · SVG | `docs/` | 🟢 Diagramas + wireframes |

## Resumen de Assets Generados

| Categoría | Cantidad | Formatos | Detalles |
|-----------|----------|----------|----------|
| Mockups Web 4K | 10 + 5 SVG | PNG (3840×2160), SVG | Dashboard, login, sensors, alerts, map, reports, settings, users, gateway |
| Mockups Mobile | 10 | PNG (1290×2796) | Home, sensors, detail, alerts, map, settings, notifications, add sensor, chart, login |
| Mockups Desktop 4K | 8 | PNG (3840×2160) | Dashboard, sensors, detail, alerts, map, reports, settings, system monitor |
| Iconos App | 26 | PNG (RGBA), JPG | 13 tamaños: 16px–4096px, cuadrado + circular |
| Iconos Sensores | 54 | PNG (RGBA) | 9 tipos × 6 tamaños (48–512px) |
| Iconos Navegación | 35 | PNG (RGBA) | 7 tipos × 5 tamaños (48–512px) |
| Iconos UI | 32 | SVG | Dashboard, sensors, alerts, charts, settings, etc. |
| Iconos JPG | 35 | JPG | App + sensor icons en alta resolución |
| ICO | 2 | ICO | favicon.ico + app.ico multi-resolución |
| Logos | 7 SVG + 8 PNG + 4 JPG | SVG, PNG, JPG | Icon, full, dark, light, horizontal, stacked, wordmark |
| Splash Screens | 6 | PNG | 750×1334 → 2160×3840 |
| Assets Android | 6 | PNG | Feature graphic, adaptive icon, splash |
| Assets iOS | 5 | PNG | App icon 1024, preview header, splash 2x/3x/SR |
| Assets Desktop | 6 | PNG | DMG bg, installer banner, macOS icon, tray icons |
| Assets Web | 6 | PNG, JPG | OG image, PWA icons, maskable, apple-touch |
| Assets Social | 3 | PNG | Twitter card, Instagram post, LinkedIn banner |
| Ilustraciones | 8 | SVG | Empty states, onboarding, errores |
| App Design | 6 | SVG | Status indicators, card templates, nav template |
| Diagramas | 6 | SVG | Arquitectura, flujo datos, ER, despliegue, auth, red sensores |
| Wireframes | 6 | SVG | Dashboard, login, mobile, admin, mapa, alertas |
| **Total** | **312** | **SVG, PNG, JPG, ICO** | |

---

*Última actualización: 25 de marzo de 2026*
