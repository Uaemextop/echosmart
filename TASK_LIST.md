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

> ⚠️ **IMPORTANTE — Enfoque "Simulation-First"**: Todo el desarrollo de drivers y software del gateway se realiza **sin hardware físico**. Cada driver incluye un modo de simulación (`simulation=True`) que genera datos realistas dentro de los rangos del invernadero. El hardware físico (Raspberry Pi + sensores) se integra únicamente en la **Fase 8: Testing con Hardware Real**.

### 1.1 Definición de Sensores para Invernadero Inteligente

A continuación se definen los **5 sensores** seleccionados para el proyecto. Cada uno fue investigado y validado como apropiado para monitoreo ambiental en invernaderos agrícolas.

#### 🌡️ Sensor 1: DS18B20 — Temperatura Ambiental
| Especificación | Valor |
|---|---|
| **Modelo** | Dallas DS18B20 (versión encapsulada impermeable) |
| **Variable** | Temperatura del aire / sustrato |
| **Protocolo** | 1-Wire (un solo pin de datos, hasta 100m de cable) |
| **Rango de medición** | -55°C a +125°C |
| **Precisión** | ±0.5°C (en rango -10°C a +85°C) |
| **Resolución** | 9–12 bits configurable (0.0625°C a 12 bits) |
| **Alimentación** | 3.0V – 5.5V (compatible con RPi 3.3V) |
| **Rango óptimo invernadero** | 18°C – 28°C |
| **¿Por qué este sensor?** | Estándar de facto en proyectos IoT agrícolas. Resistente al agua (versión encapsulada), permite múltiples sensores en el mismo bus 1-Wire con direcciones únicas. Precio bajo (~$2 USD). Compatible nativo con Raspberry Pi. |
| **Driver** | `gateway/src/sensor_drivers/ds18b20.py` |
| **Simulación** | Genera valores aleatorios entre 15.0°C y 35.0°C |

#### 💧 Sensor 2: DHT22 (AM2302) — Temperatura + Humedad Relativa
| Especificación | Valor |
|---|---|
| **Modelo** | Aosong DHT22 / AM2302 |
| **Variables** | Temperatura + Humedad relativa del aire |
| **Protocolo** | Protocolo propietario 1-wire digital (GPIO) |
| **Rango temperatura** | -40°C a +80°C (±0.5°C) |
| **Rango humedad** | 0% – 100% RH (±2–5% RH) |
| **Frecuencia de muestreo** | 1 lectura cada 2 segundos (0.5 Hz) |
| **Alimentación** | 3.3V – 6V |
| **Rango óptimo invernadero** | Temp: 18–28°C, Humedad: 60–80% RH |
| **¿Por qué este sensor?** | Combina temperatura y humedad en un solo módulo. Mejor precisión que el DHT11. Muy utilizado en agricultura de precisión. Bajo costo (~$3 USD). Amplia librería de soporte en Python (`adafruit-circuitpython-dht`). |
| **Driver** | `gateway/src/sensor_drivers/dht22.py` |
| **Simulación** | Temp: 15.0–35.0°C, Humedad: 40.0–90.0% |

#### ☀️ Sensor 3: BH1750 — Luminosidad (Lux)
| Especificación | Valor |
|---|---|
| **Modelo** | ROHM BH1750FVI |
| **Variable** | Intensidad luminosa (iluminancia) |
| **Protocolo** | I2C (dirección 0x23 o 0x5C) |
| **Rango de medición** | 1 – 65,535 lux |
| **Resolución** | 1 lux (modo alta resolución) |
| **Precisión** | ±20% (respuesta espectral similar al ojo humano) |
| **Alimentación** | 2.4V – 3.6V (compatible con RPi 3.3V) |
| **Rango óptimo invernadero** | 10,000 – 30,000 lux |
| **¿Por qué este sensor?** | Sensor digital de luz con salida directa en lux (no requiere conversión). Protocolo I2C estándar. Ideal para determinar si el invernadero necesita iluminación suplementaria o protección contra exceso de luz. Precio muy bajo (~$1.5 USD). |
| **Driver** | `gateway/src/sensor_drivers/bh1750.py` |
| **Simulación** | Genera valores entre 500 y 50,000 lux |

#### 🌱 Sensor 4: Sensor de Humedad de Suelo + ADS1115 (ADC)
| Especificación | Valor |
|---|---|
| **Modelo** | Sensor capacitivo de humedad de suelo v1.2 + ADS1115 (ADC 16-bit) |
| **Variable** | Humedad volumétrica del sustrato/suelo |
| **Protocolo** | Analógico → I2C (vía ADS1115) |
| **Rango de medición** | 0% – 100% (calibrado a capacitancia del suelo) |
| **Resolución ADC** | 16 bits (ADS1115), 4 canales multiplexados |
| **Alimentación** | 3.3V – 5V |
| **Rango óptimo invernadero** | 50% – 80% de humedad de suelo |
| **¿Por qué este sensor?** | El sensor capacitivo (v1.2) es superior al resistivo: no se corroe, vida útil más larga. El ADS1115 proporciona conversión analógico-digital de alta resolución via I2C. Permite conectar hasta 4 sensores de suelo en un solo módulo. Precio combinado ~$4 USD. |
| **Driver** | `gateway/src/sensor_drivers/soil_moisture.py` |
| **Simulación** | Genera valores entre 20.0% y 90.0% |

#### 🏭 Sensor 5: MH-Z19C — Concentración de CO₂
| Especificación | Valor |
|---|---|
| **Modelo** | Winsen MH-Z19C (NDIR infrarrojo) |
| **Variable** | Concentración de dióxido de carbono (CO₂) |
| **Protocolo** | UART (TTL 3.3V, 9600 baud) + PWM |
| **Rango de medición** | 400 – 5,000 ppm (versión estándar) |
| **Precisión** | ±50 ppm + 5% del valor leído |
| **Tiempo de respuesta** | < 120 segundos (T90) |
| **Precalentamiento** | 3 minutos |
| **Vida útil** | > 5 años |
| **Alimentación** | 4.9V – 5.1V (requiere nivel de voltaje estable) |
| **Rango óptimo invernadero** | 400 – 1,000 ppm |
| **¿Por qué este sensor?** | Tecnología NDIR (infrarrojo no dispersivo) ofrece mediciones precisas y estables a largo plazo. Autocalibración incorporada (ABC logic). El CO₂ es crítico para la fotosíntesis; niveles altos indican ventilación insuficiente. Compatible con UART del RPi. Precio ~$18 USD. |
| **Driver** | `gateway/src/sensor_drivers/mhz19c.py` |
| **Simulación** | Genera valores entre 350 y 2,000 ppm |

#### Resumen de Sensores

| # | Sensor | Variable | Protocolo | Pin/Bus RPi | Rango Invernadero | Precio aprox. |
|---|--------|----------|-----------|-------------|-------------------|---------------|
| 1 | DS18B20 | Temperatura | 1-Wire | GPIO 4 | 18–28°C | ~$2 |
| 2 | DHT22 | Temp + Humedad | GPIO | GPIO 17 | 18–28°C / 60–80% | ~$3 |
| 3 | BH1750 | Luminosidad | I2C | SDA/SCL | 10K–30K lux | ~$1.5 |
| 4 | Soil Moisture + ADS1115 | Humedad suelo | I2C (ADC) | SDA/SCL | 50–80% | ~$4 |
| 5 | MH-Z19C | CO₂ | UART | TX/RX | 400–1000 ppm | ~$18 |
| | | | | **Total** | | **~$28.5** |

**Raspberry Pi recomendado**: Raspberry Pi 4 Model B (2GB+ RAM) — $35–55 USD
**Costo total estimado del hardware**: ~$65–85 USD (RPi + 5 sensores + cables/protoboard)

### 1.2 Software del Gateway (Desarrollo en Modo Simulación)

> 🖥️ **Todo el desarrollo de esta sección se realiza SIN hardware físico.** Los drivers operan en `simulation=True` por defecto, generando datos realistas para pruebas. La implementación de lectura real del hardware (GPIO, I2C, 1-Wire, UART) queda como `TODO` para completar en la Fase 8.

- [x] Implementar Hardware Abstraction Layer (`gateway/src/hal.py`)
  - [x] Clase `HAL` con métodos: `read_gpio()`, `read_i2c()`, `read_1wire()`, `read_uart()`
  - [x] Modo simulación que no requiere hardware real
  - [ ] Implementación real de GPIO (librería `RPi.GPIO` o `gpiozero`)
  - [ ] Implementación real de I2C (librería `smbus2`)
  - [ ] Implementación real de 1-Wire (lectura de `/sys/bus/w1/devices/`)
  - [ ] Implementación real de UART (librería `pyserial`)
- [x] Desarrollar drivers de sensores en `gateway/src/sensor_drivers/`
  - [x] `ds18b20.py` — Temperatura (1-Wire) — con modo simulación
  - [x] `dht22.py` — Temperatura + Humedad (GPIO) — con modo simulación
  - [x] `bh1750.py` — Luminosidad (I2C) — con modo simulación
  - [x] `soil_moisture.py` — Humedad de suelo (ADC via I2C) — con modo simulación
  - [x] `mhz19c.py` — CO₂ (UART) — con modo simulación
  - [ ] Implementar lectura real del DS18B20 desde `/sys/bus/w1/devices/28-*/w1_slave`
  - [ ] Implementar lectura real del DHT22 vía `adafruit-circuitpython-dht`
  - [ ] Implementar lectura real del BH1750 vía `smbus2` (registros I2C)
  - [ ] Implementar lectura real del ADS1115 vía `adafruit-circuitpython-ads1x15`
  - [ ] Implementar lectura real del MH-Z19C vía `pyserial` (protocolo UART 9600 baud)
- [x] Implementar `sensor_manager.py` con polling configurable
- [x] Implementar caché local en SQLite (`local_db.py`)
- [ ] Configurar broker MQTT local (Mosquitto)
- [x] Implementar `mqtt_publisher.py` para publicación local
- [x] Implementar `discovery.py` con auto-descubrimiento SSDP
- [x] Implementar `alert_engine.py` — Motor de alertas local
- [x] Implementar `cloud_sync.py` — Sincronización batch con reintentos
- [x] Escribir tests unitarios para cada driver y módulo (con simulación)
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

## Fase 8: Testing con Hardware Real (Final)

> 🔧 **Esta fase se ejecuta ÚNICAMENTE cuando todo el software está completo y probado en modo simulación.** Aquí se adquiere el hardware físico y se validan los drivers contra sensores reales.

### 8.1 Adquisición de Hardware
- [ ] Adquirir Raspberry Pi 4 Model B (2GB+ RAM)
- [ ] Adquirir fuente de alimentación oficial RPi (5V 3A USB-C)
- [ ] Adquirir tarjeta microSD (32GB+ clase 10)
- [ ] Adquirir sensor DS18B20 (versión encapsulada impermeable)
- [ ] Adquirir sensor DHT22 / AM2302
- [ ] Adquirir sensor BH1750FVI (módulo breakout)
- [ ] Adquirir sensor capacitivo de humedad de suelo v1.2
- [ ] Adquirir módulo ADC ADS1115 (16-bit, 4 canales)
- [ ] Adquirir sensor MH-Z19C (CO₂ NDIR)
- [ ] Adquirir protoboard, cables jumper, resistencias pull-up (4.7kΩ para 1-Wire)
- [ ] Verificar que todos los componentes sean compatibles con RPi 3.3V/5V

### 8.2 Configuración del Raspberry Pi
- [ ] Instalar Raspberry Pi OS 64-bit (Lite o Desktop)
- [ ] Habilitar interfaces: I2C (`raspi-config` → Interfacing → I2C)
- [ ] Habilitar interfaces: 1-Wire (`dtoverlay=w1-gpio` en `/boot/config.txt`)
- [ ] Habilitar interfaces: UART (`enable_uart=1` en `/boot/config.txt`, deshabilitar consola serial)
- [ ] Instalar dependencias del sistema: `python3-pip`, `python3-venv`, `i2c-tools`, `git`
- [ ] Verificar bus I2C: `i2cdetect -y 1` (debe mostrar dirección 0x23 del BH1750 y 0x48 del ADS1115)
- [ ] Verificar bus 1-Wire: `ls /sys/bus/w1/devices/` (debe mostrar dispositivo 28-xxxx del DS18B20)

### 8.3 Conexión Física de Sensores
- [ ] Conectar DS18B20 a GPIO 4 con resistencia pull-up de 4.7kΩ entre DATA y VCC (3.3V)
- [ ] Conectar DHT22 a GPIO 17 con resistencia pull-up de 10kΩ (si el módulo no la incluye)
- [ ] Conectar BH1750 a bus I2C (SDA → GPIO 2, SCL → GPIO 3), alimentar a 3.3V
- [ ] Conectar ADS1115 a bus I2C (SDA → GPIO 2, SCL → GPIO 3), dirección por defecto 0x48
- [ ] Conectar sensor de humedad de suelo al canal A0 del ADS1115
- [ ] Conectar MH-Z19C a UART (TX sensor → RX RPi GPIO 15, RX sensor → TX RPi GPIO 14), alimentar a 5V
- [ ] Verificar pinout con diagrama antes de encender (evitar daños)

### 8.4 Validación de Drivers con Hardware Real
- [ ] Cambiar configuración del gateway a `simulation=False`
- [ ] Instalar librerías de hardware: `pip install RPi.GPIO adafruit-circuitpython-dht adafruit-circuitpython-ads1x15 smbus2 pyserial`
- [ ] Completar implementación real en `ds18b20.py` — leer `/sys/bus/w1/devices/28-*/w1_slave`
- [ ] Completar implementación real en `dht22.py` — usar `adafruit_dht.DHT22(board.D17)`
- [ ] Completar implementación real en `bh1750.py` — leer registros I2C con `smbus2`
- [ ] Completar implementación real en `soil_moisture.py` — leer canal ADC vía `adafruit_ads1x15`
- [ ] Completar implementación real en `mhz19c.py` — enviar comando de lectura por UART y parsear respuesta
- [ ] Verificar cada sensor individualmente: ejecutar `python -c "from sensor_drivers.ds18b20 import DS18B20Driver; d=DS18B20Driver(); print(d.read())"`
- [ ] Comparar lecturas contra instrumentos de referencia (termómetro, higrómetro)

### 8.5 Calibración y Ajustes
- [ ] Calibrar DS18B20: verificar offset de temperatura vs termómetro de referencia
- [ ] Calibrar DHT22: verificar humedad vs higrómetro de referencia
- [ ] Calibrar BH1750: verificar lux vs luxómetro (o referencia solar conocida)
- [ ] Calibrar sensor de suelo: definir curva seco (0%) vs saturado (100%) con muestras reales
- [ ] Calibrar MH-Z19C: ejecutar autocalibración ABC o calibración manual a 400ppm (aire exterior)
- [ ] Ajustar intervalos de polling según estabilidad de lecturas
- [ ] Documentar offsets y factores de corrección en configuración

### 8.6 Testing de Integración con Hardware
- [ ] Ejecutar `sensor_manager.py` con los 5 sensores reales conectados
- [ ] Verificar que el polling lee todos los sensores sin errores durante 1 hora continua
- [ ] Verificar almacenamiento local en SQLite (lecturas persistidas correctamente)
- [ ] Verificar publicación MQTT (Mosquitto recibe los mensajes)
- [ ] Verificar sincronización con backend cloud (datos llegan al API)
- [ ] Verificar motor de alertas (generar condición de alerta real, ej: calentar sensor con mano)
- [ ] Medir consumo de CPU/RAM del Raspberry Pi bajo carga
- [ ] Configurar e iniciar servicio systemd (`echosmart-gateway.service`)
- [ ] Verificar que el gateway sobrevive reinicios y desconexiones de red
- [ ] Prueba de estrés: 24 horas continuas de operación con todos los sensores

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
