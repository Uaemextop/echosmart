# EchoSmart — Lista de Tareas de Desarrollo Multiplataforma

> Proyecto IoT de agricultura de precisión para monitoreo ambiental inteligente en invernaderos.

---

## 🏛️ Principios de Arquitectura y Clean Code

> ⚠️ **OBLIGATORIO**: Todas las fases de desarrollo DEBEN seguir estos principios. Cualquier PR que viole estos estándares será rechazado.

### Principio 1: Clean Architecture (Arquitectura Limpia)

El proyecto sigue **Clean Architecture** de Robert C. Martin. Las capas son:

```
┌─────────────────────────────────────────────┐
│  Capa Externa: Frameworks & Drivers         │
│  (FastAPI, React, Electron, RPi.GPIO)       │
│  ┌─────────────────────────────────────┐    │
│  │  Capa de Adaptadores (Interfaces)   │    │
│  │  (Routers, Controllers, Repos impl) │    │
│  │  ┌─────────────────────────────┐    │    │
│  │  │  Capa de Casos de Uso       │    │    │
│  │  │  (Services, Use Cases)      │    │    │
│  │  │  ┌─────────────────────┐    │    │    │
│  │  │  │  Entidades (Core)   │    │    │    │
│  │  │  │  (Models, Schemas)  │    │    │    │
│  │  │  └─────────────────────┘    │    │    │
│  │  └─────────────────────────────┘    │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

**Regla de Dependencia**: Las capas internas NUNCA importan de las capas externas. Las dependencias siempre apuntan hacia adentro.

- **Entidades**: Modelos de datos puros, sin dependencias externas. Lógica de negocio fundamental.
- **Casos de Uso (Services)**: Orquestan las entidades. No conocen el framework HTTP ni la base de datos.
- **Adaptadores**: Routers (HTTP), repositorios (DB), publishers (MQTT). Adaptan entrada/salida.
- **Frameworks**: FastAPI, SQLAlchemy, React, Electron. Detalles de implementación reemplazables.

### Principio 2: SOLID

| Principio | Aplicación en EchoSmart |
|-----------|------------------------|
| **S** — Single Responsibility | Cada archivo/clase tiene UNA sola razón para cambiar. `sensor_service.py` NO debe manejar alertas. |
| **O** — Open/Closed | Nuevos sensores se agregan creando un nuevo driver, SIN modificar `sensor_manager.py`. |
| **L** — Liskov Substitution | Todos los drivers de sensores implementan la misma interfaz `BaseSensorDriver`. Son intercambiables. |
| **I** — Interface Segregation | No forzar a un componente a depender de métodos que no usa. Interfaces pequeñas y específicas. |
| **D** — Dependency Inversion | Los servicios dependen de abstracciones (interfaces/protocolos), no de implementaciones concretas. |

### Principio 3: Clean Code (Código Limpio)

| Regla | Descripción |
|-------|-------------|
| **Nombres descriptivos** | Variables, funciones y clases con nombres que revelen su intención. `get_avg_temp_last_24h()` en vez de `getData()`. |
| **Funciones pequeñas** | Máximo 20–30 líneas por función. Si es más larga, refactorizar en subfunciones. |
| **Un nivel de abstracción** | Cada función opera en UN solo nivel de abstracción. No mezclar lógica de negocio con queries SQL. |
| **Sin comentarios obvios** | El código debe ser auto-documentado. Comentarios solo para el "por qué", no el "qué". |
| **Sin código muerto** | No dejar funciones, variables o imports sin usar. Eliminar TODO que no se vaya a hacer. |
| **Sin números mágicos** | Usar constantes con nombre: `MAX_TEMPERATURE = 45.0`, no `if temp > 45`. |
| **Manejo explícito de errores** | Nunca `except: pass`. Siempre capturar excepciones específicas y manejarlas. |
| **DRY (Don't Repeat Yourself)** | Si un bloque de código aparece 2+ veces, extraerlo a función/módulo reutilizable. |
| **KISS (Keep It Simple)** | La solución más simple que funcione. Sin sobre-ingeniería. |
| **YAGNI (You Aren't Gonna Need It)** | No implementar features que "tal vez se necesiten en el futuro". |

### Principio 4: Estructura de Archivos por Feature (No por Tipo)

```
# ❌ MAL — Agrupación por tipo (difícil de mantener)
backend/
  models/
    user.py, sensor.py, alert.py, gateway.py...
  routers/
    user.py, sensor.py, alert.py, gateway.py...
  services/
    user.py, sensor.py, alert.py, gateway.py...

# ✅ BIEN — Agrupación por feature (Clean Architecture)
backend/src/
  auth/
    models.py, router.py, service.py, schemas.py, tests/
  sensors/
    models.py, router.py, service.py, schemas.py, repository.py, tests/
  alerts/
    models.py, router.py, service.py, schemas.py, repository.py, tests/
  shared/
    database.py, config.py, exceptions.py, middleware/
```

> **Nota**: La estructura actual del proyecto agrupa por tipo (`models/`, `routers/`, `services/`). Las fases de desarrollo incluyen la **migración gradual** a estructura por feature como tarea prioritaria.

### Principio 5: Testing Pyramid

```
        ╱╲
       ╱  ╲       E2E Tests (pocos, lentos, costosos)
      ╱────╲      - Cypress/Playwright (web)
     ╱      ╲     - Detox (mobile)
    ╱────────╲
   ╱          ╲   Integration Tests (medianos)
  ╱────────────╲  - API tests con TestClient
 ╱              ╲ - DB tests con fixtures
╱────────────────╲
╱                  ╲ Unit Tests (muchos, rápidos, baratos)
╱────────────────────╲ - pytest (Python), Vitest (JS)
```

- **Cobertura mínima**: 80% en servicios y utilidades
- **Cada PR DEBE incluir tests** para el código nuevo/modificado
- **Tests primero**: Preferir TDD (Test-Driven Development) para lógica de negocio

### Principio 6: Convenciones de Código

| Aspecto | Python (Backend/Gateway) | JavaScript/TypeScript (Frontend/Mobile/Desktop) |
|---------|--------------------------|--------------------------------------------------|
| **Estilo** | PEP 8 + Black formatter | ESLint + Prettier |
| **Nombrado** | `snake_case` para funciones/variables, `PascalCase` para clases | `camelCase` para funciones/variables, `PascalCase` para componentes |
| **Imports** | Ordenados: stdlib → third-party → local | Ordenados: react → libs → components → utils |
| **Docstrings** | Google-style docstrings | JSDoc para funciones públicas |
| **Type hints** | Obligatorios en funciones públicas | TypeScript/JSDoc types |
| **Max line length** | 88 caracteres (Black) | 100 caracteres (Prettier) |
| **Commits** | Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:` | Conventional Commits |

### Principio 7: Patrones de Diseño Aplicados

| Patrón | Dónde se usa | Ejemplo |
|--------|-------------|---------|
| **Repository** | Backend — acceso a datos | `SensorRepository` encapsula queries SQL |
| **Service Layer** | Backend — lógica de negocio | `AlertService` orquesta detección y notificación |
| **Factory** | Gateway — creación de drivers | `SensorDriverFactory.create("ds18b20")` |
| **Observer** | Gateway/Frontend — eventos | Sensor Manager emite eventos, Alert Engine escucha |
| **Strategy** | Gateway — protocolos de comunicación | Diferentes estrategias para I2C, UART, GPIO |
| **Adapter** | Frontend — API calls | Adaptar respuesta HTTP a estado Redux |
| **Singleton** | Config — configuración global | Una sola instancia de `Config` por proceso |
| **Middleware** | Backend/Frontend — pipeline | Auth middleware, rate limiter, error handler |
| **DTO** | Backend — transferencia de datos | Pydantic schemas validan y transforman datos |

### Principio 8: Manejo de Errores

```python
# ❌ MAL — Silenciar errores
try:
    reading = sensor.read()
except:
    pass

# ✅ BIEN — Errores específicos con manejo apropiado
try:
    reading = sensor.read()
except SensorTimeoutError as e:
    logger.warning(f"Sensor {sensor.id} timeout: {e}")
    return SensorReading.empty(sensor.id, error="timeout")
except SensorDisconnectedError as e:
    logger.error(f"Sensor {sensor.id} disconnected: {e}")
    alert_engine.fire(AlertType.SENSOR_OFFLINE, sensor.id)
    raise
```

**Jerarquía de excepciones personalizadas**:
```
EchoSmartError (base)
├── SensorError
│   ├── SensorTimeoutError
│   ├── SensorDisconnectedError
│   └── SensorCalibrationError
├── AuthError
│   ├── InvalidCredentialsError
│   └── InsufficientPermissionsError
├── GatewayError
│   ├── GatewayOfflineError
│   └── GatewaySyncError
└── ValidationError
```

### Principio 9: Logging Estructurado

```python
# ❌ MAL — Print statements
print(f"Sensor leyó {value}")

# ✅ BIEN — Logging con contexto
import structlog
logger = structlog.get_logger()

logger.info("sensor_reading_received",
    sensor_id=sensor.id,
    sensor_type="ds18b20",
    value=25.3,
    unit="°C",
    gateway_id=gateway.id
)
```

- Usar `structlog` (Python) o `pino`/`winston` (Node.js) para logging estructurado
- Niveles: DEBUG (desarrollo), INFO (operaciones), WARNING (degradación), ERROR (fallos), CRITICAL (sistema down)
- NUNCA loguear datos sensibles (passwords, tokens, datos personales)

### Principio 10: Seguridad por Diseño

- Input validation en CADA endpoint (Pydantic schemas con validators)
- Sanitización de datos del usuario (prevenir SQL injection, XSS)
- HTTPS obligatorio en producción
- JWT con expiración corta (15 min access, 7d refresh)
- RBAC en cada endpoint (decoradores `@require_role("admin")`)
- Rate limiting por IP y por usuario
- CORS configurado explícitamente (no `allow_origins=["*"]` en producción)
- Secrets en variables de entorno, NUNCA en código fuente
- Dependencias actualizadas (Dependabot/Renovate)

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

### 1.2 Arquitectura del Gateway (Clean Architecture)

> 🏛️ El gateway sigue Clean Architecture con estas capas:

```
gateway/src/
├── domain/                     # Capa de dominio (entidades + interfaces)
│   ├── entities/               # Entidades puras
│   │   ├── sensor_reading.py   # SensorReading dataclass
│   │   ├── alert.py            # Alert entity
│   │   └── gateway_config.py   # GatewayConfig entity
│   ├── interfaces/             # Contratos (ABC)
│   │   ├── sensor_driver.py    # BaseSensorDriver ABC
│   │   ├── storage.py          # IStorageRepository ABC
│   │   ├── publisher.py        # IMessagePublisher ABC
│   │   └── sync_client.py      # ISyncClient ABC
│   └── constants.py            # Constantes del dominio
├── application/                # Casos de uso
│   ├── sensor_manager.py       # Orquesta lectura de sensores
│   ├── alert_engine.py         # Motor de alertas
│   └── cloud_sync.py           # Sincronización con cloud
├── infrastructure/             # Implementaciones concretas
│   ├── drivers/                # Drivers de sensores
│   │   ├── ds18b20.py
│   │   ├── dht22.py
│   │   ├── bh1750.py
│   │   ├── soil_moisture.py
│   │   └── mhz19c.py
│   ├── hal.py                  # Hardware Abstraction Layer
│   ├── sqlite_storage.py       # Implementación SQLite
│   ├── mqtt_publisher.py       # Implementación MQTT
│   ├── http_sync_client.py     # Implementación HTTP sync
│   └── discovery.py            # Descubrimiento SSDP
├── config.py                   # Configuración
├── main.py                     # Entry point
└── tests/                      # Tests unitarios e integración
```

- [ ] Crear directorio `domain/entities/` con dataclasses puras
  - [ ] `sensor_reading.py` — `SensorReading(sensor_id, sensor_type, value, unit, timestamp, is_valid)`
  - [ ] `alert.py` — `Alert(id, sensor_id, type, severity, message, threshold, value, created_at)`
  - [ ] `gateway_config.py` — `GatewayConfig(id, name, sensors, polling_interval, cloud_url)`
- [ ] Crear directorio `domain/interfaces/` con ABCs (Abstract Base Classes)
  - [ ] `sensor_driver.py` — `BaseSensorDriver(ABC)` con métodos `read()`, `initialize()`, `shutdown()`, `get_info()`
  - [ ] `storage.py` — `IStorageRepository(ABC)` con `save_reading()`, `get_readings()`, `get_unsynced()`
  - [ ] `publisher.py` — `IMessagePublisher(ABC)` con `publish()`, `connect()`, `disconnect()`
  - [ ] `sync_client.py` — `ISyncClient(ABC)` con `sync_readings()`, `sync_alerts()`, `register_gateway()`
- [ ] Crear `domain/constants.py` con constantes de negocio (rangos, umbrales, timeouts)
- [ ] Migrar `sensor_manager.py` a `application/sensor_manager.py` usando interfaces
- [ ] Migrar `alert_engine.py` a `application/alert_engine.py` usando interfaces
- [ ] Migrar `cloud_sync.py` a `application/cloud_sync.py` usando interfaces
- [ ] Migrar drivers existentes a `infrastructure/drivers/` implementando `BaseSensorDriver`
- [ ] Migrar `local_db.py` a `infrastructure/sqlite_storage.py` implementando `IStorageRepository`
- [ ] Migrar `mqtt_publisher.py` a `infrastructure/mqtt_publisher.py` implementando `IMessagePublisher`

### 1.3 Software del Gateway — Drivers de Sensores (Modo Simulación)

> 🖥️ **Todo el desarrollo de esta sección se realiza SIN hardware físico.** Los drivers operan en `simulation=True` por defecto, generando datos realistas para pruebas. La implementación de lectura real del hardware (GPIO, I2C, 1-Wire, UART) queda como `TODO` para completar en la Fase 8.

#### 1.3.1 Interfaz Base de Drivers (Clean Code: Polimorfismo)
- [ ] Crear `BaseSensorDriver(ABC)` con interfaz estándar:
  - [ ] Método `read() -> SensorReading` — Lectura del sensor (simulada o real)
  - [ ] Método `initialize() -> bool` — Inicialización del hardware/simulación
  - [ ] Método `shutdown() -> None` — Apagado limpio del sensor
  - [ ] Método `get_info() -> dict` — Metadatos del sensor (tipo, protocolo, estado)
  - [ ] Método `is_healthy() -> bool` — Health check del sensor
  - [ ] Método `calibrate(reference_value) -> None` — Calibración con valor de referencia
  - [ ] Propiedad `sensor_type: str` — Tipo de sensor (temperature, humidity, etc.)
  - [ ] Propiedad `protocol: str` — Protocolo (1-wire, gpio, i2c, uart)
  - [ ] Propiedad `is_simulation: bool` — Si está en modo simulación

#### 1.3.2 Driver Factory (Patrón Factory)
- [ ] Crear `SensorDriverFactory` en `infrastructure/driver_factory.py`
  - [ ] Método `create(sensor_type: str, config: dict) -> BaseSensorDriver`
  - [ ] Registro dinámico de drivers disponibles
  - [ ] Validación de configuración antes de crear instancia
  - [ ] Tests: factory crea el driver correcto para cada tipo

#### 1.3.3 Driver DS18B20 — Temperatura (1-Wire)
- [x] Implementar clase `DS18B20Driver(BaseSensorDriver)` con modo simulación
- [ ] Agregar validación de rangos: rechazar lecturas fuera de -55°C a +125°C
- [ ] Agregar filtro de outliers: descartar lecturas que varíen >5°C entre muestras consecutivas
- [ ] Agregar soporte para múltiples sensores DS18B20 en el mismo bus (por device_id)
- [ ] Agregar método `get_resolution()` / `set_resolution(bits: int)` — Configurar resolución 9-12 bits
- [ ] Implementar caché: no leer más de 1 vez por segundo (time-based debounce)
- [ ] Agregar retry con backoff exponencial en caso de error de lectura
- [ ] Agregar logging estructurado en cada operación
- [ ] Implementar `__repr__` y `__str__` descriptivos para debugging
- [ ] Tests unitarios: lectura válida, lectura fuera de rango, sensor desconectado, timeout, múltiples sensores

#### 1.3.4 Driver DHT22 — Temperatura + Humedad (GPIO)
- [x] Implementar clase `DHT22Driver(BaseSensorDriver)` con modo simulación
- [ ] Agregar validación de rangos: temp -40°C–80°C, humedad 0%–100%
- [ ] Agregar rate limiting: no leer más de 1 vez cada 2 segundos (limitación del sensor)
- [ ] Agregar checksum validation (CRC8) para verificar integridad de datos
- [ ] Agregar filtro de lecturas espurias: descartar si humedad = 0% o > 100%
- [ ] Agregar retry (máx 3 intentos) en caso de CRC error
- [ ] Devolver `SensorReading` con ambos valores: temperatura y humedad separados
- [ ] Agregar logging con nivel y timestamp
- [ ] Tests unitarios: lectura normal, CRC error, rate limit excedido, valores fuera de rango

#### 1.3.5 Driver BH1750 — Luminosidad (I2C)
- [x] Implementar clase `BH1750Driver(BaseSensorDriver)` con modo simulación
- [ ] Agregar modos de medición: `CONTINUOUS_HIGH_RES`, `CONTINUOUS_HIGH_RES2`, `ONE_TIME`
- [ ] Agregar configuración de dirección I2C (0x23 por defecto, 0x5C alternativa)
- [ ] Agregar validación: descartar lecturas > 65535 lux (overflow del sensor)
- [ ] Agregar suavizado: promedio móvil de las últimas N lecturas
- [ ] Implementar `power_on()` / `power_off()` para ahorro de energía
- [ ] Tests unitarios: lectura normal, cambio de modo, dirección I2C alternativa, power management

#### 1.3.6 Driver Soil Moisture + ADS1115 — Humedad de Suelo (ADC)
- [x] Implementar clase `SoilMoistureDriver(BaseSensorDriver)` con modo simulación
- [ ] Agregar calibración: mapear voltaje crudo a porcentaje (dry_value, wet_value)
- [ ] Agregar selección de canal ADC (A0-A3 del ADS1115)
- [ ] Agregar configuración de ganancia del ADS1115 (2/3, 1, 2, 4, 8, 16)
- [ ] Agregar filtro de ruido: mediana de 5 lecturas consecutivas
- [ ] Agregar validación: descartar si porcentaje < 0% o > 100%
- [ ] Implementar método `auto_calibrate(dry_reading, wet_reading)`
- [ ] Tests unitarios: calibración, canal correcto, rango de ganancia, filtro de mediana

#### 1.3.7 Driver MH-Z19C — CO₂ (UART)
- [x] Implementar clase `MHZ19CDriver(BaseSensorDriver)` con modo simulación
- [ ] Agregar envío de comando UART para lectura (9 bytes: 0xFF 0x01 0x86 ...)
- [ ] Agregar parsing de respuesta UART (extraer ppm de bytes 2-3)
- [ ] Agregar checksum validation en la respuesta
- [ ] Agregar comando de auto-calibración (ABC enable/disable)
- [ ] Agregar comando de calibración a punto cero (Zero Point Calibration)
- [ ] Agregar warmup tracking: ignorar lecturas durante los primeros 3 minutos
- [ ] Agregar timeout de comunicación UART (default: 5 segundos)
- [ ] Tests unitarios: lectura normal, checksum inválido, timeout, warmup, calibración

### 1.4 Hardware Abstraction Layer (HAL)

- [x] Implementar clase `HAL` con abstracción de hardware
- [ ] Refactorizar HAL como interfaz abstracta + implementaciones:
  - [ ] `IHardwareInterface(ABC)` — Interfaz abstracta
  - [ ] `SimulatedHAL(IHardwareInterface)` — Para desarrollo sin hardware
  - [ ] `RaspberryPiHAL(IHardwareInterface)` — Para hardware real (Fase 8)
- [ ] Agregar health check de bus I2C (`scan()` devuelve dispositivos detectados)
- [ ] Agregar health check de bus 1-Wire (`list_devices()` devuelve IDs)
- [ ] Agregar health check de UART (`ping()` verifica conexión serial)
- [ ] Agregar manejo de errores con excepciones específicas: `I2CError`, `GPIOError`, `UARTError`
- [ ] Implementar `__enter__` / `__exit__` para context managers (limpieza automática de GPIO)
- [ ] Tests: cada método del HAL simulado devuelve datos consistentes

### 1.5 Sensor Manager (Orquestador)

- [x] Implementar `SensorManager` con polling configurable
- [ ] Refactorizar para inyección de dependencias (recibir interfaces, no implementaciones)
- [ ] Implementar registro dinámico de sensores via configuración JSON
- [ ] Implementar polling asíncrono con `asyncio` (no bloquear entre lecturas)
- [ ] Implementar prioridad de sensores (los críticos se leen con más frecuencia)
- [ ] Implementar circuit breaker: deshabilitar sensor temporalmente si falla N veces seguidas
- [ ] Implementar métricas internas: lecturas/minuto, errores/minuto, latencia promedio
- [ ] Implementar graceful shutdown: detener polling y cerrar todos los drivers
- [ ] Implementar hot-reload de configuración (agregar/quitar sensores sin reiniciar)
- [ ] Agregar eventos/callbacks: `on_reading`, `on_error`, `on_sensor_offline`
- [ ] Tests: polling correcto, circuit breaker, graceful shutdown, hot-reload

### 1.6 Almacenamiento Local (SQLite)

- [x] Implementar `local_db.py` con SQLite
- [ ] Refactorizar como `SqliteStorageRepository` implementando `IStorageRepository`
- [ ] Diseñar esquema de tablas:
  - [ ] `readings(id, sensor_id, sensor_type, value, unit, timestamp, synced)`
  - [ ] `alerts(id, sensor_id, type, severity, message, timestamp, synced)`
  - [ ] `sync_log(id, batch_id, records_sent, records_failed, timestamp)`
- [ ] Implementar índices para queries frecuentes (por sensor_id, por timestamp, por synced)
- [ ] Implementar retención de datos: auto-delete lecturas mayores a 7 días (configurable)
- [ ] Implementar vacuum automático para compactar la base de datos
- [ ] Implementar método `get_unsynced_readings(limit=100)` para sincronización batch
- [ ] Implementar método `mark_as_synced(reading_ids)` después de sync exitosa
- [ ] Implementar método `get_stats()` — conteo de lecturas, espacio usado, lecturas pendientes
- [ ] Agregar WAL mode para evitar bloqueos en lectura/escritura concurrente
- [ ] Tests: CRUD, retención, vacuum, concurrencia, stats

### 1.7 Motor de Alertas Local

- [x] Implementar `alert_engine.py`
- [ ] Refactorizar para usar reglas configurables desde JSON/YAML
- [ ] Implementar tipos de reglas:
  - [ ] `ThresholdRule` — Valor excede umbral (ej: temp > 35°C)
  - [ ] `RangeRule` — Valor fuera de rango (ej: humedad < 40% o > 90%)
  - [ ] `RateOfChangeRule` — Cambio rápido (ej: temp sube >2°C en 5 min)
  - [ ] `StaleDataRule` — Sin datos por N minutos (sensor offline)
  - [ ] `CompoundRule` — Combinación de reglas (ej: temp alta Y humedad baja)
- [ ] Implementar severidades: `INFO`, `WARNING`, `CRITICAL`
- [ ] Implementar cooldown: no repetir la misma alerta en N minutos
- [ ] Implementar escalamiento: si alerta no se atiende en N min, subir severidad
- [ ] Implementar acciones locales: log, LED indicador (GPIO), buzzer
- [ ] Implementar historial de alertas en SQLite
- [ ] Tests: cada tipo de regla, cooldown, escalamiento, persistencia

### 1.8 Comunicaciones (MQTT + Sync)

- [x] Implementar `mqtt_publisher.py`
- [x] Implementar `cloud_sync.py`
- [ ] Refactorizar MQTT publisher como `MqttPublisher(IMessagePublisher)`
- [ ] Implementar reconexión automática MQTT con backoff exponencial
- [ ] Implementar Quality of Service (QoS) configurable: 0 (at most once), 1 (at least once), 2 (exactly once)
- [ ] Implementar topics MQTT estructurados: `echosmart/{gateway_id}/sensors/{sensor_type}/reading`
- [ ] Implementar payload JSON estandarizado con schema versioning
- [ ] Implementar Last Will and Testament (LWT) para detectar gateway offline
- [ ] Implementar TLS/SSL para comunicación MQTT segura
- [ ] Refactorizar cloud_sync como `HttpSyncClient(ISyncClient)`
- [ ] Implementar batch sync: enviar N lecturas por request (reducir llamadas HTTP)
- [ ] Implementar retry con backoff exponencial y jitter
- [ ] Implementar offline queue: almacenar datos en SQLite si no hay conexión
- [ ] Implementar compresión gzip para payloads grandes
- [ ] Implementar health check endpoint: verificar conectividad con cloud
- [ ] Tests: reconexión MQTT, batch sync, offline queue, retry, compresión

### 1.9 Auto-descubrimiento y Configuración

- [x] Implementar `discovery.py` con SSDP
- [ ] Implementar mDNS/Zeroconf como alternativa a SSDP
- [ ] Implementar API REST local en el gateway (Flask/FastAPI ligero, puerto 8080)
  - [ ] `GET /api/status` — Estado del gateway y sensores
  - [ ] `GET /api/readings` — Últimas lecturas de cada sensor
  - [ ] `GET /api/config` — Configuración actual
  - [ ] `POST /api/config` — Actualizar configuración
  - [ ] `POST /api/restart` — Reiniciar sensor manager
- [ ] Implementar identificación del gateway (hostname, MAC, serial number)
- [ ] Tests: descubrimiento, API local, actualización de config

### 1.10 Gateway — Tests Completos

- [x] Tests básicos unitarios
- [ ] Tests para CADA driver individual con mocking del HAL
- [ ] Tests para SensorManager con drivers mockeados
- [ ] Tests para AlertEngine con reglas predefinidas
- [ ] Tests para SqliteStorage (CRUD, retención, concurrencia)
- [ ] Tests para MqttPublisher con broker mockeado
- [ ] Tests para CloudSync con HTTP mockeado (responses library)
- [ ] Tests de integración: flujo completo sensor → storage → mqtt → sync
- [ ] Tests de configuración: carga de JSON, validación, defaults
- [ ] Tests de error handling: sensor offline, DB corrupta, red caída
- [ ] Verificar cobertura ≥ 80% con `pytest --cov`
- [ ] Configurar `pytest.ini` con markers y configuración de test

### 1.11 Gateway — Calidad de Código

- [ ] Configurar `black` para formateo automático
- [ ] Configurar `isort` para ordenar imports
- [ ] Configurar `flake8` o `ruff` para linting
- [ ] Configurar `mypy` para type checking
- [ ] Agregar `pre-commit` hooks: black + isort + flake8 + mypy
- [ ] Agregar type hints a TODAS las funciones públicas
- [ ] Agregar docstrings Google-style a TODAS las clases y funciones públicas
- [ ] Crear `gateway/README.md` con instrucciones de desarrollo y testing
- [ ] Crear `gateway/Makefile` con targets: `lint`, `format`, `test`, `coverage`, `run`

---

## Fase 2: Backend Cloud (Semanas 4–7)

> 🏛️ **Clean Architecture**: El backend sigue estrictamente la separación en capas. Los routers (HTTP) solo llaman servicios. Los servicios contienen la lógica de negocio. Los repositorios encapsulan el acceso a datos. Los modelos son entidades puras.

### 2.1 Refactorización a Clean Architecture

> La estructura actual agrupa por tipo (`models/`, `routers/`, `services/`). Migrar a estructura por feature.

- [ ] Planificar la migración: documentar el mapa de archivos actual → nuevo
- [ ] Crear estructura por feature:
  ```
  backend/src/
  ├── auth/
  │   ├── __init__.py
  │   ├── models.py          # User, Token entities
  │   ├── schemas.py          # LoginRequest, TokenResponse
  │   ├── router.py           # /api/v1/auth/* endpoints
  │   ├── service.py          # AuthService (lógica de negocio)
  │   ├── repository.py       # UserRepository (acceso a DB)
  │   ├── dependencies.py     # get_current_user, require_role
  │   ├── exceptions.py       # InvalidCredentials, TokenExpired
  │   └── tests/
  │       ├── test_service.py
  │       ├── test_router.py
  │       └── test_repository.py
  ├── sensors/
  │   ├── models.py, schemas.py, router.py, service.py, repository.py
  │   └── tests/
  ├── gateways/
  │   ├── models.py, schemas.py, router.py, service.py, repository.py
  │   └── tests/
  ├── alerts/
  │   ├── models.py, schemas.py, router.py, service.py, repository.py
  │   └── tests/
  ├── reports/
  │   ├── models.py, schemas.py, router.py, service.py, repository.py
  │   └── tests/
  ├── tenants/
  │   ├── models.py, schemas.py, router.py, service.py, repository.py
  │   └── tests/
  ├── users/
  │   ├── models.py, schemas.py, router.py, service.py, repository.py
  │   └── tests/
  ├── notifications/
  │   ├── service.py, schemas.py
  │   └── tests/
  ├── shared/
  │   ├── database.py         # DB connection, session factory
  │   ├── config.py           # Settings (pydantic-settings)
  │   ├── exceptions.py       # Base exceptions
  │   ├── middleware/          # Auth, tenant, rate limit
  │   ├── pagination.py       # Pagination utilities
  │   ├── responses.py        # Standard API responses
  │   └── security.py         # Password hashing, JWT
  └── main.py                 # FastAPI app factory
  ```
- [ ] Migrar `models/user.py` → `auth/models.py` + `users/models.py`
- [ ] Migrar `models/sensor.py` → `sensors/models.py`
- [ ] Migrar `models/gateway.py` → `gateways/models.py`
- [ ] Migrar `models/alert.py` → `alerts/models.py`
- [ ] Migrar `models/report.py` → `reports/models.py`
- [ ] Migrar `models/reading.py` → `sensors/models.py` (junto con Sensor)
- [ ] Migrar `models/tenant.py` → `tenants/models.py`
- [ ] Migrar cada router a su feature correspondiente
- [ ] Migrar cada service a su feature correspondiente
- [ ] Migrar cada schema a su feature correspondiente
- [ ] Crear repositorios para cada feature (nueva capa de abstracción)
- [ ] Actualizar imports en toda la aplicación
- [ ] Verificar que TODOS los tests pasan después de la migración

### 2.2 Infraestructura de Base de Datos

- [ ] Provisionar servidor cloud (AWS EC2 / DigitalOcean / Railway)
- [ ] Instalar y configurar PostgreSQL 14+
  - [ ] Crear base de datos `echosmart_prod` y `echosmart_test`
  - [ ] Configurar usuario con permisos mínimos necesarios
  - [ ] Configurar SSL para conexiones remotas
  - [ ] Configurar backups automatizados (pg_dump cron)
  - [ ] Configurar connection pooling (pgbouncer)
- [ ] Instalar y configurar InfluxDB 2.7+
  - [ ] Crear bucket `sensor_readings` con retención 365 días
  - [ ] Crear bucket `sensor_readings_downsampled` con retención indefinida
  - [ ] Configurar continuous queries para downsampling (1h, 1d promedios)
  - [ ] Crear API token con permisos de lectura/escritura
- [ ] Instalar y configurar Redis 7+
  - [ ] Configurar para cache (TTL 5 min por defecto)
  - [ ] Configurar para rate limiting (sliding window)
  - [ ] Configurar para sesiones (si se usa)
  - [ ] Configurar persistencia (RDB + AOF)
  - [ ] Configurar maxmemory y eviction policy (allkeys-lru)
- [x] Configurar Docker y docker-compose para desarrollo
- [ ] Crear `docker-compose.dev.yml` con hot-reload
- [ ] Crear `docker-compose.test.yml` para CI

### 2.3 Modelos y Base de Datos (SQLAlchemy + Alembic)

- [x] Implementar modelos ORM básicos
- [ ] Refactorizar modelos con Clean Code:
  - [ ] Agregar docstrings a todos los modelos
  - [ ] Agregar `__repr__` descriptivo a todos los modelos
  - [ ] Agregar validación a nivel de modelo (CheckConstraints)
  - [ ] Agregar índices compuestos para queries frecuentes
  - [ ] Agregar soft delete (campo `deleted_at`) en vez de `DELETE` físico
  - [ ] Agregar campos de auditoría: `created_by`, `updated_by`
- [ ] Modelo `User`:
  - [ ] Campos: id (UUID), email (unique), hashed_password, full_name, role, tenant_id, is_active, created_at, updated_at, last_login, deleted_at
  - [ ] Roles: admin, operator, viewer (Enum)
  - [ ] Relación: User → Tenant (many-to-one)
  - [ ] Índice: (email), (tenant_id, role)
- [ ] Modelo `Tenant`:
  - [ ] Campos: id (UUID), name, slug (unique), plan, max_gateways, max_users, settings (JSONB), created_at
  - [ ] Relación: Tenant → Users (one-to-many), Tenant → Gateways (one-to-many)
- [ ] Modelo `Gateway`:
  - [ ] Campos: id (UUID), name, serial_number (unique), tenant_id, firmware_version, last_seen, status (online/offline/maintenance), ip_address, location, created_at
  - [ ] Relación: Gateway → Sensors (one-to-many), Gateway → Tenant (many-to-one)
  - [ ] Índice: (tenant_id, status), (serial_number)
- [ ] Modelo `Sensor`:
  - [ ] Campos: id (UUID), name, sensor_type (Enum), protocol, gateway_id, pin_config (JSONB), calibration (JSONB), is_active, min_value, max_value, unit, created_at
  - [ ] Relación: Sensor → Gateway (many-to-one), Sensor → Readings (one-to-many)
  - [ ] Índice: (gateway_id, sensor_type), (gateway_id, is_active)
- [ ] Modelo `Reading`:
  - [ ] Campos: id (bigint), sensor_id, value (float), unit, quality (good/suspect/bad), timestamp, gateway_received_at, cloud_received_at
  - [ ] Particionamiento por fecha (si PostgreSQL soporta)
  - [ ] Índice: (sensor_id, timestamp DESC), (timestamp)
- [ ] Modelo `Alert`:
  - [ ] Campos: id (UUID), sensor_id, gateway_id, tenant_id, type, severity (info/warning/critical), message, threshold_value, actual_value, rule_id, acknowledged, acknowledged_by, acknowledged_at, resolved, resolved_at, created_at
  - [ ] Índice: (tenant_id, severity, resolved), (sensor_id, created_at DESC)
- [ ] Modelo `AlertRule`:
  - [ ] Campos: id (UUID), tenant_id, sensor_type, rule_type (threshold/range/rate/stale), config (JSONB), is_active, cooldown_minutes, created_by, created_at
- [ ] Modelo `Report`:
  - [ ] Campos: id (UUID), tenant_id, title, type (daily/weekly/monthly/custom), date_from, date_to, format (pdf/excel/csv), file_path, status (pending/generating/completed/failed), created_by, created_at
- [ ] Configurar Alembic para migraciones:
  - [ ] `alembic init` con configuración de PostgreSQL
  - [ ] Crear migración inicial con todos los modelos
  - [ ] Crear seed de datos iniciales (admin user, default tenant)
  - [ ] Documentar proceso de migración en README

### 2.4 Repositorios (Patrón Repository)

> 🏛️ Los repositorios encapsulan TODO el acceso a datos. Los servicios NUNCA usan `session.query()` directamente.

- [ ] Crear `BaseRepository(Generic[T])` con operaciones CRUD genéricas:
  - [ ] `get_by_id(id) -> T | None`
  - [ ] `get_all(filters, pagination) -> list[T]`
  - [ ] `create(data) -> T`
  - [ ] `update(id, data) -> T`
  - [ ] `soft_delete(id) -> bool`
  - [ ] `count(filters) -> int`
  - [ ] `exists(filters) -> bool`
- [ ] `UserRepository(BaseRepository[User])`:
  - [ ] `get_by_email(email) -> User | None`
  - [ ] `get_by_tenant(tenant_id, role=None) -> list[User]`
  - [ ] `update_last_login(user_id) -> None`
- [ ] `SensorRepository(BaseRepository[Sensor])`:
  - [ ] `get_by_gateway(gateway_id) -> list[Sensor]`
  - [ ] `get_active_by_tenant(tenant_id) -> list[Sensor]`
  - [ ] `get_with_latest_reading(sensor_id) -> SensorWithReading`
- [ ] `ReadingRepository`:
  - [ ] `bulk_insert(readings: list[Reading]) -> int`
  - [ ] `get_by_sensor(sensor_id, date_from, date_to, limit) -> list[Reading]`
  - [ ] `get_aggregated(sensor_id, interval, aggregation, date_from, date_to)` — AVG, MIN, MAX, COUNT
  - [ ] `get_latest_by_gateway(gateway_id) -> dict[sensor_id, Reading]`
- [ ] `GatewayRepository(BaseRepository[Gateway])`:
  - [ ] `get_by_serial(serial_number) -> Gateway | None`
  - [ ] `get_by_tenant(tenant_id) -> list[Gateway]`
  - [ ] `update_last_seen(gateway_id) -> None`
  - [ ] `get_offline(threshold_minutes=5) -> list[Gateway]`
- [ ] `AlertRepository(BaseRepository[Alert])`:
  - [ ] `get_active_by_tenant(tenant_id, severity=None) -> list[Alert]`
  - [ ] `get_unacknowledged(tenant_id) -> list[Alert]`
  - [ ] `acknowledge(alert_id, user_id) -> Alert`
  - [ ] `resolve(alert_id) -> Alert`
  - [ ] `get_stats_by_tenant(tenant_id, days=30) -> AlertStats`
- [ ] `AlertRuleRepository(BaseRepository[AlertRule])`:
  - [ ] `get_active_by_sensor_type(tenant_id, sensor_type) -> list[AlertRule]`
- [ ] `ReportRepository(BaseRepository[Report])`:
  - [ ] `get_by_tenant(tenant_id, status=None) -> list[Report]`
- [ ] `TenantRepository(BaseRepository[Tenant])`:
  - [ ] `get_by_slug(slug) -> Tenant | None`
  - [ ] `get_usage_stats(tenant_id) -> TenantUsage`
- [ ] Tests para CADA repositorio (CRUD + métodos custom)

### 2.5 Schemas Pydantic (Validación y DTOs)

> 🏛️ Schemas Pydantic v2 para validación de entrada, serialización de salida y documentación automática de OpenAPI.

- [x] Schemas básicos implementados
- [ ] Refactorizar schemas con patrón Request/Response:
  - [ ] `SensorCreate` (input) vs `SensorResponse` (output) vs `SensorUpdate` (partial)
  - [ ] `ReadingCreate` vs `ReadingResponse` vs `ReadingAggregated`
  - [ ] `AlertCreate` vs `AlertResponse` vs `AlertAcknowledge`
  - [ ] `UserCreate` vs `UserResponse` vs `UserUpdate`
  - [ ] `GatewayCreate` vs `GatewayResponse` vs `GatewayUpdate`
  - [ ] `ReportCreate` vs `ReportResponse`
  - [ ] `TenantCreate` vs `TenantResponse`
- [ ] Agregar validadores personalizados:
  - [ ] Email format validation
  - [ ] Password strength validation (min 8 chars, uppercase, lowercase, number)
  - [ ] Sensor value range validation (por tipo de sensor)
  - [ ] Date range validation (date_from < date_to)
  - [ ] UUID format validation
- [ ] Agregar schemas de paginación:
  - [ ] `PaginationParams(page, per_page, sort_by, sort_order)`
  - [ ] `PaginatedResponse(items, total, page, per_page, pages)`
- [ ] Agregar schemas de error estándar:
  - [ ] `ErrorResponse(detail, code, timestamp)`
  - [ ] `ValidationErrorResponse(detail, errors[])`
- [ ] Agregar `model_config` con `json_schema_extra` para ejemplos en OpenAPI docs

### 2.6 Servicios de Negocio (Casos de Uso)

> 🏛️ Los servicios contienen TODA la lógica de negocio. No conocen HTTP ni la base de datos directamente (usan repositorios).

- [x] Servicios básicos implementados
- [ ] **AuthService** — Autenticación y autorización:
  - [ ] `register(email, password, full_name, tenant_id) -> User`
  - [ ] `login(email, password) -> TokenPair` (access + refresh)
  - [ ] `refresh_token(refresh_token) -> TokenPair`
  - [ ] `logout(user_id) -> None` (invalidar refresh token en Redis)
  - [ ] `change_password(user_id, old_password, new_password) -> None`
  - [ ] `reset_password_request(email) -> None` (enviar email con token)
  - [ ] `reset_password_confirm(token, new_password) -> None`
  - [ ] `verify_token(token) -> UserClaims`
  - [ ] Implementar password hashing con bcrypt (cost factor 12)
  - [ ] Implementar JWT con RS256 (claves asimétricas) o HS256
  - [ ] Implementar token blacklist en Redis
  - [ ] Tests: registro, login, refresh, logout, password reset, token expirado
- [ ] **SensorService** — Gestión de sensores y lecturas:
  - [ ] `create_sensor(data, gateway_id) -> Sensor`
  - [ ] `update_sensor(sensor_id, data) -> Sensor`
  - [ ] `delete_sensor(sensor_id) -> None` (soft delete)
  - [ ] `get_sensor_with_status(sensor_id) -> SensorWithStatus`
  - [ ] `get_readings(sensor_id, date_from, date_to, interval) -> list[Reading]`
  - [ ] `get_aggregated_readings(sensor_id, interval, aggregation) -> AggregatedData`
  - [ ] `ingest_readings(gateway_id, readings[]) -> int` (bulk insert optimizado)
  - [ ] `get_dashboard_data(tenant_id) -> DashboardData` (métricas resumen)
  - [ ] `detect_anomalies(sensor_id, readings) -> list[Anomaly]`
  - [ ] Implementar caché de lecturas recientes en Redis (TTL 30s)
  - [ ] Tests: CRUD, ingesta batch, agregaciones, caché, anomalías
- [ ] **AlertService** — Motor de alertas cloud:
  - [ ] `create_rule(tenant_id, rule_data) -> AlertRule`
  - [ ] `evaluate_readings(gateway_id, readings[]) -> list[Alert]`
  - [ ] `acknowledge_alert(alert_id, user_id) -> Alert`
  - [ ] `resolve_alert(alert_id) -> Alert`
  - [ ] `get_active_alerts(tenant_id) -> list[Alert]`
  - [ ] `get_alert_stats(tenant_id, days=30) -> AlertStats`
  - [ ] Implementar cooldown: no duplicar alertas en ventana de tiempo
  - [ ] Implementar escalamiento: escalar si no se atiende en N min
  - [ ] Tests: evaluación de reglas, cooldown, escalamiento, acknowledgment
- [ ] **ReportService** — Generación de reportes:
  - [ ] `generate_report(tenant_id, type, date_from, date_to, format) -> Report`
  - [ ] `get_report_data(report_id) -> ReportData`
  - [ ] `generate_pdf(report_data) -> bytes` (usando reportlab o weasyprint)
  - [ ] `generate_excel(report_data) -> bytes` (usando openpyxl)
  - [ ] `generate_csv(report_data) -> bytes`
  - [ ] Implementar generación asíncrona con Celery/background task
  - [ ] Tests: generación de cada formato, datos vacíos, rango de fechas
- [ ] **NotificationService** — Envío de notificaciones:
  - [ ] `send_email(to, subject, body, template=None) -> bool`
  - [ ] `send_push(user_id, title, body, data=None) -> bool`
  - [ ] `send_webhook(url, payload) -> bool`
  - [ ] `notify_alert(alert, users) -> None` (enviar por todos los canales configurados)
  - [ ] Implementar templates de email (Jinja2)
  - [ ] Implementar cola de notificaciones (no bloquear API)
  - [ ] Tests: envío de cada tipo, template rendering, cola
- [ ] **SyncService** — Sincronización gateway ↔ cloud:
  - [ ] `ingest_batch(gateway_id, readings[], alerts[]) -> SyncResult`
  - [ ] `get_pending_config(gateway_id) -> GatewayConfig | None`
  - [ ] `update_gateway_status(gateway_id, status_data) -> None`
  - [ ] Implementar deduplicación de lecturas (por sensor_id + timestamp)
  - [ ] Implementar validación de datos entrantes (rechazar datos corruptos)
  - [ ] Tests: ingesta batch, deduplicación, validación
- [ ] **TenantService** — Gestión multi-tenant:
  - [ ] `create_tenant(data) -> Tenant`
  - [ ] `get_usage(tenant_id) -> TenantUsage` (gateways, sensors, readings, users)
  - [ ] `check_limits(tenant_id, resource) -> bool` (verificar plan)
  - [ ] Implementar aislamiento de datos por tenant_id en TODAS las queries
  - [ ] Tests: creación, límites, aislamiento

### 2.7 Routers REST (Controladores HTTP)

> 🏛️ Los routers son FINOS. Solo: 1) Parsear request, 2) Llamar servicio, 3) Devolver response. Sin lógica de negocio.

- [x] Routers básicos implementados
- [ ] **Auth Router** (`/api/v1/auth`):
  - [ ] `POST /register` — Registro de usuario
  - [ ] `POST /login` — Login con email/password
  - [ ] `POST /refresh` — Renovar access token
  - [ ] `POST /logout` — Invalidar tokens
  - [ ] `POST /forgot-password` — Solicitar reset
  - [ ] `POST /reset-password` — Confirmar reset con token
  - [ ] `GET /me` — Perfil del usuario autenticado
  - [ ] `PUT /me` — Actualizar perfil propio
  - [ ] `PUT /me/password` — Cambiar contraseña
- [ ] **Sensors Router** (`/api/v1/sensors`):
  - [ ] `GET /` — Listar sensores (con filtros, paginación, búsqueda)
  - [ ] `POST /` — Crear sensor
  - [ ] `GET /{id}` — Obtener sensor por ID (con última lectura)
  - [ ] `PUT /{id}` — Actualizar sensor
  - [ ] `DELETE /{id}` — Eliminar sensor (soft delete)
  - [ ] `GET /{id}/readings` — Lecturas con filtros de fecha y agregación
  - [ ] `GET /{id}/readings/latest` — Última lectura
  - [ ] `GET /{id}/readings/stats` — Estadísticas (min, max, avg, count)
  - [ ] `POST /{id}/calibrate` — Enviar calibración al gateway
- [ ] **Gateways Router** (`/api/v1/gateways`):
  - [ ] `GET /` — Listar gateways
  - [ ] `POST /` — Registrar gateway
  - [ ] `GET /{id}` — Detalle de gateway (con sensores y estado)
  - [ ] `PUT /{id}` — Actualizar gateway
  - [ ] `DELETE /{id}` — Eliminar gateway
  - [ ] `GET /{id}/sensors` — Sensores del gateway
  - [ ] `POST /{id}/sync` — Recibir datos sincronizados del gateway
  - [ ] `GET /{id}/status` — Estado de salud del gateway
  - [ ] `POST /{id}/restart` — Reiniciar gateway remotamente
  - [ ] `PUT /{id}/config` — Actualizar configuración remota
- [ ] **Alerts Router** (`/api/v1/alerts`):
  - [ ] `GET /` — Listar alertas (filtros: severity, status, sensor, date)
  - [ ] `GET /{id}` — Detalle de alerta
  - [ ] `POST /{id}/acknowledge` — Reconocer alerta
  - [ ] `POST /{id}/resolve` — Resolver alerta
  - [ ] `GET /stats` — Estadísticas de alertas (por severidad, por sensor, timeline)
  - [ ] `GET /rules` — Listar reglas de alerta
  - [ ] `POST /rules` — Crear regla
  - [ ] `PUT /rules/{id}` — Actualizar regla
  - [ ] `DELETE /rules/{id}` — Eliminar regla
- [ ] **Reports Router** (`/api/v1/reports`):
  - [ ] `GET /` — Listar reportes generados
  - [ ] `POST /` — Solicitar generación de reporte
  - [ ] `GET /{id}` — Estado del reporte
  - [ ] `GET /{id}/download` — Descargar archivo (PDF/Excel/CSV)
  - [ ] `DELETE /{id}` — Eliminar reporte
- [ ] **Users Router** (`/api/v1/users`) — Solo admin:
  - [ ] `GET /` — Listar usuarios del tenant
  - [ ] `POST /` — Crear usuario (invitar)
  - [ ] `GET /{id}` — Detalle de usuario
  - [ ] `PUT /{id}` — Actualizar usuario
  - [ ] `DELETE /{id}` — Desactivar usuario
  - [ ] `PUT /{id}/role` — Cambiar rol
- [ ] **Tenants Router** (`/api/v1/tenants`) — Solo superadmin:
  - [ ] `GET /` — Listar tenants
  - [ ] `POST /` — Crear tenant
  - [ ] `GET /{id}` — Detalle de tenant (con estadísticas de uso)
  - [ ] `PUT /{id}` — Actualizar tenant
  - [ ] `GET /{id}/usage` — Estadísticas de uso
- [ ] **Dashboard Router** (`/api/v1/dashboard`):
  - [ ] `GET /summary` — Resumen: conteos, última lectura por tipo, alertas activas
  - [ ] `GET /charts/readings` — Datos para gráficas de lecturas (24h/7d/30d)
  - [ ] `GET /charts/alerts` — Timeline de alertas
  - [ ] `GET /map` — Datos geoespaciales de sensores/gateways
- [ ] Agregar dependency injection en cada router (servicio como dependencia)
- [ ] Agregar respuestas estándar: `200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `422`, `500`
- [ ] Agregar documentación OpenAPI (descriptions, examples, tags)

### 2.8 Middleware y Seguridad

- [x] Middlewares básicos implementados
- [ ] **Auth Middleware**:
  - [ ] Validar JWT en header `Authorization: Bearer <token>`
  - [ ] Extraer `user_id`, `tenant_id`, `role` del token
  - [ ] Inyectar `current_user` en request state
  - [ ] Retornar 401 con detalle específico (expired, invalid, missing)
- [ ] **Tenant Middleware**:
  - [ ] Inyectar `tenant_id` del usuario autenticado en todas las queries
  - [ ] Verificar que el recurso pertenece al tenant del usuario
  - [ ] Retornar 403 si intenta acceder a recursos de otro tenant
- [ ] **Rate Limiting**:
  - [ ] Rate limit por IP: 100 requests/min (general)
  - [ ] Rate limit por usuario: 1000 requests/min
  - [ ] Rate limit por endpoint: 10/min para login, 5/min para password reset
  - [ ] Implementar con Redis (sliding window algorithm)
  - [ ] Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] **CORS Middleware**:
  - [ ] Configurar orígenes permitidos por entorno (dev: *, prod: dominio específico)
  - [ ] Configurar métodos y headers permitidos
- [ ] **Error Handler Middleware**:
  - [ ] Capturar excepciones no manejadas
  - [ ] Convertir a respuesta JSON estándar
  - [ ] Loggear con stack trace (solo en server, no al cliente)
  - [ ] Retornar error genérico en producción (no exponer internals)
- [ ] **Request Logging Middleware**:
  - [ ] Loggear method, path, status_code, duration, user_id
  - [ ] No loggear bodies sensibles (passwords, tokens)
- [ ] **Compression Middleware**: Gzip para responses > 1KB

### 2.9 WebSocket para Tiempo Real

- [x] WebSocket básico implementado
- [ ] Implementar WebSocket Manager:
  - [ ] `connect(websocket, user_id, tenant_id)` — Registrar conexión
  - [ ] `disconnect(websocket)` — Limpiar conexión
  - [ ] `broadcast_to_tenant(tenant_id, message)` — Enviar a todo el tenant
  - [ ] `send_to_user(user_id, message)` — Enviar a usuario específico
- [ ] Implementar canales WebSocket:
  - [ ] `/ws/readings` — Stream de lecturas en tiempo real
  - [ ] `/ws/alerts` — Alertas en tiempo real
  - [ ] `/ws/gateway-status` — Estado de gateways
- [ ] Implementar autenticación en WebSocket (token en query param o first message)
- [ ] Implementar heartbeat/ping-pong para detectar desconexiones
- [ ] Implementar reconnection logic del lado del servidor
- [ ] Tests: conexión, desconexión, broadcast, autenticación

### 2.10 Workers Asíncronos

- [x] Workers básicos implementados
- [ ] Implementar **AlertWorker**:
  - [ ] Consumir lecturas de cola (Redis/Celery)
  - [ ] Evaluar reglas de alerta
  - [ ] Crear alertas y enviar notificaciones
  - [ ] Ejecutar cada 10 segundos o por evento
- [ ] Implementar **ReportWorker**:
  - [ ] Consumir solicitudes de generación de reportes
  - [ ] Generar archivo PDF/Excel
  - [ ] Guardar en storage (local/S3)
  - [ ] Actualizar estado del reporte en DB
- [ ] Implementar **CleanupWorker**:
  - [ ] Ejecutar diariamente
  - [ ] Eliminar lecturas antiguas según política de retención
  - [ ] Eliminar reportes expirados
  - [ ] Limpiar tokens expirados de Redis
- [ ] Implementar **GatewayHealthWorker**:
  - [ ] Ejecutar cada minuto
  - [ ] Detectar gateways que no han reportado en N minutos
  - [ ] Marcar como offline y generar alerta

### 2.11 Backend — Tests Completos

- [x] Tests básicos
- [ ] Tests unitarios para CADA servicio (mocking repositorios)
- [ ] Tests unitarios para CADA repositorio (SQLite in-memory)
- [ ] Tests de integración para CADA endpoint (TestClient + DB real)
- [ ] Tests de autenticación: login, token refresh, permisos por rol
- [ ] Tests de tenant isolation: verificar que un tenant no ve datos de otro
- [ ] Tests de rate limiting: verificar límites se aplican correctamente
- [ ] Tests de WebSocket: conexión, mensajes, desconexión
- [ ] Tests de edge cases: datos vacíos, IDs inexistentes, duplicados
- [ ] Tests de concurrencia: requests simultáneos al mismo recurso
- [ ] Configurar `conftest.py` con fixtures: db_session, test_user, test_tenant, auth_headers
- [ ] Verificar cobertura ≥ 80% con `pytest --cov`
- [ ] Configurar `pytest.ini` con markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`

### 2.12 Backend — Calidad de Código

- [ ] Configurar `black` (formatter)
- [ ] Configurar `isort` (imports)
- [ ] Configurar `ruff` o `flake8` (linter)
- [ ] Configurar `mypy` (type checker) con strict mode
- [ ] Configurar `bandit` (security scanner)
- [ ] Configurar `pre-commit` hooks
- [ ] Agregar type hints a TODAS las funciones y métodos públicos
- [ ] Agregar docstrings Google-style a todas las clases y funciones públicas
- [ ] Crear `backend/README.md` con guía de desarrollo
- [ ] Crear `backend/Makefile` con targets: `install`, `lint`, `format`, `test`, `migrate`, `run`, `docker`
- [ ] Configurar Alembic autogenerate para detectar cambios en modelos

---

## Fase 3: Frontend Web — React (Semanas 8–10)

> 🏛️ **Clean Architecture en Frontend**: Separar UI (componentes) de lógica de negocio (hooks/store) y acceso a datos (API client). Los componentes NO deben hacer fetch directamente.

### 3.1 Configuración del Proyecto y Tooling

- [x] Inicializar proyecto React 18 con Vite en `frontend/`
- [x] Configurar Redux Toolkit, React Router, i18n
- [ ] Configurar Tailwind CSS con design tokens de EchoSmart:
  - [ ] Colores: bg-black (#000), surface (#111), elevated (#1A1A1A), accent-green (#00E676), accent-cyan (#00BCD4)
  - [ ] Tipografía: Inter (UI) / JetBrains Mono (datos/código)
  - [ ] Spacing scale, border radius, shadows
  - [ ] Dark mode como default (no toggle necesario)
- [x] Configurar cliente HTTP (Axios) con JWT
- [ ] Configurar ESLint con reglas estrictas:
  - [ ] `eslint-plugin-react` — Reglas de React
  - [ ] `eslint-plugin-react-hooks` — Reglas de hooks
  - [ ] `eslint-plugin-import` — Orden de imports
  - [ ] `eslint-plugin-jsx-a11y` — Accesibilidad
  - [ ] `no-console` en producción (solo `logger`)
- [ ] Configurar Prettier (100 chars, single quotes, trailing comma)
- [ ] Configurar `husky` + `lint-staged` para pre-commit
- [ ] Configurar path aliases: `@/components`, `@/hooks`, `@/store`, `@/api`, `@/utils`
- [ ] Configurar variables de entorno (`.env.development`, `.env.production`)
- [ ] Configurar proxy para desarrollo (Vite → backend :8000)

### 3.2 Estructura de Archivos (Feature-Based)

```
frontend/src/
├── features/
│   ├── auth/
│   │   ├── components/         # LoginForm, ForgotPasswordForm
│   │   ├── hooks/              # useAuth, useLogin
│   │   ├── pages/              # LoginPage, ResetPasswordPage
│   │   ├── api.js              # Auth API calls
│   │   └── authSlice.js        # Redux slice
│   ├── dashboard/
│   │   ├── components/         # MetricCard, SensorChart, AlertWidget
│   │   ├── hooks/              # useDashboardData, useRealTimeReadings
│   │   ├── pages/              # DashboardPage
│   │   └── api.js
│   ├── sensors/
│   │   ├── components/         # SensorGrid, SensorCard, SensorDetail, ReadingChart
│   │   ├── hooks/              # useSensors, useSensorReadings
│   │   ├── pages/              # SensorsPage, SensorDetailPage
│   │   ├── api.js
│   │   └── sensorSlice.js
│   ├── alerts/
│   │   ├── components/         # AlertList, AlertCard, RuleEditor
│   │   ├── hooks/              # useAlerts, useAlertRules
│   │   ├── pages/              # AlertsPage
│   │   ├── api.js
│   │   └── alertSlice.js
│   ├── map/
│   │   ├── components/         # GreenhouseMap, SensorMarker, ZoneOverlay
│   │   ├── hooks/              # useMapData
│   │   └── pages/              # MapPage
│   ├── reports/
│   │   ├── components/         # ReportForm, ReportList, ReportPreview
│   │   ├── hooks/              # useReports
│   │   └── pages/              # ReportsPage
│   ├── settings/
│   │   ├── components/         # ProfileForm, NotificationPrefs, TenantSettings
│   │   └── pages/              # SettingsPage
│   └── admin/
│       ├── components/         # UserTable, GatewayTable, TenantForm
│       ├── hooks/              # useUsers, useGateways
│       └── pages/              # UsersPage, GatewaysPage, TenantPage
├── shared/
│   ├── components/             # Button, Input, Modal, Table, Card, Badge, Spinner, Empty
│   ├── hooks/                  # useDebounce, usePagination, useLocalStorage
│   ├── layouts/                # MainLayout, AuthLayout
│   └── utils/                  # formatters, validators, constants
├── lib/
│   ├── api-client.js           # Axios instance + interceptors
│   ├── websocket.js            # WebSocket manager
│   ├── storage.js              # LocalStorage helpers
│   └── logger.js               # Frontend logger
├── store/                      # Redux store configuration
├── i18n/                       # Traducciones
├── theme/                      # Design tokens
└── App.jsx
```

- [ ] Crear estructura de features según diagrama anterior
- [ ] Mover componentes existentes a estructura feature-based
- [ ] Crear barrel exports (index.js) en cada directorio de feature
- [ ] Verificar que no hay imports circulares

### 3.3 Componentes Compartidos (Design System)

> 🏛️ Componentes reutilizables SIN lógica de negocio. Solo UI pura. Props → render.

- [ ] **Button** — Variantes: primary, secondary, danger, ghost, icon-only. Estados: loading, disabled
- [ ] **Input** — Tipos: text, password, email, number, search. Con label, error, hint
- [ ] **Select** — Dropdown con búsqueda, multi-select, clearable
- [ ] **Modal** — Overlay con header, body, footer. Tamaños: sm, md, lg, fullscreen
- [ ] **Table** — Sortable, filterable, selectable rows, paginación, empty state
- [ ] **Card** — Surface container con header, body, footer. Hover effect
- [ ] **Badge** — Status indicators: online, offline, warning, critical. Dot + text
- [ ] **Spinner** — Loading indicator: spinner, skeleton, progress bar
- [ ] **EmptyState** — Ilustración + mensaje + CTA cuando no hay datos
- [ ] **Toast** — Notificaciones flotantes: success, error, warning, info. Auto-dismiss
- [ ] **Breadcrumb** — Navegación jerárquica
- [ ] **Tabs** — Tab navigation con indicador animado
- [ ] **Tooltip** — Hover information
- [ ] **Avatar** — User avatar con iniciales fallback
- [ ] **Sidebar** — Navegación lateral colapsable con iconos
- [ ] **Header** — Top bar con user menu, notifications bell, breadcrumb
- [ ] **DataGrid** — Tabla avanzada con virtualización para muchas filas
- [ ] **DatePicker** — Selector de fecha y rango de fechas
- [ ] **Chart** — Wrapper de Recharts con estilos del design system
- [ ] Crear Storybook (opcional) para documentar componentes
- [ ] Tests para cada componente compartido (render, props, events)

### 3.4 Feature: Autenticación

- [x] Implementar Login básico
- [ ] **LoginPage**:
  - [ ] Formulario: email + password + remember me
  - [ ] Validación en tiempo real (formato de email, longitud de password)
  - [ ] Loading state durante request
  - [ ] Mensajes de error específicos (credenciales inválidas, cuenta desactivada)
  - [ ] Redirect a dashboard después de login exitoso
  - [ ] Guardar token en localStorage/httpOnly cookie
- [ ] **ForgotPasswordPage**:
  - [ ] Formulario: email
  - [ ] Confirmación: "Si el email existe, recibirás un enlace"
- [ ] **ResetPasswordPage**:
  - [ ] Validar token de URL
  - [ ] Formulario: nueva contraseña + confirmar
  - [ ] Redirect a login después de reset
- [ ] **ProtectedRoute** (HOC/wrapper):
  - [ ] Verificar token válido antes de renderizar
  - [ ] Redirect a login si no autenticado
  - [ ] Verificar rol para rutas de admin
  - [ ] Refresh automático de token antes de expirar
- [ ] **useAuth hook**:
  - [ ] `login(email, password)` — Login y guardar tokens
  - [ ] `logout()` — Limpiar tokens y redirect
  - [ ] `isAuthenticated` — Boolean reactivo
  - [ ] `user` — Datos del usuario actual
  - [ ] `hasRole(role)` — Verificar permisos
- [ ] Tests: login flow, token refresh, protected routes, role check

### 3.5 Feature: Dashboard

- [x] Dashboard básico con gráficas
- [ ] **DashboardPage**:
  - [ ] Grid de métricas principales (4 cards: temp, humidity, co2, light)
  - [ ] Gráfica de lecturas últimas 24h (Recharts AreaChart)
  - [ ] Widget de alertas activas (últimas 5)
  - [ ] Widget de estado de gateways (online/offline)
  - [ ] Widget de mapa mini del invernadero
  - [ ] Selector de rango de tiempo (1h, 6h, 24h, 7d, 30d)
  - [ ] Auto-refresh cada 30s (o WebSocket)
- [ ] **MetricCard** component:
  - [ ] Valor actual grande + unidad
  - [ ] Indicador de tendencia (↑ ↓ →)
  - [ ] Sparkline mini
  - [ ] Color según estado (verde=normal, amarillo=warning, rojo=critical)
  - [ ] Loading skeleton mientras carga
- [ ] **SensorChart** component:
  - [ ] Line/Area chart con Recharts
  - [ ] Multi-series (varios sensores en misma gráfica)
  - [ ] Tooltip con fecha, valor, unidad
  - [ ] Zoom con brush (seleccionar rango)
  - [ ] Líneas de umbral (min/max del invernadero)
  - [ ] Responsive (adaptar a mobile)
- [ ] **AlertWidget** component:
  - [ ] Lista compacta de alertas activas
  - [ ] Indicador de severidad (color + ícono)
  - [ ] Link a detalle de alerta
  - [ ] Badge con conteo de alertas no leídas
- [ ] WebSocket integration: actualizar métricas en tiempo real
- [ ] Tests: renderizado, datos vacíos, loading, error states

### 3.6 Feature: Gestión de Sensores

- [x] Sensores básicos
- [ ] **SensorsPage**:
  - [ ] Vista grid/lista toggle
  - [ ] Filtros: tipo, estado (online/offline), gateway
  - [ ] Búsqueda por nombre
  - [ ] Botón "Agregar sensor"
  - [ ] Paginación
- [ ] **SensorCard** component:
  - [ ] Ícono del tipo de sensor (color coded)
  - [ ] Nombre del sensor
  - [ ] Última lectura + hace cuánto tiempo
  - [ ] Indicador online/offline
  - [ ] Mini sparkline de las últimas horas
  - [ ] Click → navegar a detalle
- [ ] **SensorDetailPage**:
  - [ ] Header con info del sensor (nombre, tipo, gateway, estado)
  - [ ] Gráfica principal de lecturas (configurable: 1h–30d)
  - [ ] Tabla de lecturas recientes
  - [ ] Estadísticas: min, max, avg, tendencia
  - [ ] Historial de alertas de este sensor
  - [ ] Configuración: nombre, umbrales, calibración
  - [ ] Botón "Eliminar sensor" con confirmación
- [ ] **AddSensorModal**:
  - [ ] Step wizard: seleccionar gateway → tipo de sensor → configurar → confirmar
  - [ ] Preview de la configuración antes de crear
- [ ] Tests: CRUD de sensores, filtros, búsqueda, detalle

### 3.7 Feature: Centro de Alertas

- [x] Alertas básicas
- [ ] **AlertsPage**:
  - [ ] Lista de alertas con filtros: severidad, estado, sensor, fecha
  - [ ] Badge de conteo por severidad
  - [ ] Acciones batch: acknowledge/resolve múltiples
  - [ ] Timeline view (opcional)
- [ ] **AlertCard** component:
  - [ ] Color de severidad (border left)
  - [ ] Ícono de tipo de alerta
  - [ ] Mensaje descriptivo
  - [ ] Sensor y gateway afectados
  - [ ] Timestamp relativo ("hace 5 min")
  - [ ] Botones: Acknowledge, Resolve, Ver detalle
- [ ] **AlertRuleEditor**:
  - [ ] Formulario para crear/editar reglas de alerta
  - [ ] Selección de tipo: umbral, rango, tasa de cambio, sin datos
  - [ ] Configuración de valores (min, max, duración)
  - [ ] Selección de acciones: email, push, webhook
  - [ ] Preview: "Si temperatura > 35°C por más de 5 minutos..."
- [ ] Tests: lista, filtros, acknowledge, reglas

### 3.8 Feature: Mapa del Invernadero

- [ ] **MapPage**:
  - [ ] Plano 2D del invernadero (SVG interactivo o Canvas)
  - [ ] Sensores posicionados en el mapa (drag & drop para configurar)
  - [ ] Color de cada sensor según estado actual
  - [ ] Click en sensor → popup con última lectura
  - [ ] Zonas del invernadero con promedios
  - [ ] Heatmap opcional (gradiente de temperatura/humedad)
  - [ ] Leyenda de colores
- [ ] Tests: renderizado del mapa, interacción con sensores

### 3.9 Feature: Reportes

- [x] Reportes básicos
- [ ] **ReportsPage**:
  - [ ] Formulario de generación: tipo (diario/semanal/mensual/custom), rango de fechas, formato (PDF/Excel/CSV)
  - [ ] Lista de reportes generados con estado (pendiente, generando, completado)
  - [ ] Botón de descarga para reportes completados
  - [ ] Preview del reporte antes de generar
- [ ] Tests: formulario, lista, descarga

### 3.10 Feature: Panel de Administración

- [x] Admin panel básico
- [ ] **UsersPage** (admin only):
  - [ ] Tabla de usuarios con: nombre, email, rol, estado, último login
  - [ ] Acciones: editar, cambiar rol, desactivar, eliminar
  - [ ] Formulario de invitación (enviar email)
- [ ] **GatewaysPage** (admin only):
  - [ ] Tabla de gateways con: nombre, serial, estado, última conexión, sensores
  - [ ] Detalle de gateway con logs y métricas
  - [ ] Acciones: reiniciar, actualizar config, eliminar
- [ ] **TenantSettingsPage** (admin only):
  - [ ] Configuración del tenant: nombre, logo, plan, límites
  - [ ] Estadísticas de uso: gateways, sensores, lecturas, almacenamiento
- [ ] Tests: tablas, acciones, permisos (verificar que viewer no ve admin pages)

### 3.11 Feature: Configuración

- [ ] **SettingsPage**:
  - [ ] Perfil: nombre, email, avatar
  - [ ] Seguridad: cambiar contraseña, sesiones activas
  - [ ] Notificaciones: preferencias de canales (email, push, in-app)
  - [ ] Apariencia: idioma (es/en)
  - [ ] API: generar API keys, webhooks

### 3.12 API Client (Clean Architecture)

- [x] Cliente HTTP básico
- [ ] Refactorizar API client:
  - [ ] Axios instance con baseURL, timeout, interceptors
  - [ ] Request interceptor: agregar JWT header automáticamente
  - [ ] Response interceptor: refresh token en 401, retry original request
  - [ ] Error interceptor: parsear errores del backend a formato consistente
  - [ ] Cancel tokens para requests in-flight cuando se cambia de página
- [ ] Crear funciones API por feature (no un archivo monolítico):
  - [ ] `features/auth/api.js` — `login()`, `register()`, `refreshToken()`
  - [ ] `features/sensors/api.js` — `getSensors()`, `getSensor()`, `getReadings()`
  - [ ] `features/alerts/api.js` — `getAlerts()`, `acknowledgeAlert()`
  - [ ] etc.
- [ ] Implementar caché de requests con React Query o SWR (alternativa a Redux para server state)
- [ ] Tests: interceptors, retry, cancel

### 3.13 Estado Global (Redux Toolkit)

- [x] Store básico
- [ ] Refactorizar slices por feature:
  - [ ] `authSlice` — usuario autenticado, tokens, permisos
  - [ ] `uiSlice` — sidebar collapsed, theme, locale, toasts
  - [ ] Considerar React Query/SWR para server state (sensores, alertas, etc.)
- [ ] Implementar selectors memoizados con `createSelector`
- [ ] Implementar middleware de logging en desarrollo
- [ ] Tests: reducers, selectors, async thunks

### 3.14 WebSocket Manager

- [ ] Implementar `WebSocketManager` class:
  - [ ] `connect(url, token)` — Conectar con autenticación
  - [ ] `disconnect()` — Desconectar limpiamente
  - [ ] `subscribe(channel, callback)` — Suscribirse a canal
  - [ ] `unsubscribe(channel)` — Desuscribirse
  - [ ] Auto-reconnect con backoff exponencial
  - [ ] Heartbeat cada 30s
- [ ] Implementar `useWebSocket` hook:
  - [ ] Conectar al montar, desconectar al desmontar
  - [ ] Devolver estado de conexión (connecting, connected, disconnected)
  - [ ] Devolver última lectura recibida por sensor
- [ ] Integrar WebSocket con dashboard para actualizaciones en tiempo real
- [ ] Tests: conexión, reconexión, suscripción

### 3.15 Optimización y Performance

- [ ] Implementar code splitting con `React.lazy()` y `Suspense`
- [ ] Implementar route-based code splitting (cada página es lazy)
- [ ] Implementar memoización con `React.memo`, `useMemo`, `useCallback`
- [ ] Implementar virtualización de listas grandes (`react-virtual` / `react-window`)
- [ ] Implementar debounce en búsquedas y filtros (300ms)
- [ ] Implementar infinite scroll o paginación en tablas grandes
- [ ] Optimizar imágenes: lazy loading, WebP format, responsive images
- [ ] Configurar Service Worker para PWA (cache-first strategy)
- [ ] Lograr Lighthouse score ≥ 90 en todas las métricas
- [ ] Bundle analysis: verificar que no hay dependencias innecesarias

### 3.16 Frontend — Tests Completos

- [ ] Tests unitarios para CADA componente compartido
- [ ] Tests unitarios para CADA hook personalizado
- [ ] Tests de integración por feature (renderizar página completa con mocks)
- [ ] Tests de formularios: validación, submit, error handling
- [ ] Tests de routing: navegación, guards, redirects
- [ ] Tests de responsive: verificar breakpoints principales
- [ ] Tests de accesibilidad: keyboard navigation, screen reader
- [ ] Configurar `testing-library` con custom renders (providers, router)
- [ ] Verificar cobertura ≥ 80% con `vitest --coverage`

### 3.17 Frontend — Calidad de Código

- [ ] Configurar ESLint strict mode
- [ ] Configurar Prettier
- [ ] Configurar TypeScript (migrar de JSX a TSX gradualmente — o mantener JSX con JSDoc types)
- [ ] Configurar `husky` pre-commit hooks
- [ ] Agregar prop-types o TypeScript interfaces a TODOS los componentes
- [ ] Eliminar `console.log` — usar logger dedicado
- [ ] Crear `frontend/README.md` con guía de desarrollo

---

## Fase 4: Aplicación Móvil — React Native (Semanas 11–16)

> 🏛️ **Clean Architecture en Mobile**: Misma separación que en web. Features → componentes, hooks, API, store. Componentes nativos de cada plataforma donde sea necesario.

### 4.1 Configuración y Arquitectura del Proyecto

- [x] Configurar proyecto Expo en `mobile/`
- [ ] Configurar EAS Build para Android e iOS
- [ ] Configurar variables de entorno (`.env.development`, `.env.production`)
- [ ] Configurar path aliases: `@/screens`, `@/components`, `@/hooks`, `@/api`
- [ ] Configurar ESLint + Prettier para React Native
- [ ] Estructurar proyecto por features:
  ```
  mobile/src/
  ├── features/
  │   ├── auth/         # LoginScreen, useAuth
  │   ├── dashboard/    # DashboardScreen, MetricCards
  │   ├── sensors/      # SensorsScreen, SensorDetail
  │   ├── alerts/       # AlertsScreen, AlertCard
  │   ├── map/          # MapScreen, SensorMarker
  │   ├── settings/     # SettingsScreen, ProfileForm
  │   └── notifications/ # NotificationsScreen
  ├── shared/
  │   ├── components/   # Button, Card, Input, Badge, Spinner
  │   ├── hooks/        # useApi, useLocation, useNotifications
  │   ├── navigation/   # Navigators, linking config
  │   └── utils/        # formatters, validators
  ├── lib/
  │   ├── api-client.js # Axios + auth interceptor
  │   ├── storage.js    # AsyncStorage helpers
  │   └── push.js       # Push notifications
  └── store/            # Redux/Zustand
  ```

### 4.2 Navegación (React Navigation)

- [ ] Configurar React Navigation v6:
  - [ ] `AuthStack` — Login, ForgotPassword, ResetPassword
  - [ ] `MainTabs` — Dashboard, Sensors, Alerts, Map, Settings
  - [ ] `SensorStack` — SensorList → SensorDetail → ChartFullscreen
  - [ ] `AlertStack` — AlertList → AlertDetail
  - [ ] `SettingsStack` — Settings → Profile → Notifications → About
- [ ] Configurar deep linking (URLs: `echosmart://sensors/123`)
- [ ] Implementar transiciones animadas entre pantallas
- [ ] Implementar gesture-based navigation (swipe back)
- [ ] Configurar splash screen nativo con `expo-splash-screen`
- [ ] Tests: navegación entre todas las pantallas

### 4.3 Pantallas Principales

- [ ] **DashboardScreen**:
  - [ ] Grid de métricas (2×2) con valores actuales
  - [ ] Gráfica simplificada de las últimas 6 horas
  - [ ] Lista compacta de alertas activas
  - [ ] Pull-to-refresh
  - [ ] Loading skeletons
- [ ] **SensorsScreen**:
  - [ ] Lista de sensores con SensorCard
  - [ ] Filtro rápido por tipo (chips horizontales)
  - [ ] Búsqueda por nombre
  - [ ] Pull-to-refresh
  - [ ] FAB "+" para agregar sensor
- [ ] **SensorDetailScreen**:
  - [ ] Header con info del sensor
  - [ ] Gráfica interactiva con zoom/pan (victory-native o react-native-chart-kit)
  - [ ] Selector de rango de tiempo
  - [ ] Estadísticas: min, max, avg
  - [ ] Lista de alertas recientes
  - [ ] Botón fullscreen para gráfica
- [ ] **AlertsScreen**:
  - [ ] Lista de alertas con indicadores de severidad
  - [ ] Filtros: severidad, estado
  - [ ] Swipe para acknowledge/resolve
  - [ ] Badge en tab con conteo de no leídas
- [ ] **MapScreen**:
  - [ ] Mapa del invernadero (react-native-maps o SVG)
  - [ ] Markers de sensores con colores de estado
  - [ ] Popup al tocar sensor con última lectura
- [ ] **SettingsScreen**:
  - [ ] Perfil de usuario
  - [ ] Preferencias de notificaciones
  - [ ] Idioma
  - [ ] Información de la app (versión, licencias)
  - [ ] Logout
- [ ] **NotificationsScreen**:
  - [ ] Lista de notificaciones push recibidas
  - [ ] Marcar como leída
  - [ ] Navegar al recurso relacionado al tocar
- [ ] **AddSensorScreen**:
  - [ ] Formulario step-by-step
  - [ ] Escaneo de QR/código del sensor (expo-barcode-scanner)
- [ ] **ChartFullscreenScreen**:
  - [ ] Gráfica a pantalla completa en landscape
  - [ ] Pinch to zoom
  - [ ] Exportar como imagen

### 4.4 Componentes Compartidos (Mobile)

- [ ] **Button** — Primary, secondary, danger, outline, FAB. Loading state
- [ ] **Input** — Text, password, search. Con label y error message
- [ ] **Card** — Elevated card con sombra nativa
- [ ] **Badge** — Status dot + conteo (para alertas)
- [ ] **Spinner** — Loading overlay + inline spinner
- [ ] **EmptyState** — Ilustración + mensaje + CTA
- [ ] **Avatar** — Con iniciales y badge de estado
- [ ] **BottomSheet** — Modal desde abajo (para filtros, acciones)
- [ ] **SwipeableRow** — Swipe left/right para acciones (acknowledge, delete)
- [ ] **RefreshControl** — Pull-to-refresh estilizado
- [ ] **SkeletonLoader** — Placeholder animado mientras carga
- [ ] Tests para cada componente

### 4.5 Funcionalidades Nativas

- [ ] **Push Notifications** (Firebase Cloud Messaging):
  - [ ] Configurar `expo-notifications`
  - [ ] Registrar device token en backend al login
  - [ ] Manejar notificaciones en foreground (in-app banner)
  - [ ] Manejar notificaciones en background (sistema operativo)
  - [ ] Deep linking desde notificación → pantalla relevante
  - [ ] Canales de notificación por severidad de alerta (Android)
- [ ] **Modo Offline**:
  - [ ] Cache de última lectura de cada sensor en AsyncStorage
  - [ ] Detectar estado de red (`@react-native-community/netinfo`)
  - [ ] Mostrar banner "Sin conexión" cuando offline
  - [ ] Sincronizar al reconectar
  - [ ] Cola de acciones offline (acknowledge alerts)
- [ ] **Biometría** (iOS/Android):
  - [ ] Login con Face ID / Touch ID / Fingerprint
  - [ ] Configurar en Settings
  - [ ] `expo-local-authentication`
- [ ] **Haptic Feedback**:
  - [ ] Feedback táctil en acciones importantes (acknowledge, alert)
  - [ ] `expo-haptics`

### 4.6 Android — Build y Distribución

- [ ] Configurar `eas.json` para Android:
  - [ ] Profile: development (APK debug), preview (APK release), production (AAB)
- [ ] Configurar splash screen nativo
- [ ] Configurar adaptive icon (foreground + background layers)
- [ ] Generar APK de desarrollo: `eas build --platform android --profile preview`
- [ ] Probar en emulador Android (Android Studio)
- [ ] Probar en dispositivos Android reales (3+ dispositivos)
- [ ] Configurar Google Play Console
- [ ] Publicar en Google Play Store (internal testing → production)

### 4.7 iOS — Build y Distribución

- [ ] Configurar `eas.json` para iOS:
  - [ ] Profile: development (simulator), preview (ad-hoc), production (App Store)
- [ ] Configurar provisioning profiles y certificates
- [ ] Configurar splash screen y app icon para iOS
- [ ] Adaptar UI para convenciones iOS (Safe Area, large titles, gestos)
- [ ] Generar build: `eas build --platform ios --profile preview`
- [ ] Probar en simulador iOS (Xcode)
- [ ] Probar en dispositivos iOS reales
- [ ] Configurar App Store Connect
- [ ] Publicar en App Store (TestFlight → production)

### 4.8 Mobile — Tests

- [ ] Tests unitarios para hooks personalizados
- [ ] Tests de componentes con React Native Testing Library
- [ ] Tests de navegación (screen mounting, params)
- [ ] Tests de integración: flujo login → dashboard → sensor detail
- [ ] Tests de offline: cache hit, queue actions, sync
- [ ] Verificar performance: 60fps en listas, scroll suave
- [ ] Verificar accesibilidad: labels, roles, focus order

### 4.9 Mobile — Calidad de Código

- [ ] ESLint + Prettier para React Native
- [ ] Remover `console.log` — usar logger
- [ ] Agregar prop-types/TypeScript a todos los componentes
- [ ] Crear `mobile/README.md` con guía de desarrollo y testing

---

## Fase 5: Aplicación de Escritorio — Electron (Semanas 17–20)

> 🏛️ **Clean Architecture en Electron**: Separar main process (Node.js) de renderer process (React). Comunicación exclusivamente vía IPC con preload scripts seguros.

### 5.1 Arquitectura Electron

```
desktop/src/
├── main/
│   ├── main.js              # Entry point, ventana principal
│   ├── menu.js              # Menú nativo por plataforma
│   ├── tray.js              # Icono en bandeja del sistema
│   ├── ipc-handlers.js      # Manejadores IPC (main ↔ renderer)
│   ├── auto-updater.js      # Auto-actualización
│   ├── local-gateway.js     # Conexión directa al gateway (LAN)
│   └── store.js             # Configuración persistente (electron-store)
├── preload/
│   └── preload.js           # Exposición segura de APIs al renderer
├── renderer/                # Frontend React (el mismo de frontend/)
│   └── index.html
└── assets/
    ├── icon.png             # Icono de la app
    └── tray-icon.png        # Icono de la bandeja
```

- [x] Configurar proyecto Electron
- [x] Implementar main process básico
- [x] Implementar preload scripts
- [x] Integrar frontend React como renderer
- [ ] Refactorizar main process con separación de responsabilidades
- [ ] Implementar IPC handlers tipados

### 5.2 Funcionalidades Compartidas (Desktop)

- [ ] **Window Management**:
  - [ ] Ventana principal con tamaño mínimo (1024×768)
  - [ ] Guardar posición y tamaño de ventana al cerrar
  - [ ] Splash screen nativo al iniciar
  - [ ] Prevent multiple instances (single instance lock)
- [ ] **Menú Nativo**:
  - [ ] Crear menú por plataforma (Windows, macOS, Linux)
  - [ ] File → Export Data, Import Config
  - [ ] View → Reload, DevTools (solo dev), Fullscreen
  - [ ] Help → About, Check for Updates, Documentation
  - [ ] Shortcuts: Ctrl+R, Ctrl+Shift+I, F11
- [ ] **System Tray**:
  - [ ] Icono en bandeja con estado (verde=online, rojo=alerta)
  - [ ] Context menu: Open, Status, Quit
  - [ ] Minimize to tray (no cerrar al hacer click en X)
  - [ ] Notificaciones nativas del sistema operativo
- [ ] **Auto-Update** (`electron-updater`):
  - [ ] Check for updates al iniciar y periódicamente
  - [ ] Notificar al usuario si hay actualización
  - [ ] Descargar e instalar en background
  - [ ] Configurar GitHub Releases como update server
- [ ] **Almacenamiento Local** (`electron-store`):
  - [ ] Configuración persistente (tema, idioma, ventana)
  - [ ] Cache de credenciales con encriptación
  - [ ] Cache de últimas lecturas para acceso offline
- [ ] **Conexión Directa al Gateway**:
  - [ ] Descubrimiento de gateways en red local (mDNS/SSDP)
  - [ ] Conexión HTTP directa para lecturas sin cloud
  - [ ] Indicador de modo: "Directo" vs "Cloud"
  - [ ] Fallback a cloud si gateway no accesible
- [ ] **IPC (Inter-Process Communication)**:
  - [ ] Definir channels tipados: `gateway:discover`, `gateway:connect`, `app:update-check`
  - [ ] Exponer APIs seguras vía `contextBridge`
  - [ ] Nunca exponer `require`, `fs`, o `child_process` al renderer

### 5.3 Windows

- [ ] Configurar electron-builder para Windows (NSIS installer)
- [ ] Desktop shortcut, start menu entry
- [ ] Generar instalador `.exe`
- [ ] Firmar ejecutable con certificado de código
- [ ] Probar en Windows 10 y Windows 11
- [ ] Probar instalación, actualización, desinstalación

### 5.4 macOS

- [ ] Configurar electron-builder para macOS (DMG + ZIP)
- [ ] Configurar DMG con fondo personalizado y drag-to-Applications
- [ ] Adaptar menú nativo y dock
- [ ] Firmar con Apple Developer certificate
- [ ] Notarización de la app
- [ ] Probar en macOS Ventura/Sonoma

### 5.5 Linux

- [ ] Configurar electron-builder: AppImage, `.deb`, `.snap`
- [ ] Desktop entry (`.desktop` file) con ícono
- [ ] Adaptar notificaciones para GNOME/KDE
- [ ] Probar en Ubuntu 22.04+

### 5.6 Desktop — Tests y Calidad

- [ ] Tests de IPC handlers
- [ ] Tests de preload scripts (seguridad)
- [ ] Tests de menú nativo y tray
- [ ] Security audit: renderer sin acceso a Node.js APIs
- [ ] Configurar CSP (Content Security Policy)
- [ ] ESLint para main process
- [ ] Crear `desktop/README.md`

---

## Fase 6: Infraestructura y DevOps (Continuo)

> 🏛️ **Infrastructure as Code**: Toda la infraestructura definida en archivos versionados. Reproducible al 100%.

### 6.1 Docker — Containerización

- [ ] **Backend Dockerfile** (`infra/docker/backend.Dockerfile`):
  - [ ] Multi-stage build: builder → runner (slim image < 200MB)
  - [ ] Non-root user
  - [ ] Health check endpoint
  - [ ] Optimizar layer caching
- [ ] **Frontend Dockerfile** (`infra/docker/frontend.Dockerfile`):
  - [ ] Multi-stage: node (build) → nginx (serve)
  - [ ] SPA fallback config en nginx
  - [ ] Imagen final < 50MB
- [x] `docker-compose.yml` para desarrollo
- [ ] `docker-compose.dev.yml` con hot-reload para backend y frontend
- [ ] `docker-compose.prod.yml` con gunicorn, SSL, resource limits
- [ ] `docker-compose.test.yml` para CI
- [ ] `.dockerignore` para cada servicio

### 6.2 Kubernetes — Orquestación

- [x] Manifiestos básicos en `infra/k8s/`
- [ ] Backend Deployment (2+ replicas, readiness/liveness probes)
- [ ] Frontend Deployment (Nginx serving static)
- [ ] PostgreSQL StatefulSet con PVC
- [ ] InfluxDB StatefulSet con PVC
- [ ] Redis Deployment
- [ ] Mosquitto Deployment
- [x] Ingress con TLS (cert-manager)
- [ ] HPA (auto-scale backend basado en CPU)
- [ ] NetworkPolicy (segmentación de red)
- [ ] Kustomize para ambientes (dev/staging/prod)

### 6.3 CI/CD (GitHub Actions)

- [ ] **CI Pipeline** (`ci.yml`):
  - [ ] Trigger: push + PR to main
  - [ ] Jobs: lint-backend, lint-frontend, test-backend, test-frontend, test-gateway, security-scan
  - [ ] Reportar cobertura como comentario en PR
  - [ ] Bloquear merge si cobertura < 80% o lint falla
- [ ] **CD Pipeline** (`deploy.yml`):
  - [ ] Build Docker images multi-arch
  - [ ] Push a Container Registry
  - [ ] Deploy a staging (auto) y producción (manual approval)
- [ ] **Mobile Build** (`mobile.yml`): EAS Build Android + iOS en tag `mobile-v*`
- [ ] **Desktop Build** (`desktop.yml`): Electron build Win/Mac/Linux en tag `desktop-v*`
- [ ] **Dependabot**: Python + Node.js + GitHub Actions, semanal

### 6.4 Monitoreo y Observabilidad

- [ ] Logging centralizado (structlog → ELK/Loki)
- [ ] Métricas Prometheus (`/metrics` en backend)
- [ ] Grafana dashboards
- [ ] Alertas de infraestructura (CPU, memory, error rate)
- [ ] Health checks para todos los servicios

### 6.5 Scripts de Automatización

- [ ] `setup-dev.sh` — Setup completo del entorno de desarrollo
- [ ] `backup-db.sh` — Backup PostgreSQL + InfluxDB con rotación
- [ ] `deploy.sh` — Deploy con zero-downtime y rollback
- [ ] `seed-data.sh` — Datos de demo (tenant, users, gateways, sensors, readings)

### 6.6 Seguridad de Infraestructura

- [ ] HTTPS en todos los endpoints
- [ ] Firewall: solo puertos 80, 443, 8883
- [ ] Rate limiting a nivel de Nginx/Ingress
- [ ] Secrets management (no hardcoded)
- [ ] Backups encriptados
- [ ] Procedimiento de incident response documentado

---

## Fase 7: Features Avanzadas (Semanas 21+)

### 7.1 Control de Actuadores

- [ ] Modelo de datos: `Actuator(id, name, type, gpio_pin, state, gateway_id)`
- [ ] Driver de relés en gateway: `RelayDriver` (On/Off via GPIO)
- [ ] Protección contra switching rápido (debounce)
- [ ] Programación horaria tipo CRON
- [ ] Automatización por reglas:
  - [ ] `IF temp > 35°C AND duration > 5min THEN ventilación ON`
  - [ ] `IF soil_moisture < 40% THEN riego ON por 10 min`
  - [ ] `IF light < 5000 lux THEN iluminación ON`
- [ ] API REST para control remoto
- [ ] UI en frontend
- [ ] Tests: drivers, scheduling, automatización

### 7.2 Analítica Predictiva (ML)

- [ ] Dataset de entrenamiento (30+ días de datos)
- [ ] Predicción de temperatura (LSTM/Prophet, 1h/6h/24h)
- [ ] Detección de anomalías (Isolation Forest)
- [ ] Recomendaciones de riego
- [ ] API de predicciones
- [ ] Visualización en dashboard
- [ ] Tests con datos históricos

### 7.3 Integraciones Externas

- [ ] WhatsApp Business API para alertas
- [ ] Telegram Bot (@EchoSmartBot)
- [ ] Slack / Microsoft Teams webhooks
- [ ] API Meteorológica (OpenWeatherMap) — pronóstico + correlación
- [ ] Tests con APIs mockeadas

### 7.4 Administración Avanzada

- [ ] Audit Log: registrar TODA acción con old_value/new_value
- [ ] SSO: Google OAuth2, Microsoft Azure AD, SAML 2.0
- [ ] 2FA: TOTP con Google Authenticator + backup codes
- [ ] Suscripciones: Free/Pro/Enterprise con Stripe
- [ ] Tests: audit trail, SSO flow, 2FA setup

### 7.5 API Pública y Documentación

- [ ] API keys con scopes (read, write, admin)
- [ ] Rate limiting por API key
- [ ] Portal de desarrolladores con guías
- [ ] Webhooks salientes configurables
- [ ] Documentación OpenAPI interactiva

### 7.6 Internacionalización y Accesibilidad

- [ ] Traducciones completas español/inglés/portugués
- [ ] WCAG 2.1 AA en frontend web
- [ ] VoiceOver/TalkBack en mobile
- [ ] Modo alto contraste
- [ ] Tests de accesibilidad automatizados (axe-core)

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
