# EchoSmart — Lista de Tareas de Desarrollo Multiplataforma

> Kit IoT de agricultura de precisión para monitoreo ambiental inteligente en invernaderos.
> Gateway implementado en **C++17 nativo** con empaquetado **.deb** para Raspberry Pi OS (arm64).
> Producto comercializado como **kit llave en mano** (Raspberry Pi + sensores + microSD pre-grabada).

---

## 🏛️ Principios de Arquitectura y Clean Code

> ⚠️ **OBLIGATORIO**: Todas las fases de desarrollo DEBEN seguir estos principios. Cualquier PR que viole estos estándares será rechazado.

### Principio 1: Clean Architecture (Arquitectura Limpia)

El proyecto sigue **Clean Architecture** de Robert C. Martin. Las capas son:

```
┌─────────────────────────────────────────────┐
│  Capa Externa: Frameworks & Drivers         │
│  (FastAPI, React, Electron, C++ binaries)    │
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
| **O** — Open/Closed | Nuevos sensores se agregan creando un nuevo sub-comando `echosmart read <nuevo>`, SIN modificar otros comandos. |
| **L** — Liskov Substitution | Todos los sensores se leen con la misma interfaz del binario `echosmart read <sensor> --simulate=true`. Son intercambiables. |
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
╱────────────────────╲ - pytest (Backend Python), CTest/shell (Gateway C++), Vitest (JS)
```

- **Cobertura mínima**: 80% en servicios y utilidades
- **Cada PR DEBE incluir tests** para el código nuevo/modificado
- **Tests primero**: Preferir TDD (Test-Driven Development) para lógica de negocio

### Principio 6: Convenciones de Código

| Aspecto | C++ (Gateway) | Python (Backend) | JavaScript/TypeScript (Frontend/Mobile/Desktop) |
|---------|---------------|------------------|--------------------------------------------------|
| **Estilo** | C++17, clang-format | PEP 8 + Black formatter | ESLint + Prettier |
| **Nombrado** | `snake_case` para funciones/variables, `PascalCase` para clases | `snake_case` funciones/variables, `PascalCase` clases | `camelCase` para funciones/variables, `PascalCase` para componentes |
| **Compilación** | CMake + g++/clang++ | N/A | N/A |
| **Empaquetado** | .deb (dpkg-buildpackage) | pip + requirements.txt | npm |
| **Type hints** | Tipado estático nativo C++ | Obligatorios en funciones públicas | TypeScript/JSDoc types |
| **Max line length** | 100 caracteres | 88 caracteres (Black) | 100 caracteres (Prettier) |
| **Commits** | Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:` | Conventional Commits | Conventional Commits |

### Principio 7: Patrones de Diseño Aplicados

| Patrón | Dónde se usa | Ejemplo |
|--------|-------------|---------|
| **Repository** | Backend — acceso a datos | `SensorRepository` encapsula queries SQL |
| **Service Layer** | Backend — lógica de negocio | `AlertService` orquesta detección y notificación |
| **Factory** | Gateway — creación de lecturas | `echosmart read <tipo>` selecciona el sub-comando correcto |
| **Observer** | Gateway/Frontend — eventos | Sensor Manager emite eventos, Alert Engine escucha |
| **Strategy** | Gateway — protocolos de comunicación | Diferentes estrategias para I2C, UART, GPIO |
| **Adapter** | Frontend — API calls | Adaptar respuesta HTTP a estado Redux |
| **Singleton** | Config — configuración global | Una sola instancia de `Config` por proceso |
| **Middleware** | Backend/Frontend — pipeline | Auth middleware, rate limiter, error handler |
| **DTO** | Backend — transferencia de datos | Pydantic schemas validan y transforman datos |

### Principio 8: Manejo de Errores

```cpp
// ❌ MAL — Silenciar errores
try {
    reading = sensor.read();
} catch (...) {
    // silencio
}

// ✅ BIEN — Errores específicos con manejo apropiado
try {
    auto reading = sensor.read();
} catch (const SensorTimeoutError& e) {
    log_warning("Sensor " + sensor.id + " timeout: " + e.what());
    return SensorReading::empty(sensor.id, "timeout");
} catch (const SensorDisconnectedError& e) {
    log_error("Sensor " + sensor.id + " disconnected: " + e.what());
    alert_engine.fire(AlertType::SENSOR_OFFLINE, sensor.id);
    throw;
}
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

```cpp
// ❌ MAL — Print statements
std::cout << "Sensor leyó " << value << std::endl;

// ✅ BIEN — Logging con contexto (ISO 8601 + JSON)
log_info("sensor_reading_received",
    {{"sensor_id", sensor.id},
     {"sensor_type", "ds18b20"},
     {"value", 25.3},
     {"unit", "°C"},
     {"gateway_id", gateway.id}});
```

- Usar logging estructurado a stdout/journal (C++ gateway) o `structlog` (Python backend)
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

### 0.14 Normas de Diseño y Uso de Assets para Todas las Plataformas

> 🎨 **OBLIGATORIO**: Todas las apps (Web, Android, iOS, Desktop) DEBEN seguir estas normas para que el resultado sea coherente con los mockups y el estilo Starlink.

#### Paleta de Colores (Aplicar en TODAS las plataformas)

| Token | Hex | Uso |
|-------|-----|-----|
| `bg-primary` | `#000000` | Fondo principal de la app |
| `bg-surface` | `#111111` | Cards, contenedores, modales |
| `bg-elevated` | `#1A1A1A` | Elementos elevados, headers, tooltips |
| `bg-sidebar` | `#0A0A0A` | Sidebar, navigation drawer |
| `bg-hover` | `#222222` | Hover state en elementos interactivos |
| `bg-input` | `#1A1A1A` | Campos de texto, dropdowns |
| `accent-green` | `#00E676` | Botones primarios, indicadores positivos, CTA |
| `accent-cyan` | `#00BCD4` | Links, elementos secundarios, badges info |
| `text-primary` | `#FFFFFF` | Texto principal |
| `text-secondary` | `#B0BEC5` | Texto secundario, labels |
| `text-muted` | `#616161` | Texto deshabilitado, placeholders |
| `border` | `#2A2A2A` | Bordes sutiles entre secciones |
| `sensor-temp` | `#FF5252` | Todo lo relacionado con temperatura |
| `sensor-humidity` | `#42A5F5` | Todo lo relacionado con humedad |
| `sensor-light` | `#FFD54F` | Todo lo relacionado con luminosidad |
| `sensor-soil` | `#8D6E63` | Todo lo relacionado con suelo |
| `sensor-co2` | `#78909C` | Todo lo relacionado con CO₂ |
| `alert-critical` | `#FF1744` | Alertas críticas |
| `alert-high` | `#FF9100` | Alertas altas |
| `alert-medium` | `#FFD600` | Alertas medias |
| `alert-low` | `#00E676` | Alertas bajas/info |
| `status-online` | `#00E676` | Dispositivo online |
| `status-offline` | `#FF5252` | Dispositivo offline |
| `status-warning` | `#FFD600` | Dispositivo con warning |

#### Tipografía

| Fuente | Uso | Plataformas |
|--------|-----|-------------|
| **Inter** | UI principal (labels, botones, navegación) | Web, Desktop, Mobile |
| **JetBrains Mono** | Datos numéricos, logs, código, lecturas de sensores | Web, Desktop, Mobile |
| System (SF Pro / Roboto) | Fallback nativo | iOS / Android |

#### Iconos y Assets — Reglas de Uso

- [ ] **App Icons**: Usar assets de `assets/icons/png/` en resolución correcta por plataforma:
  - Web favicon: `assets/icons/ico/favicon.ico`
  - Web PWA: `assets/icons/png/app-icon-192.png`, `app-icon-512.png`
  - Android: `assets/platform/android/adaptive-icon-foreground.png` + `background.png`
  - iOS: `assets/platform/ios/app-icon-1024.png`
  - Desktop: `assets/icons/ico/app.ico` (Windows), `assets/icons/png/app-icon-512.png` (macOS/Linux)
  - Tray: `assets/platform/desktop/tray-icon-32.png` / `64.png` / `128.png`
- [ ] **Sensor Icons**: Usar SVGs de `assets/icons/svg/sensors/` para UI inline:
  - `temperature.svg`, `humidity.svg`, `light.svg`, `soil-moisture.svg`, `co2.svg`
  - Colorear dinámicamente según estado (normal=sensor color, alert=alert color)
- [ ] **Navigation Icons**: Usar SVGs de `assets/icons/svg/navigation/` para menús y tabs:
  - `dashboard.svg`, `sensors.svg`, `alerts.svg`, `map.svg`, `reports.svg`, `settings.svg`, `users.svg`
- [ ] **Logos**: Usar SVGs de `assets/icons/svg/logos/` en headers y splash:
  - `logo-icon.svg` — Solo ícono (sidebar colapsado, app icon)
  - `logo-full.svg` — Ícono + texto (header, splash, about)
  - `logo-horizontal.svg` — Para headers anchos
- [ ] **Splash Screens**: Usar PNGs de `assets/splash/png/` por resolución de pantalla
- [ ] **Ilustraciones**: Usar SVGs de `assets/icons/svg/illustrations/` para empty states y onboarding
- [ ] **Open Graph**: Usar `assets/platform/web/og-image.png` para metadata social

#### Principios de Diseño Visual (Estilo Starlink)

- [ ] **Fondo siempre negro puro** (#000000) — NUNCA usar gris, azul oscuro o verde oscuro como fondo
- [ ] **Cards con superficie #111111** — Sin bordes visibles, solo sombra sutil
- [ ] **Bordes mínimos** — Preferir separación por espaciado, no por líneas
- [ ] **Sin decoraciones**: no grid lines, no stripes, no patterns en fondos
- [ ] **Tipografía clara**: texto blanco (#FFF) sobre negro, con jerarquía de tamaños
- [ ] **Datos numéricos grandes**: lecturas de sensores en font-size grande (24-48px) con unidad en texto pequeño
- [ ] **Gráficas con colores vivos** sobre fondo negro — usar colores de sensor para series
- [ ] **Animaciones sutiles**: transiciones de 200-300ms, no flashy
- [ ] **Responsive**: adaptar layout a mobile-first, luego tablet, luego desktop
- [ ] **Accesibilidad**: contrast ratio ≥ 4.5:1, focus indicators visibles, alt text en imágenes

---

## Fase 1: MVP — Gateway Local (Semanas 1–3)

> ⚠️ **IMPORTANTE — Enfoque "Simulation-First"**: Todo el desarrollo de binarios del gateway se realiza **sin hardware físico**. Cada binario incluye un flag `--simulate` que genera datos realistas dentro de los rangos del invernadero. El hardware físico (Raspberry Pi + sensores) se integra únicamente en la **Fase 11: Testing con Hardware Real**. El gateway se implementa en **C++17** y se empaqueta como **.deb** para Raspberry Pi OS (arm64).

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
| **Driver** | `gateway/cpp/echosmart read.cpp` (sub-comando `ds18b20`) |
| **Simulación** | `echosmart read ds18b20 --simulate=true` → valores entre 15.0°C y 35.0°C |

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
| **¿Por qué este sensor?** | Combina temperatura y humedad en un solo módulo. Mejor precisión que el DHT11. Muy utilizado en agricultura de precisión. Bajo costo (~$3 USD). Lectura vía GPIO con libgpiod en el binario C++. |
| **Driver** | `gateway/cpp/echosmart read.cpp` (sub-comando `dht22`) |
| **Simulación** | `echosmart read dht22 --simulate=true` → Temp: 15.0–35.0°C, Humedad: 40.0–90.0% |

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
| **Driver** | `gateway/cpp/echosmart read.cpp` (sub-comando `bh1750`) |
| **Simulación** | `echosmart read bh1750 --simulate=true` → valores entre 500 y 50,000 lux |

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
| **Driver** | `gateway/cpp/echosmart read.cpp` (sub-comando `soil`) |
| **Simulación** | `echosmart read soil --simulate=true` → valores entre 20.0% y 90.0% |

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
| **Driver** | `gateway/cpp/echosmart read.cpp` (sub-comando `mhz19c`) |
| **Simulación** | `echosmart read mhz19c --simulate=true` → valores entre 350 y 2,000 ppm |

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

### 1.2 Arquitectura del Gateway (Binario Unificado Qt/C++ + .deb)

> 🏛️ Todo el gateway se compila en **un solo binario `echosmart`** que expone
> múltiples comandos con la sintaxis: `echosmart <command> <input> --<arg>=<value>`.
> Los archivos fuente usan `.cpp`, `.h`, `.qml`, `.qrc` y `.ui`.

#### Tabla de comandos del binario `echosmart`

| Comando | Input | Argumentos | Descripción |
|---------|-------|------------|-------------|
| `echosmart read` | `<sensor>` | `--simulate=true`, `--format=json` | Leer un sensor |
| `echosmart sysinfo` | — | `--format=json\|text` | Diagnósticos del sistema |
| `echosmart run` | — | `--config=<path>`, `--sensors=<path>`, `--simulate=true`, `--once=true`, `--interval=<sec>` | Ejecutar daemon de polling |
| `echosmart setup` | — | `--config=<path>` | Wizard de primer arranque |
| `echosmart status` | — | `--format=json\|text` | Estado del gateway y sensores |
| `echosmart calibrate` | `<sensor>` | `--dry=<val>`, `--wet=<val>`, `--ref=<val>` | Calibrar sensor |
| `echosmart list` | — | — | Listar sensores configurados |
| `echosmart test` | `<sensor>\|all` | `--simulate=true` | Probar sensores |
| `echosmart version` | — | — | Mostrar versión |
| `echosmart help` | `[command]` | — | Mostrar ayuda |

#### Ejemplos de uso

```bash
echosmart read ds18b20 --simulate=true          # Lectura simulada de temperatura
echosmart read dht22                             # Lectura real de temp+humedad
echosmart read bh1750 --format=json              # Lectura de luz en JSON
echosmart sysinfo                                # Diagnósticos del sistema
echosmart sysinfo --format=text                  # Diagnósticos en texto plano
echosmart run --simulate=true --once=true         # Un ciclo de polling simulado
echosmart run --interval=30                       # Daemon con polling cada 30s
echosmart run --config=/etc/echosmart/gateway.env # Daemon con config custom
echosmart setup                                   # Wizard interactivo
echosmart status                                  # Estado actual
echosmart calibrate soil --dry=3200 --wet=1400    # Calibrar sensor de suelo
echosmart list                                    # Listar sensores
echosmart test all --simulate=true                # Probar todos los sensores
echosmart version                                 # Mostrar versión
echosmart help read                               # Ayuda del comando read
```

#### Estructura de archivos fuente

```
gateway/
├── cpp/                                          # Código fuente C++ / Qt
│   ├── CMakeLists.txt                            # Build system raíz (C++17, Qt6, -O2)
│   │
│   ├── main.cpp                                  # Entry point — dispatch de comandos
│   ├── cli.h                                     # Parseo de `echosmart <cmd> <input> --<arg>=<val>`
│   ├── cli.cpp                                   # Implementación del parser CLI
│   │
│   ├── commands/                                 # Un .h + .cpp por comando
│   │   ├── cmd_read.h                            # Comando `echosmart read <sensor>`
│   │   ├── cmd_read.cpp                          # Dispatch a driver + salida JSON
│   │   ├── cmd_sysinfo.h                         # Comando `echosmart sysinfo`
│   │   ├── cmd_sysinfo.cpp                       # Recopila CPU, RAM, disco, uptime
│   │   ├── cmd_run.h                             # Comando `echosmart run` (daemon)
│   │   ├── cmd_run.cpp                           # Loop de polling + alertas + sync
│   │   ├── cmd_setup.h                           # Comando `echosmart setup`
│   │   ├── cmd_setup.cpp                         # Wizard interactivo de config
│   │   ├── cmd_status.h                          # Comando `echosmart status`
│   │   ├── cmd_status.cpp                        # Lee sysinfo + última lectura
│   │   ├── cmd_calibrate.h                       # Comando `echosmart calibrate <sensor>`
│   │   ├── cmd_calibrate.cpp                     # Calibración de sensor
│   │   ├── cmd_list.h                            # Comando `echosmart list`
│   │   ├── cmd_list.cpp                          # Lista sensores de sensors.json
│   │   ├── cmd_test.h                            # Comando `echosmart test <sensor|all>`
│   │   ├── cmd_test.cpp                          # Ejecuta lectura de prueba
│   │   ├── cmd_version.h                         # Comando `echosmart version`
│   │   ├── cmd_version.cpp                       # Imprime versión
│   │   ├── cmd_help.h                            # Comando `echosmart help [cmd]`
│   │   └── cmd_help.cpp                          # Imprime ayuda general o por comando
│   │
│   ├── drivers/                                  # Un .h + .cpp por tipo de sensor
│   │   ├── sensor_driver.h                       # Clase base abstracta SensorDriver
│   │   ├── sensor_driver.cpp                     # Lógica común (simulación, validación)
│   │   ├── ds18b20_driver.h                      # DS18B20Driver : SensorDriver
│   │   ├── ds18b20_driver.cpp                    # 1-Wire + simulación
│   │   ├── dht22_driver.h                        # DHT22Driver : SensorDriver
│   │   ├── dht22_driver.cpp                      # GPIO + simulación
│   │   ├── bh1750_driver.h                       # BH1750Driver : SensorDriver
│   │   ├── bh1750_driver.cpp                     # I2C + simulación
│   │   ├── soil_driver.h                         # SoilDriver : SensorDriver
│   │   ├── soil_driver.cpp                       # ADS1115 ADC + simulación
│   │   ├── mhz19c_driver.h                       # MHZ19CDriver : SensorDriver
│   │   ├── mhz19c_driver.cpp                     # UART + simulación
│   │   ├── driver_factory.h                      # DriverFactory — crea driver por tipo
│   │   └── driver_factory.cpp                    # Registro y dispatch
│   │
│   ├── core/                                     # Lógica central del daemon
│   │   ├── gateway.h                             # Clase Gateway (orquestador del daemon)
│   │   ├── gateway.cpp                           # Ciclo de polling + señales
│   │   ├── sensor_poller.h                       # Clase SensorPoller
│   │   ├── sensor_poller.cpp                     # Polling de sensores
│   │   ├── alert_engine.h                        # Clase AlertEngine
│   │   ├── alert_engine.cpp                      # Evaluación de reglas + cooldown
│   │   ├── data_store.h                          # Clase DataStore (persistencia)
│   │   ├── data_store.cpp                        # JSONL rotativo + cleanup
│   │   ├── cloud_syncer.h                        # Clase CloudSyncer (HTTP sync)
│   │   ├── cloud_syncer.cpp                      # POST batch + retry + backoff
│   │   ├── mqtt_publisher.h                      # Clase MqttPublisher
│   │   └── mqtt_publisher.cpp                    # Publicación MQTT + LWT
│   │
│   ├── shared/                                   # Tipos y utilidades compartidas
│   │   ├── version.h                             # ES_VERSION_MAJOR/MINOR/PATCH/STRING
│   │   ├── sensor_data.h                         # Struct SensorData
│   │   ├── sensor_data.cpp                       # Serialización JSON
│   │   ├── alert_rule.h                          # Struct AlertRule
│   │   ├── alert_rule.cpp                        # Evaluación
│   │   ├── config_loader.h                       # GatewayConfig + SensorEntry
│   │   ├── config_loader.cpp                     # Parser .env y .json
│   │   ├── json_formatter.h                      # Funciones JSON sin deps
│   │   ├── json_formatter.cpp                    # Implementación
│   │   ├── logger.h                              # log_info/warn/error (ISO 8601)
│   │   ├── logger.cpp                            # Implementación
│   │   ├── file_utils.h                          # read_file, trim, etc.
│   │   ├── file_utils.cpp                        # Implementación
│   │   └── resources.qrc                         # Recursos embebidos (schemas, defaults)
│   │
│   ├── ui/                                       # Interfaz gráfica Qt (opcional)
│   │   ├── main_window.h                         # Ventana principal Qt Widgets
│   │   ├── main_window.cpp                       # Implementación
│   │   ├── main_window.ui                        # Qt Designer — layout principal
│   │   ├── sensor_panel.ui                       # Qt Designer — panel de sensores
│   │   ├── alert_dialog.ui                       # Qt Designer — diálogo de alertas
│   │   ├── config_dialog.ui                      # Qt Designer — configuración
│   │   └── resources.qrc                         # Recursos de UI (iconos, estilos)
│   │
│   ├── qml/                                      # Interfaz QML (pantalla táctil RPi)
│   │   ├── main.qml                              # Ventana raíz
│   │   ├── Dashboard.qml                         # Panel resumen de sensores
│   │   ├── SensorCard.qml                        # Tarjeta individual de sensor
│   │   ├── AlertBanner.qml                       # Banner de alertas activas
│   │   ├── StatusBar.qml                         # WiFi, cloud, uptime, CPU temp
│   │   ├── ConfigScreen.qml                      # Pantalla de configuración
│   │   ├── CalibrationScreen.qml                 # Pantalla de calibración
│   │   └── qmldir                                # Registro de módulos QML
│   │
│   └── tests/                                    # Tests unitarios y de integración
│       ├── CMakeLists.txt                        # Targets CTest
│       ├── test_cli.cpp                          # Tests del parser CLI
│       ├── test_sensor_data.cpp                  # Tests de SensorData
│       ├── test_alert_rule.cpp                   # Tests de AlertRule
│       ├── test_config_loader.cpp                # Tests de ConfigLoader
│       ├── test_json_formatter.cpp               # Tests de JSON
│       ├── test_ds18b20.cpp                      # Tests DS18B20
│       ├── test_dht22.cpp                        # Tests DHT22
│       ├── test_bh1750.cpp                       # Tests BH1750
│       ├── test_soil.cpp                         # Tests Soil
│       ├── test_mhz19c.cpp                       # Tests MHZ19C
│       ├── test_driver_factory.cpp               # Tests DriverFactory
│       ├── test_sysinfo.cpp                      # Tests sysinfo
│       ├── test_gateway_cycle.cpp                # Tests ciclo daemon
│       ├── test_data_store.cpp                   # Tests persistencia
│       └── test_alert_engine.cpp                 # Tests motor de alertas
│
├── bin/                                          # Scripts wrapper
│   └── echosmart-gateway-setup                   # Wrapper legacy (llama `echosmart setup`)
├── debian/                                       # Empaquetado .deb (debhelper 13)
│   ├── control                                   # Metadatos del paquete
│   ├── rules                                     # cmake build + install
│   ├── changelog                                 # Historial de versiones
│   ├── compat                                    # Nivel 13
│   ├── postinst                                  # Post-instalación (usuario, systemd)
│   ├── prerm                                     # Pre-remoción (stop servicio)
│   └── echosmart-gateway.service                 # Unidad systemd: ExecStart=/usr/bin/echosmart run
├── sensors.json                                  # Config sensores por defecto
├── .env.example                                  # Variables de entorno por defecto
└── README.md                                     # Instrucciones build + instalación
```

#### 1.2.1 Build System — CMakeLists.txt
- [ ] Crear `gateway/cpp/CMakeLists.txt` — proyecto raíz
  - [ ] `cmake_minimum_required(VERSION 3.16)`
  - [ ] `project(echosmart VERSION 1.0.0 LANGUAGES CXX)`
  - [ ] `set(CMAKE_CXX_STANDARD 17)` + `CMAKE_CXX_STANDARD_REQUIRED ON`
  - [ ] `find_package(Qt6 COMPONENTS Core Quick Widgets QUIET)` (opcional)
  - [ ] Compilar todas las fuentes en un solo target `echosmart`
  - [ ] `target_sources(echosmart PRIVATE main.cpp cli.cpp commands/*.cpp drivers/*.cpp core/*.cpp shared/*.cpp)`
  - [ ] Si Qt6 encontrado: agregar `ui/*.cpp ui/*.ui qml/*.qml` y `resources.qrc`
  - [ ] `install(TARGETS echosmart RUNTIME DESTINATION bin)`
  - [ ] Opciones: `-DBUILD_QML=ON/OFF`, `-DBUILD_UI=ON/OFF`, `-DBUILD_TESTS=ON/OFF`
  - [ ] Cross-compilación: `CMAKE_TOOLCHAIN_FILE` para arm64
  - [ ] Flags: `-Wall -Wextra -Wpedantic -O2`

#### 1.2.2 Entry Point — `main.cpp` + `cli.h` / `cli.cpp`
- [ ] Crear `gateway/cpp/main.cpp`
  - [ ] `int main(int argc, char* argv[])` — parsear args, dispatch a comando
  - [ ] Si `argc < 2` → imprimir ayuda y salir con código 1
  - [ ] Mapa de comandos: `{"read", "sysinfo", "run", "setup", "status", "calibrate", "list", "test", "version", "help"}`
  - [ ] Dispatch: `cmd_map[argv[1]](argc, argv)` → código de salida
  - [ ] Comando desconocido → `"error: unknown command '<cmd>'. Run 'echosmart help'.\n"` + exit 1
- [ ] Crear `gateway/cpp/cli.h`
  - [ ] `struct CliArgs` con: `std::string command`, `std::string input`, `std::map<std::string, std::string> args`
  - [ ] `CliArgs parse(int argc, char* argv[])` — parser de `echosmart <cmd> <input> --<arg>=<val>`
  - [ ] `std::string getArg(const std::string& name, const std::string& default_val = "")` — obtener arg
  - [ ] `bool hasArg(const std::string& name)` — verificar arg existe
  - [ ] `bool getBool(const std::string& name, bool default_val = false)` — arg como bool
  - [ ] `int getInt(const std::string& name, int default_val = 0)` — arg como entero
- [ ] Crear `gateway/cpp/cli.cpp`
  - [ ] Parser: `argv[1]` = command, `argv[2]` = input (si no empieza con `--`), resto = args `--key=value`
  - [ ] Soportar: `--simulate=true`, `--simulate` (sin valor = true), `--interval=30`
  - [ ] Soportar: `--config=/path/to/file`, `--format=json`
  - [ ] Validar: keys sólo contienen `[a-z0-9-]`, values no vacíos

### 1.3 Biblioteca Compartida (`shared/`)

#### 1.3.1 `version.h`
- [ ] Crear `gateway/cpp/shared/version.h`
  - [ ] `#define ES_VERSION_MAJOR 1`
  - [ ] `#define ES_VERSION_MINOR 0`
  - [ ] `#define ES_VERSION_PATCH 0`
  - [ ] `#define ES_VERSION_STRING "1.0.0"`
  - [ ] `constexpr const char* es_version()` — retorna string de versión

#### 1.3.2 `sensordata.h` / `sensordata.cpp`
- [ ] Crear `gateway/cpp/shared/sensordata.h`
  - [ ] `struct SensorData` con campos: `std::string sensor_type`, `std::string sensor_name`, `double value`, `std::string unit`, `int64_t timestamp_ms`, `bool is_valid`
  - [ ] `static SensorData from_json(const std::string& json)` — parsear JSON de sensor-read
  - [ ] `std::string to_json() const` — serializar a JSON
  - [ ] `static SensorData empty(const std::string& type, const std::string& error)` — lectura inválida
- [ ] Crear `gateway/cpp/shared/sensordata.cpp`
  - [ ] Implementar `from_json()` con parser JSON minimal
  - [ ] Implementar `to_json()` con formato compacto
  - [ ] Implementar `empty()` con `is_valid = false`

#### 1.3.3 `alertrule.h` / `alertrule.cpp`
- [ ] Crear `gateway/cpp/shared/alertrule.h`
  - [ ] `enum class AlertSeverity { INFO, WARNING, CRITICAL }`
  - [ ] `enum class AlertCondition { GT, LT, EQ, RANGE }`
  - [ ] `struct AlertRule` con: `sensor_type`, `condition`, `threshold`, `threshold_low`, `threshold_high`, `severity`, `message`, `cooldown_seconds`
  - [ ] `bool evaluate(const SensorData& reading) const` — evalúa regla
  - [ ] `static std::vector<AlertRule> load_defaults()` — reglas por defecto
  - [ ] `static std::vector<AlertRule> from_json(const std::string& json)` — desde fichero
- [ ] Crear `gateway/cpp/shared/alertrule.cpp`
  - [ ] Implementar `evaluate()` para GT, LT, EQ, RANGE
  - [ ] Implementar `load_defaults()` con umbrales de invernadero
  - [ ] Implementar `from_json()` parser

#### 1.3.4 `jsonformatter.h` / `jsonformatter.cpp`
- [ ] Crear `gateway/cpp/shared/jsonformatter.h`
  - [ ] `std::string json_object(const std::vector<std::pair<std::string, std::string>>& fields)`
  - [ ] `std::string json_string(const std::string& key, const std::string& value)`
  - [ ] `std::string json_number(const std::string& key, double value, int precision)`
  - [ ] `std::string json_int(const std::string& key, int64_t value)`
  - [ ] `std::string json_bool(const std::string& key, bool value)`
  - [ ] `std::string json_array(const std::vector<std::string>& items)`
- [ ] Crear `gateway/cpp/shared/jsonformatter.cpp`
  - [ ] Implementar todas las funciones sin dependencias externas
  - [ ] Escapar caracteres especiales en strings JSON

#### 1.3.5 `configloader.h` / `configloader.cpp`
- [ ] Crear `gateway/cpp/shared/configloader.h`
  - [ ] `struct GatewayConfig` con: `gateway_id`, `gateway_name`, `cloud_api_url`, `cloud_api_key`, `mqtt_broker`, `mqtt_port`, `polling_interval`, `sync_interval`, `simulation_mode`, `log_level`
  - [ ] `static GatewayConfig load(const std::string& env_path)` — parsear gateway.env
  - [ ] `struct SensorEntry` con: `type`, `name`, `device_id`, `pin`, `address`, `channel`, `port`
  - [ ] `static std::vector<SensorEntry> load_sensors(const std::string& json_path)`
- [ ] Crear `gateway/cpp/shared/configloader.cpp`
  - [ ] Implementar parser key=value para `.env`
  - [ ] Implementar parser JSON minimal para `sensors.json`
  - [ ] Valores por defecto si fichero no existe
  - [ ] Validación de campos obligatorios

#### 1.3.6 `logger.h` / `logger.cpp`
- [ ] Crear `gateway/cpp/shared/logger.h`
  - [ ] `enum class LogLevel { DEBUG, INFO, WARNING, ERROR, CRITICAL }`
  - [ ] `void log_debug(const std::string& msg)`
  - [ ] `void log_info(const std::string& msg)`
  - [ ] `void log_warning(const std::string& msg)`
  - [ ] `void log_error(const std::string& msg)`
  - [ ] `void log_critical(const std::string& msg)`
  - [ ] `void set_log_level(LogLevel level)`
  - [ ] `std::string now_iso8601()` — timestamp ISO 8601
- [ ] Crear `gateway/cpp/shared/logger.cpp`
  - [ ] Formato: `2026-03-29T08:00:00 [INFO]  mensaje`
  - [ ] Salida a stdout (INFO+) y stderr (ERROR+)
  - [ ] Filtrado por nivel configurado

#### 1.3.7 `fileutils.h` / `fileutils.cpp`
- [ ] Crear `gateway/cpp/shared/fileutils.h`
  - [ ] `std::string read_file(const std::string& path)`
  - [ ] `bool write_file(const std::string& path, const std::string& content)`
  - [ ] `bool file_exists(const std::string& path)`
  - [ ] `std::string trim(const std::string& s)`
  - [ ] `std::vector<std::string> split(const std::string& s, char delim)`
  - [ ] `std::string get_hostname()`
  - [ ] `std::string get_mac_address()`
- [ ] Crear `gateway/cpp/shared/fileutils.cpp`
  - [ ] Implementar con `<fstream>`, `<filesystem>` (C++17)
  - [ ] `get_mac_address()` lee de `/sys/class/net/eth0/address`

#### 1.3.8 `resources.qrc` (shared)
- [ ] Crear `gateway/cpp/shared/resources.qrc`
  - [ ] Embeber `sensors-schema.json` (schema de validación de sensors.json)
  - [ ] Embeber `default-alerts.json` (reglas de alerta por defecto)
  - [ ] Embeber `version.txt` (versión del build para runtime)

### 1.4 Comando `echosmart read <sensor>` — Lectura de Sensores

#### 1.4.1 `commands/cmd_read.h` / `cmd_read.cpp`
- [ ] Crear `gateway/cpp/commands/cmd_read.h`
  - [ ] `int cmd_read(const CliArgs& args)` — entry point del comando `read`
  - [ ] Validar `args.input` ∈ {ds18b20, dht22, bh1750, soil, mhz19c}
  - [ ] Obtener `--simulate=true|false` (default: false)
  - [ ] Obtener `--format=json|text` (default: json)
- [ ] Crear `gateway/cpp/commands/cmd_read.cpp`
  - [ ] Instanciar driver vía `DriverFactory::create(args.input)`
  - [ ] Llamar `driver->read(simulate)` → `SensorData`
  - [ ] Imprimir resultado según `--format`
  - [ ] Return 0 éxito, 1 sensor desconocido, 2 error de lectura

#### 1.4.2 `drivers/sensor_driver.h` / `sensor_driver.cpp` — Clase base
- [ ] Crear `gateway/cpp/drivers/sensor_driver.h`
  - [ ] `class SensorDriver` (base abstracta)
  - [ ] `virtual SensorData read(bool simulate) = 0`
  - [ ] `virtual std::string sensorType() const = 0`
  - [ ] `virtual std::string protocol() const = 0`
  - [ ] `virtual bool isAvailable() const`
  - [ ] `virtual ~SensorDriver() = default`
- [ ] Crear `gateway/cpp/drivers/sensor_driver.cpp`
  - [ ] `isAvailable()` default: true en simulación
  - [ ] Helper `simulateValue(double lo, double hi)` — random con `<random>`

#### 1.4.3 `drivers/driver_factory.h` / `driver_factory.cpp`
- [ ] Crear `gateway/cpp/drivers/driver_factory.h`
  - [ ] `static std::unique_ptr<SensorDriver> create(const std::string& type)`
  - [ ] `static std::vector<std::string> listTypes()`
- [ ] Crear `gateway/cpp/drivers/driver_factory.cpp`
  - [ ] Mapa: ds18b20, dht22, bh1750, soil, mhz19c → driver class

#### 1.4.4 `drivers/ds18b20_driver.h` / `ds18b20_driver.cpp`
- [ ] Crear `gateway/cpp/drivers/ds18b20_driver.h`
  - [ ] `class DS18B20Driver : public SensorDriver`
  - [ ] `SensorData read(bool simulate) override`
  - [ ] `std::string sensorType()` → `"ds18b20"`, `protocol()` → `"1-wire"`
  - [ ] `std::vector<std::string> listDevices()` — enumerar bus 1-Wire
- [ ] Crear `gateway/cpp/drivers/ds18b20_driver.cpp`
  - [ ] Simulación: random 15.0–35.0 °C
  - [ ] Real: parsear `/sys/bus/w1/devices/{id}/w1_slave`, campo `t=XXXXX`
  - [ ] Validación: rechazar < -55 o > 125

#### 1.4.5 `drivers/dht22_driver.h` / `dht22_driver.cpp`
- [ ] Crear `gateway/cpp/drivers/dht22_driver.h`
  - [ ] `class DHT22Driver : public SensorDriver`
  - [ ] `SensorData read(bool simulate) override`
  - [ ] `double lastHumidity() const`
- [ ] Crear `gateway/cpp/drivers/dht22_driver.cpp`
  - [ ] Simulación: temp 15–35, humidity 40–90
  - [ ] Real: GPIO con libgpiod, CRC8 checksum, rate limit ≥2s

#### 1.4.6 `drivers/bh1750_driver.h` / `bh1750_driver.cpp`
- [ ] Crear `gateway/cpp/drivers/bh1750_driver.h`
  - [ ] `class BH1750Driver : public SensorDriver`
  - [ ] Constructor con `i2c_bus=1, address=0x23`
- [ ] Crear `gateway/cpp/drivers/bh1750_driver.cpp`
  - [ ] Simulación: random 100–50000 lux
  - [ ] Real: `ioctl(I2C_SLAVE, 0x23)`, write 0x10, read 2 bytes

#### 1.4.7 `drivers/soil_driver.h` / `soil_driver.cpp`
- [ ] Crear `gateway/cpp/drivers/soil_driver.h`
  - [ ] `class SoilDriver : public SensorDriver`
  - [ ] `void calibrate(int dry_raw, int wet_raw)`
  - [ ] `double rawToPercent(int raw) const`
- [ ] Crear `gateway/cpp/drivers/soil_driver.cpp`
  - [ ] Simulación: random 10–95%
  - [ ] Real: ADS1115 via I2C, lineal `(raw-dry)/(wet-dry)*100`, clamp 0–100

#### 1.4.8 `drivers/mhz19c_driver.h` / `mhz19c_driver.cpp`
- [ ] Crear `gateway/cpp/drivers/mhz19c_driver.h`
  - [ ] `class MHZ19CDriver : public SensorDriver`
  - [ ] `bool sendCalibration()`, `bool isWarmedUp() const`
- [ ] Crear `gateway/cpp/drivers/mhz19c_driver.cpp`
  - [ ] Simulación: random 400–2000 ppm
  - [ ] Real: UART termios, cmd `{0xFF,0x01,0x86,...}`, checksum, timeout 5s

### 1.5 Comando `echosmart sysinfo` — Diagnósticos del Sistema

#### 1.5.1 `commands/cmd_sysinfo.h` / `cmd_sysinfo.cpp`
- [ ] Crear `gateway/cpp/commands/cmd_sysinfo.h`
  - [ ] `int cmd_sysinfo(const CliArgs& args)`
  - [ ] `--format=json|text` (default: json)
- [ ] Crear `gateway/cpp/commands/cmd_sysinfo.cpp`
  - [ ] Instanciar `SysInfo`, `collect()`, imprimir según formato

#### 1.5.2 `commands/sysinfo.h` / `sysinfo.cpp`
- [ ] Crear `gateway/cpp/commands/sysinfo.h`
  - [ ] `struct SystemInfo` — hostname, model, cpu_temp, uptime, load, mem, disk, version
  - [ ] `class SysInfo` — `collect()`, `toJson()`, `toText()`
- [ ] Crear `gateway/cpp/commands/sysinfo.cpp`
  - [ ] Leer `/etc/hostname`, `/proc/device-tree/model`, `/sys/class/thermal/thermal_zone0/temp`
  - [ ] Leer `/proc/uptime`, `/proc/loadavg`, `/proc/meminfo`
  - [ ] Usar `statvfs("/")` para disco

### 1.6 Comando `echosmart run` — Daemon Principal

#### 1.6.1 `commands/cmd_run.h` / `cmd_run.cpp`
- [ ] Crear `gateway/cpp/commands/cmd_run.h`
  - [ ] `int cmd_run(const CliArgs& args)`
  - [ ] Args: `--config=`, `--sensors=`, `--simulate=`, `--once=`, `--interval=`
- [ ] Crear `gateway/cpp/commands/cmd_run.cpp`
  - [ ] Signal handlers: SIGINT/SIGTERM → `g_running = false`
  - [ ] Cargar config + sensors, instanciar Gateway, `run()` o `runOnce()`

#### 1.6.2 Comandos adicionales
- [ ] `commands/cmd_setup.h/.cpp` — wizard interactivo, escribe `/etc/echosmart/gateway.env`
- [ ] `commands/cmd_status.h/.cpp` — sysinfo + última lectura de cada sensor
- [ ] `commands/cmd_calibrate.h/.cpp` — `echosmart calibrate soil --dry=3200 --wet=1400`
- [ ] `commands/cmd_list.h/.cpp` — listar sensores de `sensors.json`
- [ ] `commands/cmd_test.h/.cpp` — probar sensores, imprimir PASS/FAIL
- [ ] `commands/cmd_version.h/.cpp` — `"echosmart v{ES_VERSION_STRING}\n"`
- [ ] `commands/cmd_help.h/.cpp` — ayuda general o por comando

#### 1.6.3 `core/gateway.h` / `core/gateway.cpp`
- [ ] Crear `gateway/cpp/core/gateway.h`
  - [ ] `class Gateway` — `run()`, `runOnce()`, `shutdown()`, `pollCount()`, `isRunning()`
- [ ] Crear `gateway/cpp/core/gateway.cpp`
  - [ ] `runOnce()`: pollAll → evaluate → save → sync

#### 1.6.4 `core/sensor_poller.h` / `core/sensor_poller.cpp`
- [ ] Crear `gateway/cpp/core/sensor_poller.h` / `.cpp`
  - [ ] `poll(SensorEntry)` — instanciar driver, leer, retornar SensorData
  - [ ] `pollAll(vector<SensorEntry>)` — iterar, log errores
  - [ ] Timeout 10s por sensor

#### 1.6.5 `core/alert_engine.h` / `core/alert_engine.cpp`
- [ ] Crear `gateway/cpp/core/alert_engine.h` / `.cpp`
  - [ ] `evaluate(SensorData)` — evaluar reglas, cooldown, retornar alertas

#### 1.6.6 `core/data_store.h` / `core/data_store.cpp`
- [ ] Crear `gateway/cpp/core/data_store.h` / `.cpp`
  - [ ] `save()`, `saveAlert()`, `getUnsynced()`, `cleanup()`, `pendingCount()`
  - [ ] Ficheros JSONL rotativos: `readings-YYYYMMDD.jsonl`

#### 1.6.7 `core/cloud_syncer.h` / `core/cloud_syncer.cpp`
- [ ] Crear `gateway/cpp/core/cloud_syncer.h` / `.cpp`
  - [ ] `sync(vector<SensorData>)` — HTTP POST batch, retry backoff

#### 1.6.8 `core/mqtt_publisher.h` / `core/mqtt_publisher.cpp`
- [ ] Crear `gateway/cpp/core/mqtt_publisher.h` / `.cpp`
  - [ ] `connect()`, `publish(SensorData)`, `disconnect()`, LWT

### 1.6b Interfaz Gráfica Qt (opcional, BUILD_UI=ON / BUILD_QML=ON)

#### 1.6b.1 Formularios `.ui` (Qt Designer)
- [ ] Crear `gateway/cpp/ui/main_window.ui` — layout con tabs
- [ ] Crear `gateway/cpp/ui/sensor_panel.ui` — tabla de sensores live
- [ ] Crear `gateway/cpp/ui/alert_dialog.ui` — alertas activas
- [ ] Crear `gateway/cpp/ui/config_dialog.ui` — configuración
- [ ] Crear `gateway/cpp/ui/main_window.h` / `main_window.cpp`
- [ ] Crear `gateway/cpp/ui/resources.qrc` — iconos y estilos

#### 1.6b.2 Interfaz QML (pantalla táctil)
- [ ] Crear `gateway/cpp/qml/main.qml` — ApplicationWindow + StackView
- [ ] Crear `gateway/cpp/qml/Dashboard.qml` — grid de SensorCard
- [ ] Crear `gateway/cpp/qml/SensorCard.qml` — valor, unidad, estado, sparkline
- [ ] Crear `gateway/cpp/qml/AlertBanner.qml` — alertas con severidad
- [ ] Crear `gateway/cpp/qml/StatusBar.qml` — WiFi, cloud, uptime, CPU
- [ ] Crear `gateway/cpp/qml/ConfigScreen.qml` — configuración
- [ ] Crear `gateway/cpp/qml/CalibrationScreen.qml` — calibración
- [ ] Crear `gateway/cpp/qml/qmldir` — registro de módulos

### 1.7 Tests Unitarios y de Integración (CTest)

#### 1.7.1 Tests de la biblioteca compartida
- [ ] Crear `gateway/cpp/tests/CMakeLists.txt`
  - [ ] `enable_testing()`
  - [ ] `add_executable` + `add_test` para cada test
  - [ ] Linkear contra `echosmart-shared`
- [ ] Crear `gateway/cpp/tests/test_sensordata.cpp`
  - [ ] Test: `SensorData::to_json()` produce JSON válido
  - [ ] Test: `SensorData::from_json()` parsea correctamente
  - [ ] Test: `SensorData::empty()` tiene `is_valid = false`
  - [ ] Test: round-trip `to_json()` → `from_json()` preserva datos
  - [ ] Test: caracteres especiales en nombre se escapan
- [ ] Crear `gateway/cpp/tests/test_alertrule.cpp`
  - [ ] Test: `AlertRule` con condición GT evalúa correctamente
  - [ ] Test: `AlertRule` con condición LT evalúa correctamente
  - [ ] Test: `AlertRule` con condición EQ evalúa correctamente
  - [ ] Test: `AlertRule` con condición RANGE evalúa correctamente
  - [ ] Test: `AlertRule` no genera alerta si valor está dentro del rango
  - [ ] Test: `load_defaults()` retorna reglas con umbrales válidos
- [ ] Crear `gateway/cpp/tests/test_configloader.cpp`
  - [ ] Test: cargar gateway.env válido
  - [ ] Test: cargar gateway.env con comentarios y líneas vacías
  - [ ] Test: valores por defecto si fichero no existe
  - [ ] Test: cargar sensors.json con 5 sensores
  - [ ] Test: cargar sensors.json vacío retorna lista por defecto
  - [ ] Test: campo faltante usa valor por defecto
- [ ] Crear `gateway/cpp/tests/test_jsonformatter.cpp`
  - [ ] Test: `json_object()` produce objeto válido
  - [ ] Test: `json_string()` escapa comillas y backslashes
  - [ ] Test: `json_number()` respeta precision
  - [ ] Test: `json_array()` con 0, 1, N elementos
  - [ ] Test: `json_bool()` produce true/false

#### 1.7.2 Tests de drivers de sensores
- [ ] Crear `gateway/cpp/tests/test_ds18b20driver.cpp`
  - [ ] Test: `read(simulate=true)` retorna valor entre 15 y 35
  - [ ] Test: `sensorType()` retorna `"ds18b20"`
  - [ ] Test: `protocol()` retorna `"1-wire"`
  - [ ] Test: valor fuera de rango [-55, 125] se rechaza
  - [ ] Test: `listDevices()` en directorio mock
- [ ] Crear `gateway/cpp/tests/test_dht22driver.cpp`
  - [ ] Test: `read(simulate=true)` retorna temp y humidity válidos
  - [ ] Test: `sensorType()` retorna `"dht22"`
  - [ ] Test: temp en rango [-40, 80], humidity en [0, 100]
  - [ ] Test: `lastHumidity()` retorna último valor leído
- [ ] Crear `gateway/cpp/tests/test_bh1750driver.cpp`
  - [ ] Test: `read(simulate=true)` retorna valor entre 100 y 50000
  - [ ] Test: `sensorType()` retorna `"bh1750"`
  - [ ] Test: valor > 65535 se descarta
- [ ] Crear `gateway/cpp/tests/test_soildriver.cpp`
  - [ ] Test: `read(simulate=true)` retorna valor entre 10 y 95
  - [ ] Test: `sensorType()` retorna `"soil_moisture"`
  - [ ] Test: `calibrate()` ajusta mapeo crudo → porcentaje
  - [ ] Test: `rawToPercent()` clamp a [0, 100]
- [ ] Crear `gateway/cpp/tests/test_mhz19cdriver.cpp`
  - [ ] Test: `read(simulate=true)` retorna valor entre 400 y 2000
  - [ ] Test: `sensorType()` retorna `"mhz19c"`
  - [ ] Test: checksum validation correcto e incorrecto
  - [ ] Test: `isWarmedUp()` retorna false antes de 3 min

#### 1.7.3 Tests del daemon
- [ ] Crear `gateway/cpp/tests/test_sysinfo.cpp`
  - [ ] Test: `collect()` retorna todos los campos no vacíos
  - [ ] Test: `toJson()` produce JSON válido
  - [ ] Test: `toText()` produce texto legible
  - [ ] Test: `cpu_temp_c` es razonable (> -50, < 120)
- [ ] Crear `gateway/cpp/tests/test_gateway_cycle.cpp`
  - [ ] Test: `Gateway::runOnce()` completa un ciclo sin error
  - [ ] Test: `Gateway::pollCount()` incrementa después de cada ciclo
  - [ ] Test: `Gateway::shutdown()` establece `isRunning() = false`
  - [ ] Test: alertas se generan cuando valor excede umbral
  - [ ] Test: ciclo con sensores vacíos no crashea
- [ ] Crear `gateway/cpp/tests/test_datastore.cpp`
  - [ ] Test: `save()` crea fichero JSONL
  - [ ] Test: `saveAlert()` crea fichero de alertas
  - [ ] Test: `getUnsynced()` retorna lecturas guardadas
  - [ ] Test: `cleanup()` elimina ficheros viejos
  - [ ] Test: `pendingCount()` retorna conteo correcto

#### 1.7.4 Tests de integración (binarios compilados)
- [ ] Test de integración: compilar todos los binarios → verificar exit code 0
- [ ] Test de integración: `echosmart sysinfo --version=true` → contiene "1.0.0"
- [ ] Test de integración: `echosmart read ds18b20 --simulate=true` → JSON con "sensor":"ds18b20"
- [ ] Test de integración: `echosmart read dht22 --simulate=true` → JSON con "temperature" y "humidity"
- [ ] Test de integración: `echosmart read bh1750 --simulate=true` → JSON con "sensor":"bh1750"
- [ ] Test de integración: `echosmart read soil --simulate=true` → JSON con "sensor":"soil_moisture"
- [ ] Test de integración: `echosmart read mhz19c --simulate=true` → JSON con "sensor":"mhz19c"
- [ ] Test de integración: `echosmart read invalid_sensor` → exit code ≠ 0
- [ ] Test de integración: `echosmart run --simulate=true --once=true` → log "polling cycle start" y "polling cycle end"
- [ ] Test de integración: `echosmart version` → contiene "1.0.0"
- [ ] Test de integración: verificar .deb se construye sin errores

### 1.8 Comunicaciones (MQTT + HTTP Sync)

- [ ] Implementar `mqttpublisher.h` / `mqttpublisher.cpp`:
  - [ ] `MqttPublisher::MqttPublisher(broker, port, gateway_id)` — constructor
  - [ ] `MqttPublisher::connect()` — conectar al broker MQTT
  - [ ] `MqttPublisher::publish(const SensorData&)` — publicar lectura en topic
  - [ ] `MqttPublisher::publishAlert(const std::string&)` — publicar alerta
  - [ ] `MqttPublisher::disconnect()` — desconexión limpia
  - [ ] `MqttPublisher::isConnected() const` — estado de conexión
  - [ ] Topics: `echosmart/{gw_id}/sensors/{type}/reading`
  - [ ] Topic alertas: `echosmart/{gw_id}/alerts`
  - [ ] LWT: `echosmart/{gw_id}/status` → `"offline"`
- [ ] Implementar `cloudsyncer.h` / `cloudsyncer.cpp`:
  - [ ] `CloudSyncer::CloudSyncer(api_url, api_key, gateway_id)` — constructor
  - [ ] `CloudSyncer::sync(vector<SensorData>)` — HTTP POST batch
  - [ ] `CloudSyncer::isOnline() const` — último sync < 5 min
  - [ ] `CloudSyncer::failedAttempts() const` — contador de fallos
  - [ ] Retry con backoff exponencial (1s, 2s, 4s... max 5 min)
  - [ ] HTTP vía `libcurl` o `popen("curl ...")` como fallback
- [ ] Implementar reconexión automática MQTT con backoff
- [ ] Implementar QoS configurable: 0 (at most once), 1 (at least once), 2 (exactly once)
- [ ] Implementar TLS/SSL para comunicación MQTT segura
- [ ] Implementar offline queue: almacenar datos localmente si no hay conexión
- [ ] Tests: publicación MQTT mock, sync HTTP mock, retry, offline queue

### 1.9 Empaquetado .deb del Gateway

#### 1.9.1 Metadatos Debian
- [ ] Actualizar `gateway/debian/control` con dependencias Qt opcionales
- [ ] Actualizar `gateway/debian/rules` con cmake + install de todos los binarios
- [ ] Actualizar `gateway/debian/postinst` con creación de usuario y directorios
- [ ] Actualizar `gateway/debian/prerm` con stop y disable de servicio

#### 1.9.2 Contenido del .deb
- [ ] `/usr/bin/echosmart` — binario unificado del gateway
- [ ] 
- [ ] `/usr/bin/echosmart sysinfo` — diagnósticos del sistema (C++)
- [ ] `/usr/bin/echosmart read` — lectura de sensores (C++)
- [ ] `/usr/bin/echosmart setup` — wizard de configuración (bash)
- [ ] `/etc/echosmart/gateway.env` — configuración por defecto (conffile)
- [ ] `/etc/echosmart/sensors.json` — definición de sensores (conffile)
- [ ] `/lib/systemd/system/echosmart-gateway.service` — unidad systemd

#### 1.9.3 Verificación del .deb
- [ ] Build nativo: `dpkg-buildpackage -b -us -uc` → exit 0
- [ ] Build cross: `dpkg-buildpackage -b -us -uc --host-arch=arm64` → exit 0
- [ ] Lintian: `lintian echosmart-gateway_*.deb` → sin errores E:
- [ ] Instalar: `dpkg -i echosmart-gateway_*.deb` → exit 0
- [ ] Listar ficheros: `dpkg -L echosmart-gateway` → 8 rutas esperadas
- [ ] Servicio: `systemctl status echosmart-gateway` → loaded
- [ ] Desinstalar: `dpkg -r echosmart-gateway` → limpio

### 1.10 Auto-descubrimiento y API Local

- [ ] Implementar mDNS/Zeroconf para descubrimiento en red local
- [ ] Implementar API REST local ligera en el gateway (puerto 8080)
  - [ ] `GET /api/status` — invoca `echosmart sysinfo`, retorna JSON
  - [ ] `GET /api/readings` — últimas lecturas de cada sensor
  - [ ] `GET /api/config` — lee `/etc/echosmart/gateway.env`
  - [ ] `POST /api/config` — actualiza configuración y reinicia servicio
  - [ ] `POST /api/restart` — `systemctl restart echosmart-gateway` (servicio systemd)
- [ ] Identificación del gateway: hostname, MAC, serial, versión
- [ ] Tests: descubrimiento, API local, actualización de config

### 1.11 Gateway — Calidad de Código

- [ ] Crear `gateway/cpp/.clang-format` con estilo Google, IndentWidth 4, ColumnLimit 100
- [ ] Configurar `cppcheck` para análisis estático de `gateway/cpp/`
- [ ] Agregar CI step: compilar con `-Wall -Wextra -Wpedantic` → 0 warnings
- [ ] Agregar CI step: ejecutar `cppcheck --error-exitcode=1`
- [ ] Agregar CI step: ejecutar CTest → todos los tests pasan
- [ ] Agregar CI step: construir .deb sin errores
- [ ] Crear `gateway/README.md` con:
  - [ ] Requisitos de build (cmake ≥ 3.16, g++ ≥ 10, qt6 opcional)
  - [ ] Instrucciones de compilación: `cmake -S cpp -B build && cmake --build build`
  - [ ] Instrucciones de testing: `ctest --test-dir build --output-on-failure`
  - [ ] Instrucciones de empaquetado: `cd gateway && dpkg-buildpackage -b -us -uc`
  - [ ] Tabla de binarios con todos sus flags y sub-comandos
  - [ ] Tabla de archivos `.h`, `.cpp`, `.qml`, `.qrc`, `.ui` con descripción

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

## Fase 3: Frontend Web — React + TypeScript (Semanas 8–10)

> 🏛️ **Clean Architecture en Frontend**: Separar UI (componentes) de lógica de negocio (hooks/store) y acceso a datos (API client). Los componentes NO deben hacer fetch directamente.

> 🎯 **Stack Definido**: React 18 + Vite + TypeScript + Tailwind CSS + Redux Toolkit + React Router v6 + Recharts + Vitest. El resultado debe ser visualmente idéntico a los mockups en `assets/mockups/web/`.

### 3.1 Definición de Tecnologías y Justificación

| Tecnología | Versión | Justificación |
|------------|---------|---------------|
| **React 18** | ^18.2.0 | Biblioteca UI más popular, amplio ecosistema, hooks, concurrent features |
| **TypeScript** | ^5.3.0 | Type safety obligatorio para Clean Code, autocompletado, refactoring seguro |
| **Vite** | ^5.0.0 | Build tool rápido (ESBuild + Rollup), HMR instantáneo, configuración mínima |
| **Tailwind CSS** | ^3.4.0 | Utility-first CSS, design tokens, purge automático, responsive |
| **Redux Toolkit** | ^2.0.0 | Estado global predecible, DevTools, middleware, createAsyncThunk |
| **React Router** | ^6.20.0 | Routing declarativo, nested routes, lazy loading, data loaders |
| **Recharts** | ^2.10.0 | Gráficas declarativas basadas en React, responsive, customizable |
| **Axios** | ^1.6.0 | HTTP client con interceptors, cancel tokens, retry |
| **React Query** | ^5.0.0 | Server state management, cache, refetch, pagination |
| **Vitest** | ^1.0.0 | Testing rápido compatible con Vite, API compatible con Jest |
| **Testing Library** | ^14.0.0 | Tests centrados en el usuario, no en implementación |
| **Storybook** | ^7.6.0 | Documentación visual de componentes, design system |

- [ ] Migrar proyecto de JSX a TSX (`.jsx` → `.tsx`, `.js` → `.ts`)
- [ ] Configurar `tsconfig.json` con strict mode habilitado
- [ ] Instalar y configurar Tailwind CSS con design tokens personalizados
- [ ] Instalar React Query para server state (reemplazar fetch directo)
- [ ] Instalar Storybook para design system

### 3.2 Configuración del Proyecto y Tooling

- [x] Inicializar proyecto React 18 con Vite en `frontend/`
- [x] Configurar Redux Toolkit, React Router, i18n
- [ ] Configurar TypeScript strict mode:
  - [ ] `strict: true`, `noImplicitAny: true`, `strictNullChecks: true`
  - [ ] `noUnusedLocals: true`, `noUnusedParameters: true`
- [ ] Configurar Tailwind CSS con design tokens de EchoSmart:
  - [ ] Colores: `bg-black` (#000), `surface` (#111), `elevated` (#1A1A1A), `accent-green` (#00E676), `accent-cyan` (#00BCD4)
  - [ ] Colores de sensores: `sensor-temp` (#FF5252), `sensor-humidity` (#42A5F5), `sensor-light` (#FFD54F), `sensor-soil` (#8D6E63), `sensor-co2` (#78909C)
  - [ ] Colores de alertas: `alert-critical` (#FF1744), `alert-high` (#FF9100), `alert-medium` (#FFD600), `alert-low` (#00E676)
  - [ ] Tipografía: Inter (UI) / JetBrains Mono (datos)
  - [ ] Spacing scale, border radius (`rounded-lg` = 12px), shadows
  - [ ] Dark mode como default (no toggle necesario)
- [x] Configurar cliente HTTP (Axios) con JWT
- [ ] Configurar ESLint con reglas estrictas:
  - [ ] `@typescript-eslint/parser` — Parser TypeScript
  - [ ] `@typescript-eslint/eslint-plugin` — Reglas TypeScript
  - [ ] `eslint-plugin-react` — Reglas de React
  - [ ] `eslint-plugin-react-hooks` — Reglas de hooks
  - [ ] `eslint-plugin-import` — Orden de imports
  - [ ] `eslint-plugin-jsx-a11y` — Accesibilidad
  - [ ] `no-console` en producción (solo `logger`)
  - [ ] `no-any` — Prohibir `any` en TypeScript
- [ ] Configurar Prettier (100 chars, single quotes, trailing comma)
- [ ] Configurar `husky` + `lint-staged` para pre-commit
- [ ] Configurar path aliases en `tsconfig.json` y `vite.config.ts`:
  - [ ] `@/components` → `src/shared/components`
  - [ ] `@/hooks` → `src/shared/hooks`
  - [ ] `@/store` → `src/store`
  - [ ] `@/api` → `src/lib/api-client`
  - [ ] `@/utils` → `src/shared/utils`
  - [ ] `@/features` → `src/features`
  - [ ] `@/assets` → `src/assets`
  - [ ] `@/types` → `src/types`
- [ ] Configurar variables de entorno (`.env.development`, `.env.production`):
  - [ ] `VITE_API_URL` — URL del backend
  - [ ] `VITE_WS_URL` — URL del WebSocket
  - [ ] `VITE_APP_NAME` — Nombre de la app
  - [ ] `VITE_APP_VERSION` — Versión
- [ ] Configurar proxy para desarrollo en `vite.config.ts` (→ backend :8000)
- [ ] Configurar PWA con `vite-plugin-pwa`:
  - [ ] `manifest.json` con iconos de `assets/platform/web/`
  - [ ] Service worker con cache-first strategy
  - [ ] Offline fallback page

### 3.3 Estructura de Archivos (Feature-Based)

```
frontend/src/
├── features/
│   ├── auth/
│   │   ├── components/         # LoginForm.tsx, ForgotPasswordForm.tsx
│   │   ├── hooks/              # useAuth.ts, useLogin.ts
│   │   ├── pages/              # LoginPage.tsx, ResetPasswordPage.tsx
│   │   ├── api.ts              # Auth API calls
│   │   ├── auth.slice.ts       # Redux slice
│   │   └── types.ts            # AuthUser, LoginRequest, etc.
│   ├── dashboard/
│   │   ├── components/         # MetricCard.tsx, SensorChart.tsx, AlertWidget.tsx
│   │   ├── hooks/              # useDashboardData.ts, useRealTimeReadings.ts
│   │   ├── pages/              # DashboardPage.tsx
│   │   ├── api.ts
│   │   └── types.ts
│   ├── sensors/
│   │   ├── components/         # SensorGrid.tsx, SensorCard.tsx, SensorDetail.tsx, ReadingChart.tsx
│   │   ├── hooks/              # useSensors.ts, useSensorReadings.ts
│   │   ├── pages/              # SensorsPage.tsx, SensorDetailPage.tsx
│   │   ├── api.ts
│   │   ├── sensor.slice.ts
│   │   └── types.ts
│   ├── alerts/
│   │   ├── components/         # AlertList.tsx, AlertCard.tsx, RuleEditor.tsx
│   │   ├── hooks/              # useAlerts.ts, useAlertRules.ts
│   │   ├── pages/              # AlertsPage.tsx
│   │   ├── api.ts
│   │   ├── alert.slice.ts
│   │   └── types.ts
│   ├── map/
│   │   ├── components/         # GreenhouseMap.tsx, SensorMarker.tsx, ZoneOverlay.tsx, HeatmapLayer.tsx
│   │   ├── hooks/              # useMapData.ts
│   │   ├── pages/              # MapPage.tsx
│   │   └── types.ts
│   ├── reports/
│   │   ├── components/         # ReportForm.tsx, ReportList.tsx, ReportPreview.tsx
│   │   ├── hooks/              # useReports.ts
│   │   ├── pages/              # ReportsPage.tsx
│   │   └── types.ts
│   ├── gateways/
│   │   ├── components/         # GatewayCard.tsx, GatewayDetail.tsx, GatewayStatus.tsx
│   │   ├── hooks/              # useGateways.ts
│   │   ├── pages/              # GatewaysPage.tsx, GatewayDetailPage.tsx
│   │   └── types.ts
│   ├── settings/
│   │   ├── components/         # ProfileForm.tsx, NotificationPrefs.tsx, ThemeSettings.tsx
│   │   ├── pages/              # SettingsPage.tsx
│   │   └── types.ts
│   └── admin/
│       ├── components/         # UserTable.tsx, GatewayTable.tsx, TenantForm.tsx
│       ├── hooks/              # useUsers.ts, useGateways.ts
│       ├── pages/              # UsersPage.tsx, GatewaysPage.tsx, TenantPage.tsx
│       └── types.ts
├── shared/
│   ├── components/             # Button, Input, Modal, Table, Card, Badge, Spinner, Empty
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Spinner.tsx
│   │   ├── EmptyState.tsx
│   │   ├── Toast.tsx
│   │   ├── Breadcrumb.tsx
│   │   ├── Tabs.tsx
│   │   ├── Tooltip.tsx
│   │   ├── Avatar.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── DataGrid.tsx
│   │   ├── DatePicker.tsx
│   │   ├── Chart.tsx
│   │   ├── SensorIcon.tsx
│   │   ├── StatusDot.tsx
│   │   └── index.ts            # Barrel export
│   ├── hooks/                  # useDebounce, usePagination, useLocalStorage
│   ├── layouts/                # MainLayout, AuthLayout
│   └── utils/                  # formatters, validators, constants
├── lib/
│   ├── api-client.ts           # Axios instance + interceptors
│   ├── websocket.ts            # WebSocket manager
│   ├── storage.ts              # LocalStorage helpers
│   ├── logger.ts               # Frontend logger
│   └── query-client.ts         # React Query config
├── store/                      # Redux store configuration
├── types/                      # Shared TypeScript types
│   ├── sensor.types.ts
│   ├── alert.types.ts
│   ├── user.types.ts
│   ├── gateway.types.ts
│   └── api.types.ts
├── i18n/                       # Traducciones (es, en)
├── theme/                      # Design tokens
│   ├── tokens.ts               # Colores, tipografía, espaciado
│   └── tailwind.config.ts      # Extensión Tailwind
├── assets/                     # Copia de assets relevantes para build
│   ├── icons/                  # SVGs de sensores, nav, logos
│   └── images/                 # Ilustraciones
└── App.tsx
```

- [ ] Crear estructura de features según diagrama anterior
- [ ] Crear archivo `types/` para cada entidad del dominio
- [ ] Mover componentes existentes a estructura feature-based
- [ ] Crear barrel exports (`index.ts`) en cada directorio de feature
- [ ] Verificar que no hay imports circulares con `eslint-plugin-import`
- [ ] Copiar iconos SVG relevantes de `assets/icons/svg/` a `frontend/src/assets/`

### 3.4 Design System — Componentes Compartidos con Storybook

> 🏛️ Componentes reutilizables SIN lógica de negocio. Solo UI pura. Props → render. Cada componente tiene story en Storybook.

- [ ] **Configurar Storybook** para documentar el design system:
  - [ ] Instalar `@storybook/react-vite`
  - [ ] Configurar tema dark en Storybook (que coincida con la app)
  - [ ] Crear stories para CADA componente compartido
  - [ ] Documentar props, variantes y estados
- [ ] **Button** (`Button.tsx`):
  - [ ] Props: `variant` (primary/secondary/danger/ghost/icon-only), `size` (sm/md/lg), `loading`, `disabled`, `icon`, `fullWidth`
  - [ ] Primary: bg `#00E676`, text black, hover más claro
  - [ ] Secondary: bg `#1A1A1A`, border `#2A2A2A`, text white
  - [ ] Danger: bg `#FF1744`, text white
  - [ ] Ghost: bg transparent, text `#B0BEC5`, hover bg `#1A1A1A`
  - [ ] Loading: spinner inline, deshabilitar click
  - [ ] Story: todas las variantes y estados
  - [ ] Tests: render, click, disabled, loading
- [ ] **Input** (`Input.tsx`):
  - [ ] Props: `type` (text/password/email/number/search), `label`, `error`, `hint`, `icon`, `clearable`
  - [ ] Fondo: `#1A1A1A`, borde: `#2A2A2A`, focus border: `#00E676`
  - [ ] Error: borde `#FF1744`, mensaje debajo en rojo
  - [ ] Icon: ícono a la izquierda del input
  - [ ] Tests: render, input, validation, clear
- [ ] **Select** (`Select.tsx`):
  - [ ] Props: `options`, `value`, `onChange`, `searchable`, `multi`, `clearable`, `placeholder`
  - [ ] Dropdown con fondo `#111111`, items hover `#222222`
  - [ ] Searchable: input de búsqueda en el dropdown
  - [ ] Multi: chips con X para remover
  - [ ] Tests: selección, búsqueda, multi-select
- [ ] **Modal** (`Modal.tsx`):
  - [ ] Props: `isOpen`, `onClose`, `title`, `size` (sm/md/lg/fullscreen), `footer`
  - [ ] Overlay oscuro, card con fondo `#111111`
  - [ ] Close: click overlay, tecla Escape, botón X
  - [ ] Animación: fade in + scale
  - [ ] Tests: open, close, overlay click, escape
- [ ] **Table** (`Table.tsx`):
  - [ ] Props: `columns`, `data`, `sortable`, `selectable`, `pagination`, `emptyMessage`
  - [ ] Header: fondo `#1A1A1A`, texto `#B0BEC5`
  - [ ] Rows: hover `#111111`, zebra striping sutil
  - [ ] Sortable: click en header para ordenar, indicador ↑↓
  - [ ] Selectable: checkbox en cada fila, selección batch
  - [ ] Pagination: controls abajo con total, página actual, items/page
  - [ ] Tests: render, sort, select, pagination
- [ ] **Card** (`Card.tsx`):
  - [ ] Props: `title`, `subtitle`, `actions`, `onClick`, `hoverable`, `padding`
  - [ ] Fondo `#111111`, border-radius 12px, sin bordes visibles
  - [ ] Hover: sombra sutil o bg `#1A1A1A`
  - [ ] Tests: render, click, hover
- [ ] **Badge** (`Badge.tsx`):
  - [ ] Props: `variant` (success/warning/danger/info/neutral), `dot`, `count`
  - [ ] Colores según variante, pill shape
  - [ ] Dot: solo círculo de color sin texto
  - [ ] Count: número dentro del badge (para notificaciones)
- [ ] **Spinner** (`Spinner.tsx`):
  - [ ] Props: `size` (sm/md/lg), `fullPage`, `text`
  - [ ] Animación de rotación suave en `#00E676`
  - [ ] fullPage: overlay con spinner centrado
- [ ] **EmptyState** (`EmptyState.tsx`):
  - [ ] Props: `icon` (SVG ilustración), `title`, `description`, `action` (CTA button)
  - [ ] Usar ilustraciones de `assets/icons/svg/illustrations/`
  - [ ] Centrado vertical y horizontal
- [ ] **Toast** (`Toast.tsx` + `useToast` hook):
  - [ ] Props: `variant` (success/error/warning/info), `message`, `duration`, `action`
  - [ ] Stack de toasts en esquina superior derecha
  - [ ] Auto-dismiss configurable (default 5s)
  - [ ] Animación: slide in desde la derecha
- [ ] **Breadcrumb** (`Breadcrumb.tsx`):
  - [ ] Props: `items` array con `{label, href}`
  - [ ] Separador: `/` en color `#616161`
  - [ ] Último item sin link (página actual)
- [ ] **Tabs** (`Tabs.tsx`):
  - [ ] Props: `tabs`, `activeTab`, `onChange`
  - [ ] Indicador animado debajo del tab activo en `#00E676`
  - [ ] Contenido por tab
- [ ] **Tooltip** (`Tooltip.tsx`):
  - [ ] Props: `content`, `position` (top/bottom/left/right), `delay`
  - [ ] Fondo `#1A1A1A`, texto blanco, arrow
- [ ] **Avatar** (`Avatar.tsx`):
  - [ ] Props: `src`, `name`, `size`, `status` (online/offline)
  - [ ] Fallback: iniciales del nombre sobre fondo verde
  - [ ] Status dot en esquina inferior derecha
- [ ] **Sidebar** (`Sidebar.tsx`):
  - [ ] Props: `items`, `collapsed`, `onToggle`
  - [ ] Fondo `#0A0A0A`, items con iconos de `assets/icons/svg/navigation/`
  - [ ] Active item: fondo `#111111`, borde izquierdo `#00E676`
  - [ ] Collapsed: solo iconos, hover muestra tooltip con label
  - [ ] Logo EchoSmart en la parte superior
  - [ ] Tests: navigation, collapse, active state
- [ ] **Header** (`Header.tsx`):
  - [ ] Props: `user`, `notifications`
  - [ ] Breadcrumb en la izquierda
  - [ ] Campana de notificaciones con badge de conteo
  - [ ] Avatar con dropdown: perfil, settings, logout
  - [ ] Barra de búsqueda global (opcional)
- [ ] **DataGrid** (`DataGrid.tsx`):
  - [ ] Extensión de Table con virtualización (`react-window`)
  - [ ] Para tablas con 1000+ filas sin lag
  - [ ] Columnas resizables y reordenables
- [ ] **DatePicker** (`DatePicker.tsx`):
  - [ ] Selector de fecha individual y rango
  - [ ] Presets: "Últimas 24h", "Última semana", "Último mes"
  - [ ] Calendar dropdown con fondo `#111111`
- [ ] **Chart** (`Chart.tsx`):
  - [ ] Wrapper de Recharts con estilos del design system
  - [ ] Fondo transparente (se usa sobre cards `#111111`)
  - [ ] Colores de líneas/áreas: según tipo de sensor
  - [ ] Tooltip personalizado con fondo `#1A1A1A`
  - [ ] Eje X: fechas formateadas
  - [ ] Eje Y: valores con unidad
  - [ ] Grid: líneas muy sutiles (`#222222`) o sin grid
- [ ] **SensorIcon** (`SensorIcon.tsx`):
  - [ ] Props: `type` (temperature/humidity/light/soil/co2), `size`, `color`
  - [ ] Renderizar SVG del sensor desde `assets/icons/svg/sensors/`
  - [ ] Color por defecto según tipo, override con prop
- [ ] **StatusDot** (`StatusDot.tsx`):
  - [ ] Props: `status` (online/offline/warning), `pulse`
  - [ ] Punto de color con animación de pulso opcional
- [ ] Tests para CADA componente compartido (render, props, events, snapshots)

### 3.5 Layouts y Navegación

- [ ] **MainLayout** (`layouts/MainLayout.tsx`):
  - [ ] Sidebar izquierda (colapsable en mobile)
  - [ ] Header superior con user info
  - [ ] Content area con scroll
  - [ ] Responsive: sidebar → hamburger menu en mobile
  - [ ] Usar logo de `assets/icons/svg/logos/logo-icon.svg` en sidebar
- [ ] **AuthLayout** (`layouts/AuthLayout.tsx`):
  - [ ] Centrado vertical/horizontal
  - [ ] Logo grande de `assets/icons/svg/logos/logo-full.svg`
  - [ ] Card de formulario sobre fondo negro
  - [ ] Diseño idéntico al mockup `mockup-web-login.png`
- [ ] **Routing** (`App.tsx`):
  - [ ] `/login` → LoginPage (AuthLayout)
  - [ ] `/forgot-password` → ForgotPasswordPage (AuthLayout)
  - [ ] `/reset-password/:token` → ResetPasswordPage (AuthLayout)
  - [ ] `/` → redirect a `/dashboard`
  - [ ] `/dashboard` → DashboardPage (MainLayout)
  - [ ] `/sensors` → SensorsPage (MainLayout)
  - [ ] `/sensors/:id` → SensorDetailPage (MainLayout)
  - [ ] `/alerts` → AlertsPage (MainLayout)
  - [ ] `/map` → MapPage (MainLayout)
  - [ ] `/reports` → ReportsPage (MainLayout)
  - [ ] `/gateways` → GatewaysPage (MainLayout)
  - [ ] `/gateways/:id` → GatewayDetailPage (MainLayout)
  - [ ] `/settings` → SettingsPage (MainLayout)
  - [ ] `/admin/users` → UsersPage (MainLayout, admin only)
  - [ ] `/admin/tenants` → TenantsPage (MainLayout, admin only)
  - [ ] `*` → NotFoundPage (404 con ilustración)
- [ ] Lazy loading de cada página con `React.lazy` + `Suspense`
- [ ] Loading fallback con Spinner componente
- [ ] Error boundary con página de error amigable
- [ ] Tests: navegación entre rutas, guards, redirects, 404

### 3.6 Feature: Autenticación

- [x] Implementar Login básico
- [ ] **LoginPage** (debe verse como `mockup-web-login.png`):
  - [ ] Logo EchoSmart centrado arriba
  - [ ] Card con fondo `#111111` centrada en pantalla
  - [ ] Título: "Welcome Back" o "Iniciar Sesión"
  - [ ] Input email con ícono de correo
  - [ ] Input password con ícono de candado y toggle visibility
  - [ ] Checkbox "Remember me"
  - [ ] Botón "Iniciar Sesión" en verde `#00E676` con texto negro
  - [ ] Link "Forgot password?" debajo
  - [ ] Link "Don't have an account? Sign up" abajo
  - [ ] Validación en tiempo real (formato email, longitud password ≥ 8)
  - [ ] Loading state en botón durante request
  - [ ] Mensajes de error: credenciales inválidas, cuenta desactivada, red
  - [ ] Redirect a dashboard después de login exitoso
  - [ ] Guardar tokens en localStorage con encriptación básica
- [ ] **ForgotPasswordPage**:
  - [ ] Input email + botón "Send Reset Link"
  - [ ] Confirmación: "Si el email existe, recibirás un enlace"
  - [ ] Link "Back to login"
- [ ] **ResetPasswordPage**:
  - [ ] Validar token de URL
  - [ ] Inputs: nueva contraseña + confirmar (con indicador de fortaleza)
  - [ ] Redirect a login después de reset exitoso
- [ ] **ProtectedRoute** (wrapper):
  - [ ] Verificar token válido antes de renderizar
  - [ ] Redirect a `/login` si no autenticado
  - [ ] Verificar rol para rutas de admin
  - [ ] Refresh automático de token 5 min antes de expirar
- [ ] **useAuth hook**:
  - [ ] `login(email, password): Promise<User>` — Login y guardar tokens
  - [ ] `logout(): void` — Limpiar tokens, redirect a login
  - [ ] `isAuthenticated: boolean` — Reactivo
  - [ ] `user: User | null` — Datos del usuario actual
  - [ ] `hasRole(role: string): boolean` — Verificar permisos
  - [ ] `refreshToken(): Promise<void>` — Refresh automático
- [ ] Tests: login flow, token refresh, protected routes, role check, error states

### 3.7 Feature: Dashboard (como `mockup-web-dashboard.png`)

- [x] Dashboard básico con gráficas
- [ ] **DashboardPage** — Layout idéntico al mockup:
  - [ ] Fila superior: 4 MetricCards (Temperatura, Humedad, CO₂, Luminosidad)
  - [ ] Sección central: gráfica de lecturas últimas 24h (AreaChart multi-series)
  - [ ] Panel derecho: lista de alertas activas (últimas 5)
  - [ ] Sección inferior: mini mapa del invernadero + estado de gateways
  - [ ] Selector de rango de tiempo (1h, 6h, 24h, 7d, 30d)
  - [ ] Auto-refresh cada 30s con indicador de última actualización
  - [ ] WebSocket para actualizaciones en tiempo real
- [ ] **MetricCard** component (exacto al mockup):
  - [ ] Ícono del sensor (SVG de `assets/icons/svg/sensors/`)
  - [ ] Valor actual en fuente grande JetBrains Mono (ej: "24.5°C")
  - [ ] Unidad en texto pequeño al lado
  - [ ] Label del sensor (ej: "Temperature")
  - [ ] Indicador de tendencia (↑ subiendo, ↓ bajando, → estable) con color
  - [ ] Sparkline mini de últimas 6 horas
  - [ ] Fondo: `#111111`, border-radius 12px
  - [ ] Color del valor según estado: verde=normal, amarillo=warning, rojo=critical
  - [ ] Loading skeleton mientras carga
  - [ ] Click → navegar a sensor detail
- [ ] **SensorChart** component:
  - [ ] Line/Area chart con Recharts sobre fondo transparente
  - [ ] Multi-series: múltiples sensores en misma gráfica con colores de sensor
  - [ ] Tooltip custom: fecha formateada, valor, unidad, color del sensor
  - [ ] Zoom con brush (seleccionar rango) en la parte inferior
  - [ ] Líneas de umbral horizontal (min/max del invernadero) en punteado sutil
  - [ ] Legend con nombre del sensor + último valor
  - [ ] Responsive (adaptar a tamaño del container)
  - [ ] Eje X: fechas con formato inteligente (HH:mm, DD MMM, etc.)
  - [ ] Eje Y: valores con unidad
- [ ] **AlertWidget** component:
  - [ ] Lista compacta de alertas activas (máx 5)
  - [ ] Cada alerta: indicador de severidad (color), mensaje, tiempo relativo
  - [ ] Badge con conteo total de alertas activas
  - [ ] Link "Ver todas las alertas" al final
  - [ ] Click en alerta → navegar a detalle
  - [ ] Empty state si no hay alertas: "All systems normal ✓"
- [ ] **GatewayStatusWidget** component:
  - [ ] Lista de gateways con status dot (online/offline)
  - [ ] Nombre, última conexión, conteo de sensores
  - [ ] Click → navegar a gateway detail
- [ ] Tests: renderizado completo, datos vacíos, loading, error states, auto-refresh

### 3.8 Feature: Gestión de Sensores (como `mockup-web-sensors.png`)

- [x] Sensores básicos
- [ ] **SensorsPage**:
  - [ ] Vista grid (cards) / lista (tabla) toggle
  - [ ] Filtros: tipo de sensor (chips horizontales con íconos), estado (online/offline), gateway
  - [ ] Búsqueda por nombre con debounce 300ms
  - [ ] Botón "Agregar sensor" (verde, top-right)
  - [ ] Paginación o infinite scroll
  - [ ] Conteo total: "Showing X of Y sensors"
  - [ ] Diseño grid: 3 columnas desktop, 2 tablet, 1 mobile
- [ ] **SensorCard** component:
  - [ ] Ícono SVG del tipo de sensor (coloreado según tipo)
  - [ ] Nombre del sensor (bold)
  - [ ] Tipo de sensor (label secundario)
  - [ ] Última lectura: valor + unidad en fuente grande
  - [ ] Tiempo relativo de última lectura ("hace 2 min")
  - [ ] StatusDot: online (verde) / offline (rojo) / warning (amarillo)
  - [ ] Mini sparkline de las últimas 6 horas
  - [ ] Gateway asociado (texto pequeño)
  - [ ] Click → navegar a `/sensors/:id`
- [ ] **SensorDetailPage** (como `mockup-web-sensor-detail.png`):
  - [ ] Header: breadcrumb (Sensors → DS18B20), nombre, tipo, gateway, estado
  - [ ] Card de valor actual: lectura grande + unidad + tendencia
  - [ ] Gráfica principal de lecturas (configurable: 1h–30d)
  - [ ] Selector de rango de tiempo con presets
  - [ ] Tabla de lecturas recientes (10 últimas) con timestamp, valor
  - [ ] Estadísticas: min, max, avg, std dev (para rango seleccionado)
  - [ ] Historial de alertas de este sensor (últimas 10)
  - [ ] Configuración del sensor: nombre editable, umbrales de alerta
  - [ ] Botón "Eliminar sensor" con modal de confirmación
  - [ ] Tab: "Overview" / "History" / "Alerts" / "Config"
- [ ] **AddSensorModal**:
  - [ ] Step wizard (3 pasos):
    - [ ] Paso 1: Seleccionar gateway de la lista
    - [ ] Paso 2: Seleccionar tipo de sensor (cards con íconos SVG)
    - [ ] Paso 3: Configurar nombre, umbrales, ubicación en mapa
  - [ ] Preview de la configuración antes de confirmar
  - [ ] Botón "Create" en verde
- [ ] Tests: lista, filtros, búsqueda, grid/list toggle, detalle, CRUD

### 3.9 Feature: Centro de Alertas (como `mockup-web-alerts.png`)

- [x] Alertas básicas
- [ ] **AlertsPage**:
  - [ ] Fila de contadores por severidad: Critical (X), High (X), Medium (X), Low (X)
  - [ ] Lista de alertas con filtros:
    - [ ] Severidad: critical / high / medium / low (multi-select chips)
    - [ ] Estado: active / acknowledged / resolved
    - [ ] Sensor tipo: temperatura / humedad / etc.
    - [ ] Rango de fecha
  - [ ] Acciones batch: seleccionar múltiples + acknowledge/resolve
  - [ ] Ordenar por: fecha, severidad, sensor
  - [ ] Pagination: 20 por página
- [ ] **AlertCard** component:
  - [ ] Borde izquierdo coloreado por severidad
  - [ ] Ícono de tipo de alerta (según sensor)
  - [ ] Mensaje descriptivo: "Temperature exceeded 35°C in Zone A"
  - [ ] Sensor y gateway afectados (links)
  - [ ] Timestamp relativo ("hace 5 min")
  - [ ] Valor que disparó la alerta (ej: "37.2°C")
  - [ ] Botones: Acknowledge (verde outline), Resolve (verde fill), Ver detalle (ícono)
  - [ ] Estado visual: Active (borde vivo), Acknowledged (borde opaco), Resolved (gris)
- [ ] **AlertRuleEditor** (modal/página):
  - [ ] Formulario para crear/editar reglas de alerta
  - [ ] Selección de tipo: umbral (>/<), rango (fuera de), tasa de cambio (Δ/min), sin datos (timeout)
  - [ ] Selección de sensor(es) aplicables
  - [ ] Configuración de valores (min, max, duración antes de trigger)
  - [ ] Selección de severidad
  - [ ] Selección de acciones: email, push notification, webhook
  - [ ] Preview en lenguaje natural: "Si la temperatura supera 35°C durante más de 5 minutos, enviar alerta crítica por email"
  - [ ] Lista de reglas existentes con toggle enable/disable
- [ ] Tests: lista, filtros, acknowledge, batch actions, reglas

### 3.10 Feature: Mapa del Invernadero (como `mockup-web-map.png`)

- [ ] **MapPage**:
  - [ ] Plano 2D del invernadero (SVG interactivo o Canvas con Konva.js)
  - [ ] Sensores posicionados como markers en el mapa
  - [ ] Cada marker: ícono del sensor + color según estado
  - [ ] Click en sensor → popup con: última lectura, estado, link a detalle
  - [ ] Zonas del invernadero con promedios (color de fondo según condición)
  - [ ] **Heatmap mode**: gradiente de temperatura/humedad sobre el plano
  - [ ] **Edit mode**: drag & drop para reposicionar sensores en el mapa
  - [ ] Leyenda de colores (por sensor o por estado)
  - [ ] Zoom in/out y pan del mapa
  - [ ] Fullscreen toggle
  - [ ] Responsive: adaptable a mobile
- [ ] Tests: renderizado del mapa, click en sensores, heatmap, edit mode

### 3.11 Feature: Reportes (como `mockup-web-reports.png`)

- [x] Reportes básicos
- [ ] **ReportsPage**:
  - [ ] Formulario de generación:
    - [ ] Tipo: diario / semanal / mensual / custom
    - [ ] Rango de fechas con DatePicker
    - [ ] Sensores a incluir (multi-select)
    - [ ] Formato de descarga: PDF / Excel (.xlsx) / CSV
  - [ ] Lista de reportes generados:
    - [ ] Nombre, fecha, tipo, estado (pendiente/generando/completado/error)
    - [ ] Progreso de generación (barra de progreso)
    - [ ] Botón de descarga para completados
    - [ ] Botón de regenerar para errores
  - [ ] Preview del reporte antes de generar (tabla + gráficas)
  - [ ] Programación automática: "Generar reporte diario todos los lunes a las 8:00"
- [ ] Tests: formulario de generación, descarga, programación

### 3.12 Feature: Gateways (como `mockup-web-gateway-detail.png`)

- [ ] **GatewaysPage**:
  - [ ] Lista de gateways con: nombre, serial, estado (online/offline), última conexión, # sensores
  - [ ] Filtro por estado
  - [ ] Botón "Add Gateway" con wizard de provisioning
- [ ] **GatewayDetailPage**:
  - [ ] Header: nombre, serial, estado, uptime, versión del firmware
  - [ ] Métricas del gateway: CPU%, memoria%, disco%, red
  - [ ] Lista de sensores conectados al gateway
  - [ ] Logs del gateway en tiempo real (via WebSocket)
  - [ ] Acciones: reiniciar, actualizar firmware, editar configuración, eliminar
  - [ ] Historial de conexiones/desconexiones
- [ ] Tests: lista, detalle, acciones

### 3.13 Feature: Panel de Administración (como `mockup-web-users.png`)

- [x] Admin panel básico
- [ ] **UsersPage** (admin only, como `mockup-web-users.png`):
  - [ ] Contadores en cards: Total Users, Active, Admins, Pending
  - [ ] Tabla de usuarios: nombre, email, rol (badge), estado (dot), último login, acciones
  - [ ] Filtros: rol, estado
  - [ ] Búsqueda por nombre/email
  - [ ] Acciones por usuario: editar rol, desactivar, eliminar, reset password
  - [ ] Modal de invitación: enviar email de invitación con rol asignado
- [ ] **GatewaysAdminPage** (admin only):
  - [ ] Tabla de TODOS los gateways del tenant
  - [ ] Detalle con logs, métricas, configuración
  - [ ] Acciones: reiniciar, actualizar, eliminar
- [ ] **TenantSettingsPage** (admin only):
  - [ ] Configuración del tenant: nombre, logo personalizado, plan, límites
  - [ ] Estadísticas de uso: gateways, sensores, lecturas, almacenamiento
  - [ ] Billing info (si aplica)
- [ ] Tests: tablas, acciones, permisos (verificar que viewer no accede a admin)

### 3.14 Feature: Configuración (como `mockup-web-settings.png`)

- [ ] **SettingsPage**:
  - [ ] Tabs: Profile / Security / Notifications / Appearance / API
  - [ ] **Profile**: nombre, email, avatar upload, timezone
  - [ ] **Security**: cambiar contraseña (current + new + confirm), sesiones activas, 2FA setup
  - [ ] **Notifications**: preferencias por canal (email/push/in-app) y por tipo de alerta
  - [ ] **Appearance**: idioma (es/en), formato de fecha, unidades (°C/°F)
  - [ ] **API**: generar API keys, ver webhooks configurados
- [ ] Tests: cada tab, guardado de preferencias

### 3.15 API Client y Server State (Clean Architecture)

- [x] Cliente HTTP básico
- [ ] Refactorizar API client (`lib/api-client.ts`):
  - [ ] Axios instance tipada con TypeScript generics
  - [ ] Base URL desde env variable
  - [ ] Timeout: 30s
  - [ ] Request interceptor: agregar `Authorization: Bearer <token>` automáticamente
  - [ ] Response interceptor: refresh token en 401, retry original request (max 1 retry)
  - [ ] Error interceptor: parsear errores del backend a `ApiError` type consistente
  - [ ] Cancel tokens para requests in-flight cuando se cambia de página
- [ ] Configurar React Query (`lib/query-client.ts`):
  - [ ] `staleTime: 5 * 60 * 1000` (5 min)
  - [ ] `cacheTime: 30 * 60 * 1000` (30 min)
  - [ ] `refetchOnWindowFocus: true`
  - [ ] `retry: 2` para errores de red
- [ ] Crear hooks de React Query por feature:
  - [ ] `useSensors(filters)` — query con pagination
  - [ ] `useSensor(id)` — query single sensor
  - [ ] `useSensorReadings(id, range)` — query readings con refetch
  - [ ] `useAlerts(filters)` — query alerts
  - [ ] `useCreateSensor()` — mutation
  - [ ] `useAcknowledgeAlert()` — mutation con optimistic update
  - [ ] `useGateways()` — query gateways
  - [ ] `useUsers()` — query users (admin)
  - [ ] `useReports()` — query reports
- [ ] Crear funciones API tipadas por feature:
  - [ ] `features/auth/api.ts` — `login()`, `register()`, `refreshToken()`, `forgotPassword()`
  - [ ] `features/sensors/api.ts` — `getSensors()`, `getSensor()`, `getReadings()`, `createSensor()`, `updateSensor()`, `deleteSensor()`
  - [ ] `features/alerts/api.ts` — `getAlerts()`, `acknowledgeAlert()`, `resolveAlert()`, `createRule()`, `getRules()`
  - [ ] `features/gateways/api.ts` — `getGateways()`, `getGateway()`, `restartGateway()`, `updateConfig()`
  - [ ] `features/reports/api.ts` — `getReports()`, `generateReport()`, `downloadReport()`
  - [ ] `features/admin/api.ts` — `getUsers()`, `inviteUser()`, `updateRole()`, `deactivateUser()`
- [ ] Tests: interceptors, retry, cancel, tipado, error handling

### 3.16 Estado Global (Redux Toolkit)

- [x] Store básico
- [ ] Reducir Redux a SOLO estado de UI (server state → React Query):
  - [ ] `authSlice` — usuario autenticado, tokens, permisos
  - [ ] `uiSlice` — sidebar collapsed, locale, active toasts, breadcrumb
- [ ] Implementar selectors memoizados con `createSelector`:
  - [ ] `selectCurrentUser`, `selectIsAdmin`, `selectIsAuthenticated`
  - [ ] `selectSidebarCollapsed`, `selectLocale`
- [ ] Implementar middleware de logging en desarrollo
- [ ] Tests: reducers, selectors, middleware

### 3.17 WebSocket Manager

- [ ] Implementar `WebSocketManager` class (`lib/websocket.ts`):
  - [ ] `connect(url: string, token: string): void` — Conectar con autenticación
  - [ ] `disconnect(): void` — Desconectar limpiamente
  - [ ] `subscribe(channel: string, callback: (data: T) => void): () => void` — Suscribirse, retorna unsub
  - [ ] `send(channel: string, data: unknown): void` — Enviar mensaje
  - [ ] Auto-reconnect con backoff exponencial (1s, 2s, 4s, 8s, max 30s)
  - [ ] Heartbeat cada 30s (ping/pong)
  - [ ] Buffer de mensajes durante desconexión
  - [ ] Event emitter pattern: `onConnect`, `onDisconnect`, `onError`
- [ ] Implementar `useWebSocket` hook:
  - [ ] Conectar al montar MainLayout, desconectar al desmontar
  - [ ] Estado de conexión: `connecting`, `connected`, `disconnected`
  - [ ] `useSubscription(channel)` — Devolver últimos datos del canal
  - [ ] Integrar con React Query para invalidar queries al recibir update
- [ ] Channels de WebSocket:
  - [ ] `readings:{sensor_id}` — Lecturas en tiempo real por sensor
  - [ ] `alerts` — Nuevas alertas
  - [ ] `gateways:{gateway_id}:status` — Estado del gateway
  - [ ] `notifications:{user_id}` — Notificaciones del usuario
- [ ] Tests: conexión, reconexión, suscripción, heartbeat

### 3.18 Optimización y Performance

- [ ] Code splitting con `React.lazy()` + `Suspense` por cada página
- [ ] Prefetch de rutas probables (ej: si está en sensors, prefetch dashboard)
- [ ] Memoización con `React.memo`, `useMemo`, `useCallback` donde sea necesario
- [ ] Virtualización de listas grandes con `@tanstack/react-virtual`
- [ ] Debounce en búsquedas y filtros (300ms) con `useDebounce` hook
- [ ] Infinite scroll en tablas con muchos registros
- [ ] Optimizar imágenes: lazy loading (`loading="lazy"`), WebP format, responsive `srcset`
- [ ] Comprimir SVGs con SVGO
- [ ] Configurar Service Worker con `vite-plugin-pwa`:
  - [ ] Cache-first para assets estáticos
  - [ ] Network-first para API calls
  - [ ] Offline fallback page con logo EchoSmart
- [ ] Lograr **Lighthouse score ≥ 90** en: Performance, Accessibility, Best Practices, SEO
- [ ] Bundle analysis con `rollup-plugin-visualizer`: verificar tamaño < 500KB gzipped
- [ ] Tree shaking verificado: no importar todo lodash, solo funciones individuales

### 3.19 Internacionalización (i18n)

- [ ] Configurar `react-i18next` con lazy loading de namespaces
- [ ] Crear archivos de traducción:
  - [ ] `i18n/es/common.json` — Botones, labels, errores genéricos
  - [ ] `i18n/es/dashboard.json` — Textos del dashboard
  - [ ] `i18n/es/sensors.json` — Textos de sensores
  - [ ] `i18n/es/alerts.json` — Textos de alertas
  - [ ] `i18n/en/common.json` — English translations
  - [ ] `i18n/en/dashboard.json`, etc.
- [ ] Selector de idioma en Settings
- [ ] Formateo de fechas según locale (`date-fns/locale`)
- [ ] Formateo de números según locale (decimal separator)
- [ ] Tests: cambio de idioma, formateo, fallback

### 3.20 PWA (Progressive Web App)

- [ ] `manifest.json` con:
  - [ ] `name: "EchoSmart"`, `short_name: "EchoSmart"`
  - [ ] `theme_color: "#000000"`, `background_color: "#000000"`
  - [ ] Icons: usar `assets/platform/web/pwa-icon-192.png` y `pwa-icon-512.png`
  - [ ] `display: "standalone"`
  - [ ] `start_url: "/dashboard"`
- [ ] Service worker con Workbox (via vite-plugin-pwa):
  - [ ] Precache de shell de la app (HTML, CSS, JS)
  - [ ] Runtime cache para API con stale-while-revalidate
  - [ ] Offline fallback page
- [ ] Install prompt: banner para instalar como app
- [ ] Meta tags: `apple-touch-icon`, `apple-mobile-web-app-capable`
- [ ] Tests: instalación, offline mode, cache

### 3.21 Frontend — Tests Completos

- [ ] Tests unitarios para CADA componente compartido (20+ componentes × 3+ tests cada uno)
- [ ] Tests unitarios para CADA hook personalizado
- [ ] Tests de integración por feature:
  - [ ] Auth: login → redirect → dashboard
  - [ ] Sensors: list → filter → detail → edit → delete
  - [ ] Alerts: list → acknowledge → resolve
  - [ ] Dashboard: render all widgets con datos mock
- [ ] Tests de formularios: validación, submit, error handling, loading states
- [ ] Tests de routing: navegación, guards, redirects, 404
- [ ] Tests de responsive: verificar breakpoints (mobile, tablet, desktop)
- [ ] Tests de accesibilidad: keyboard navigation, screen reader labels, ARIA roles
- [ ] Configurar `testing-library` con custom renders (providers, router, query client)
- [ ] Verificar cobertura ≥ 80% con `vitest --coverage`
- [ ] Snapshots tests para componentes estables (Card, Badge, EmptyState)

### 3.22 Frontend — Calidad de Código

- [ ] Configurar ESLint strict mode con zero warnings
- [ ] Configurar Prettier y verificar formato en CI
- [ ] TypeScript strict mode con `noImplicitAny`, `strictNullChecks`
- [ ] Configurar `husky` pre-commit: lint + type-check + test affected
- [ ] TODAS las interfaces y types exportados y documentados
- [ ] CERO `any` en todo el codebase (usar `unknown` o types específicos)
- [ ] CERO `console.log` — usar `lib/logger.ts` dedicado
- [ ] Crear `frontend/README.md` con:
  - [ ] Guía de setup de desarrollo
  - [ ] Estructura del proyecto explicada
  - [ ] Convenciones de naming y código
  - [ ] Guía de testing
  - [ ] Design system reference

---

## Fase 4: Aplicación Móvil — React Native + Expo (Semanas 11–16)

> 🏛️ **Clean Architecture en Mobile**: Misma separación que en web. Features → componentes, hooks, API, store. Componentes nativos de cada plataforma donde sea necesario.

> 📱 **Stack Definido**: React Native 0.73 + Expo SDK 50 + TypeScript. Compilación a **APK (Android)** vía Expo EAS Build y a **IPA (iOS)** vía Expo EAS Build. La app se escribe UNA VEZ en React Native/TypeScript y se compila nativamente para ambas plataformas.

### 4.1 Definición de Tecnologías y Justificación de Plataforma

| Decisión | Elección | Justificación |
|----------|----------|---------------|
| **Framework** | React Native + Expo | Code sharing con web (mismos hooks, API client, tipos). Una codebase → 2 plataformas. Expo simplifica builds y acceso a APIs nativas |
| **Lenguaje** | TypeScript | Type safety, consistencia con frontend web, autocompletado, refactoring seguro |
| **NO Flutter/Dart** | Descartado | El equipo ya usa React/TypeScript en web. Flutter requeriría aprender Dart y duplicar lógica de negocio |
| **NO Kotlin/Java nativo** | Descartado | Duplicaría el desarrollo para iOS (Swift). React Native permite una codebase para ambas plataformas |
| **NO Swift nativo** | Descartado | Solo cubre iOS. React Native cubre ambas plataformas con una codebase |
| **Build Android** | EAS Build → APK / AAB | Expo EAS compila en la nube sin necesidad de Android Studio local |
| **Build iOS** | EAS Build → IPA | Expo EAS compila en la nube sin necesidad de Xcode local (necesita Apple Developer account) |
| **Navegación** | React Navigation v6 | Estándar de facto para React Native, gestos nativos, deep linking |
| **Estado** | Zustand + React Query | Zustand más ligero que Redux para mobile. React Query para server state con cache |
| **Gráficas** | react-native-chart-kit o Victory Native | Charts nativos optimizados para mobile |
| **Mapas** | react-native-maps | Maps nativos (Google Maps Android, Apple Maps iOS) |
| **Push** | expo-notifications + FCM | Firebase Cloud Messaging para Android, APNs para iOS |
| **Storage** | AsyncStorage + MMKV | AsyncStorage para datos simples, MMKV para datos sensibles con encriptación |

### 4.2 Configuración y Arquitectura del Proyecto

- [x] Configurar proyecto Expo en `mobile/`
- [ ] Migrar de JavaScript a TypeScript:
  - [ ] Renombrar archivos `.js` → `.ts` / `.tsx`
  - [ ] Configurar `tsconfig.json` con strict mode
  - [ ] Instalar `@types/react-native`
- [ ] Configurar EAS Build:
  - [ ] `eas.json` con profiles: development, preview, production
  - [ ] Configurar `app.json` / `app.config.ts` con:
    - [ ] `name: "EchoSmart"`
    - [ ] `slug: "echosmart"`
    - [ ] `version: "1.0.0"`
    - [ ] `icon: "../assets/platform/ios/app-icon-1024.png"` (iOS)
    - [ ] `splash.image: "../assets/splash/png/splash-1242x2688.png"`
    - [ ] `splash.backgroundColor: "#000000"`
    - [ ] `android.adaptiveIcon.foregroundImage: "../assets/platform/android/adaptive-icon-foreground.png"`
    - [ ] `android.adaptiveIcon.backgroundColor: "#000000"`
    - [ ] `android.package: "com.echosmart.app"`
    - [ ] `ios.bundleIdentifier: "com.echosmart.app"`
    - [ ] `ios.supportsTablet: true`
- [ ] Configurar variables de entorno (`.env.development`, `.env.production`):
  - [ ] `API_URL` — URL del backend
  - [ ] `WS_URL` — URL del WebSocket
- [ ] Configurar path aliases con `babel-plugin-module-resolver`:
  - [ ] `@/screens` → `src/features/*/screens`
  - [ ] `@/components` → `src/shared/components`
  - [ ] `@/hooks` → `src/shared/hooks`
  - [ ] `@/api` → `src/lib/api-client`
  - [ ] `@/store` → `src/store`
  - [ ] `@/assets` → `src/assets`
  - [ ] `@/types` → `src/types`
- [ ] Configurar ESLint + Prettier para React Native + TypeScript
- [ ] Instalar dependencias core:
  - [ ] `react-navigation` (native, native-stack, bottom-tabs, drawer)
  - [ ] `react-native-safe-area-context`, `react-native-screens`
  - [ ] `@tanstack/react-query` (React Query para server state)
  - [ ] `zustand` (client state)
  - [ ] `axios` (HTTP client)
  - [ ] `react-native-mmkv` (secure storage)
  - [ ] `expo-notifications` (push)
  - [ ] `expo-local-authentication` (biometría)
  - [ ] `expo-haptics` (feedback táctil)
  - [ ] `@react-native-community/netinfo` (estado de red)
  - [ ] `react-native-reanimated` (animaciones)
  - [ ] `react-native-gesture-handler` (gestos)
  - [ ] `react-native-svg` (iconos SVG)

### 4.3 Estructura del Proyecto Mobile

```
mobile/src/
├── features/
│   ├── auth/
│   │   ├── screens/            # LoginScreen.tsx, ForgotPasswordScreen.tsx
│   │   ├── components/         # LoginForm.tsx, BiometricButton.tsx
│   │   ├── hooks/              # useAuth.ts, useBiometric.ts
│   │   ├── api.ts              # Auth API calls
│   │   └── types.ts
│   ├── dashboard/
│   │   ├── screens/            # DashboardScreen.tsx
│   │   ├── components/         # MetricCard.tsx, MiniChart.tsx, AlertBanner.tsx
│   │   ├── hooks/              # useDashboardData.ts
│   │   └── types.ts
│   ├── sensors/
│   │   ├── screens/            # SensorsScreen.tsx, SensorDetailScreen.tsx, ChartFullscreenScreen.tsx, AddSensorScreen.tsx
│   │   ├── components/         # SensorCard.tsx, SensorList.tsx, ReadingChart.tsx
│   │   ├── hooks/              # useSensors.ts, useSensorReadings.ts
│   │   └── types.ts
│   ├── alerts/
│   │   ├── screens/            # AlertsScreen.tsx
│   │   ├── components/         # AlertCard.tsx, SwipeableAlert.tsx
│   │   ├── hooks/              # useAlerts.ts
│   │   └── types.ts
│   ├── map/
│   │   ├── screens/            # MapScreen.tsx
│   │   ├── components/         # GreenhouseMap.tsx, SensorMarker.tsx
│   │   └── hooks/              # useMapData.ts
│   ├── settings/
│   │   ├── screens/            # SettingsScreen.tsx, ProfileScreen.tsx, NotificationsScreen.tsx, AboutScreen.tsx
│   │   └── components/         # SettingsRow.tsx, ProfileAvatar.tsx
│   └── notifications/
│       ├── screens/            # NotificationsScreen.tsx
│       └── hooks/              # useNotifications.ts
├── shared/
│   ├── components/             # Button, Input, Card, Badge, Spinner, EmptyState, BottomSheet, SwipeableRow
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Spinner.tsx
│   │   ├── EmptyState.tsx
│   │   ├── BottomSheet.tsx
│   │   ├── SwipeableRow.tsx
│   │   ├── RefreshControl.tsx
│   │   ├── SkeletonLoader.tsx
│   │   ├── Avatar.tsx
│   │   ├── SensorIcon.tsx
│   │   ├── StatusDot.tsx
│   │   ├── Toast.tsx
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useApi.ts
│   │   ├── useLocation.ts
│   │   ├── useNotifications.ts
│   │   ├── useNetworkStatus.ts
│   │   ├── useDebounce.ts
│   │   └── useRefresh.ts
│   ├── navigation/
│   │   ├── AppNavigator.tsx     # Root navigator
│   │   ├── AuthStack.tsx        # Login, Forgot
│   │   ├── MainTabs.tsx         # Bottom tabs
│   │   ├── SensorStack.tsx      # Sensor list → detail → chart
│   │   ├── AlertStack.tsx       # Alert list → detail
│   │   └── SettingsStack.tsx    # Settings → sub-screens
│   └── utils/
│       ├── formatters.ts
│       ├── validators.ts
│       └── constants.ts
├── lib/
│   ├── api-client.ts            # Axios + auth interceptor (compartido con web)
│   ├── storage.ts               # MMKV helpers
│   ├── push.ts                  # Push notifications setup
│   ├── websocket.ts             # WebSocket manager (compartido con web)
│   └── logger.ts                # Mobile logger
├── store/
│   ├── auth.store.ts            # Zustand auth store
│   └── ui.store.ts              # Zustand UI store
├── types/                       # Shared types (idealmente importar de shared/)
├── assets/                      # Copia de assets para build
│   ├── icons/                   # SVGs de sensores y navegación
│   └── images/                  # Ilustraciones para empty states
└── App.tsx
```

- [ ] Crear estructura de features completa
- [ ] Crear tipos compartidos (importar de `shared/` donde sea posible)
- [ ] Crear barrel exports en cada feature

### 4.4 Tema y Design System Mobile

> 🎨 Los colores y estilos DEBEN ser idénticos a los mockups en `assets/mockups/mobile/`

- [ ] Crear `theme/tokens.ts` con constantes de diseño:
  - [ ] Colores: misma paleta que web (bg-primary #000, surface #111, etc.)
  - [ ] Tipografía: Inter (text) + JetBrains Mono (datos numéricos)
  - [ ] Spacing: 4, 8, 12, 16, 20, 24, 32, 48 (scale de 4px)
  - [ ] Border radius: 8 (small), 12 (medium), 16 (large), 24 (pill)
  - [ ] Shadows: sombra sutil para cards elevadas
- [ ] Crear `theme/GlobalStyles.ts` con estilos base:
  - [ ] Default font family
  - [ ] Background color negro (#000)
  - [ ] Text color blanco
- [ ] Configurar fuentes personalizadas con `expo-font`:
  - [ ] Descargar Inter (Regular, Medium, Bold) y JetBrains Mono (Regular)
  - [ ] Pre-cargar fuentes antes de mostrar app

### 4.5 Navegación (React Navigation)

- [ ] Configurar React Navigation v6:
  - [ ] **AuthStack** (Stack Navigator):
    - [ ] `LoginScreen` — Formulario de login
    - [ ] `ForgotPasswordScreen` — Recuperar contraseña
    - [ ] `ResetPasswordScreen` — Nueva contraseña
  - [ ] **MainTabs** (Bottom Tab Navigator):
    - [ ] Tab 1: `DashboardScreen` — Ícono: dashboard.svg
    - [ ] Tab 2: `SensorsScreen` — Ícono: sensors.svg
    - [ ] Tab 3: `AlertsScreen` — Ícono: alerts.svg, badge con conteo
    - [ ] Tab 4: `MapScreen` — Ícono: map.svg
    - [ ] Tab 5: `SettingsScreen` — Ícono: settings.svg
  - [ ] **SensorStack** (Stack Navigator, dentro de Tab 2):
    - [ ] `SensorsScreen` → `SensorDetailScreen` → `ChartFullscreenScreen`
  - [ ] **AlertStack** (Stack Navigator, dentro de Tab 3):
    - [ ] `AlertsScreen` → `AlertDetailScreen`
  - [ ] **SettingsStack** (Stack Navigator, dentro de Tab 5):
    - [ ] `SettingsScreen` → `ProfileScreen` → `NotificationsScreen` → `AboutScreen`
- [ ] Tab bar estilizado:
  - [ ] Fondo: `#0A0A0A` (casi negro)
  - [ ] Íconos inactivos: `#616161` (gris)
  - [ ] Ícono activo: `#00E676` (verde)
  - [ ] Label activo: `#00E676`
  - [ ] Badge en Alerts tab: círculo rojo con número
  - [ ] Usar SVGs de `assets/icons/svg/navigation/`
- [ ] Configurar deep linking (URLs: `echosmart://sensors/123`, `echosmart://alerts`)
- [ ] Configurar splash screen nativo con `expo-splash-screen`:
  - [ ] Usar imagen de `assets/splash/png/` según resolución
  - [ ] Background: `#000000`
  - [ ] Mantener splash hasta que se carguen fuentes y auth check
- [ ] Transiciones animadas entre pantallas (slide, fade)
- [ ] Gesture-based navigation (swipe back en iOS, edge swipe en Android)
- [ ] Tests: navegación entre todas las pantallas, deep linking

### 4.6 Pantallas Principales (cada una debe coincidir con mockups mobile)

- [ ] **LoginScreen** (como `mockup-mobile-login.png`):
  - [ ] Logo EchoSmart centrado arriba (de `assets/icons/svg/logos/`)
  - [ ] Card de formulario con fondo `#111111`
  - [ ] Input email con ícono, validación de formato
  - [ ] Input password con toggle visibility
  - [ ] Checkbox "Remember me"
  - [ ] Botón "Iniciar Sesión" en verde `#00E676`
  - [ ] Link "Forgot password?"
  - [ ] Biometric login button (Face ID / Fingerprint) si está habilitado
  - [ ] KeyboardAvoidingView para que el teclado no tape inputs
  - [ ] Loading state durante request
  - [ ] Error messages: shake animation + texto rojo

- [ ] **DashboardScreen** (como `mockup-mobile-home.png`):
  - [ ] Header con logo + nombre de la app
  - [ ] Grid 2×2 de métricas (Temperature, Humidity, CO₂, Light):
    - [ ] Cada card: ícono SVG, valor grande en JetBrains Mono, unidad, tendencia
    - [ ] Colores según tipo de sensor
    - [ ] Touch → navegar a sensor detail
  - [ ] Gráfica simplificada de últimas 6 horas (mini area chart)
  - [ ] Sección "Recent Alerts": 3 alertas más recientes
    - [ ] Cada alerta: ícono de severidad, mensaje, tiempo relativo
    - [ ] Touch → navegar a alerta
  - [ ] Pull-to-refresh con RefreshControl personalizado
  - [ ] Loading skeletons durante primera carga
  - [ ] WebSocket: actualizar métricas en tiempo real

- [ ] **SensorsScreen** (como `mockup-mobile-sensors.png`):
  - [ ] Barra de búsqueda en la parte superior
  - [ ] Chips de filtro horizontal: All, Temperature, Humidity, Light, Soil, CO₂
  - [ ] Lista de sensores (FlatList con virtualización):
    - [ ] SensorCard: ícono, nombre, última lectura, tiempo, status dot
    - [ ] Touch → navegar a detail
  - [ ] FAB "+" verde en esquina inferior derecha → AddSensorScreen
  - [ ] Pull-to-refresh
  - [ ] Empty state: ilustración de `assets/icons/svg/illustrations/` + "No sensors yet"
  - [ ] Animated transitions: cards con fade in staggered

- [ ] **SensorDetailScreen** (como `mockup-mobile-sensor-detail.png`):
  - [ ] Header: nombre del sensor, tipo (badge), estado (dot)
  - [ ] Card grande: valor actual en font enorme + unidad + tendencia
  - [ ] Gráfica de lecturas con selector de rango (1h, 6h, 24h, 7d)
  - [ ] Touch en gráfica → ChartFullscreenScreen
  - [ ] Estadísticas: Min, Max, Avg en 3 mini cards
  - [ ] Lista de alertas recientes de este sensor
  - [ ] Botón "Settings" para configurar nombre y umbrales

- [ ] **AlertsScreen** (como `mockup-mobile-alerts.png`):
  - [ ] Contadores por severidad en la parte superior
  - [ ] Lista de alertas con SwipeableRow:
    - [ ] Swipe right → Acknowledge (verde)
    - [ ] Swipe left → Resolve (azul)
  - [ ] Filtros: chips de severidad (Critical, High, Medium, Low)
  - [ ] Badge en tab con conteo de no leídas
  - [ ] Pull-to-refresh
  - [ ] Haptic feedback al acknowledge/resolve

- [ ] **MapScreen** (como `mockup-mobile-map.png`):
  - [ ] Mapa del invernadero (react-native-maps o SVG):
    - [ ] Markers de sensores con colores de estado
    - [ ] Touch en marker → popup con última lectura
  - [ ] Leyenda de colores
  - [ ] Zoom in/out con pinch gesture

- [ ] **SettingsScreen** (como `mockup-mobile-settings.png`):
  - [ ] Secciones con SettingsRow components:
    - [ ] Perfil: nombre, email, avatar
    - [ ] Notificaciones: toggle por tipo (email, push, in-app)
    - [ ] Biometría: toggle Face ID / Fingerprint
    - [ ] Idioma: selector es/en
    - [ ] Información: versión, licencias, soporte
    - [ ] Logout: botón rojo

- [ ] **NotificationsScreen** (como `mockup-mobile-notifications.png`):
  - [ ] Lista de notificaciones push recibidas
  - [ ] Marcar como leída (touch)
  - [ ] Navegar al recurso relacionado al tocar
  - [ ] Empty state si no hay notificaciones

- [ ] **AddSensorScreen** (como `mockup-mobile-add-sensor.png`):
  - [ ] Step wizard (3 pasos con indicador de progreso):
    - [ ] Paso 1: Seleccionar gateway (lista de gateways online)
    - [ ] Paso 2: Seleccionar tipo de sensor (cards con ícono SVG)
    - [ ] Paso 3: Nombre + configuración (umbrales)
  - [ ] Opción: escanear QR/código del sensor con `expo-barcode-scanner`
  - [ ] Botón "Create" en verde

- [ ] **ChartFullscreenScreen** (como `mockup-mobile-chart-fullscreen.png`):
  - [ ] Gráfica a pantalla completa en landscape (forzar orientación)
  - [ ] Pinch to zoom
  - [ ] Selector de rango de tiempo
  - [ ] Botón "Export as image" (capturar view como PNG)
  - [ ] Botón "Back" para volver a portrait

### 4.7 Componentes Compartidos (Mobile Design System)

> Cada componente usa colores de `theme/tokens.ts` y es visualmente consistente con los mockups mobile.

- [ ] **Button** — Primary (verde), secondary (#1A1A1A), danger (rojo), outline, FAB:
  - [ ] Loading state con ActivityIndicator
  - [ ] Disabled state (opacidad 0.5)
  - [ ] Haptic feedback al tocar
  - [ ] Tests: render, press, loading, disabled
- [ ] **Input** — Text, password (toggle visibility), search (ícono lupa):
  - [ ] Label encima del input
  - [ ] Error message debajo en rojo
  - [ ] Fondo `#1A1A1A`, borde `#2A2A2A`, focus `#00E676`
  - [ ] Tests: input, validation, clear
- [ ] **Card** — Surface container con fondo `#111111`, border-radius 12px:
  - [ ] Sombra nativa (iOS shadow, Android elevation)
  - [ ] Touch feedback (opacity)
- [ ] **Badge** — Status dot + conteo:
  - [ ] Variantes: success (verde), warning (amarillo), danger (rojo), info (cyan)
- [ ] **Spinner** — Loading overlay + inline:
  - [ ] Fullscreen overlay con fondo semitransparente
  - [ ] Inline spinner para botones y listas
- [ ] **EmptyState** — Ilustración SVG + mensaje + CTA button:
  - [ ] Usar ilustraciones de `assets/icons/svg/illustrations/`
  - [ ] Centrado vertical en contenedor
- [ ] **Avatar** — Con iniciales y badge de estado:
  - [ ] Imagen de perfil o iniciales sobre fondo verde
  - [ ] Status dot en esquina
- [ ] **BottomSheet** — Modal desde abajo:
  - [ ] Para filtros, acciones rápidas, opciones
  - [ ] Gesture: swipe down para cerrar
  - [ ] Fondo `#111111`, handle bar en `#333333`
- [ ] **SwipeableRow** — Swipe left/right para acciones:
  - [ ] Reveal action buttons detrás de la fila
  - [ ] Haptic feedback al completar swipe
- [ ] **RefreshControl** — Pull-to-refresh estilizado:
  - [ ] Spinner en verde `#00E676`
- [ ] **SkeletonLoader** — Placeholder animado:
  - [ ] Shimmer animation sobre fondo `#111111`
  - [ ] Shapes: rectangle, circle, text line
- [ ] **SensorIcon** — Renderizar SVG del sensor:
  - [ ] Props: type, size, color
  - [ ] Usar `react-native-svg`
- [ ] **StatusDot** — Online/offline indicator:
  - [ ] Pulse animation para online
- [ ] **Toast** — Notificación in-app:
  - [ ] Slide down desde top
  - [ ] Auto-dismiss
  - [ ] Variantes: success, error, warning, info
- [ ] Tests para cada componente

### 4.8 Funcionalidades Nativas

- [ ] **Push Notifications** (Firebase Cloud Messaging):
  - [ ] Configurar `expo-notifications`:
    - [ ] Solicitar permisos al usuario
    - [ ] Obtener device push token (FCM para Android, APNs para iOS)
    - [ ] Enviar token al backend: `POST /api/v1/users/me/push-token`
  - [ ] Manejar notificaciones en foreground: in-app Toast banner
  - [ ] Manejar notificaciones en background: notificación del sistema
  - [ ] Deep linking desde notificación:
    - [ ] Alerta → AlertDetailScreen
    - [ ] Sensor → SensorDetailScreen
    - [ ] Gateway offline → GatewayScreen
  - [ ] Canales de notificación por severidad (Android):
    - [ ] "Critical Alerts" — Sound + vibration
    - [ ] "General Alerts" — Sound only
    - [ ] "Info" — Silent
  - [ ] Tests: registro, recepción, deep link

- [ ] **Modo Offline**:
  - [ ] Cache de última lectura de cada sensor en MMKV:
    - [ ] Key: `sensor:{id}:last_reading`
    - [ ] Value: `{value, timestamp, unit}`
  - [ ] Detectar estado de red con `@react-native-community/netinfo`
  - [ ] Mostrar banner "Sin conexión" cuando offline (sticky top)
  - [ ] En offline: mostrar datos cacheados con indicador "Cached X min ago"
  - [ ] Queue de acciones offline (acknowledge alerts) con retry al reconectar
  - [ ] Sincronizar datos acumulados al reconectar
  - [ ] Tests: offline mode, cache, queue, sync

- [ ] **Biometría** (Face ID / Touch ID / Fingerprint):
  - [ ] `expo-local-authentication`:
    - [ ] Verificar hardware disponible: `hasHardwareAsync()`
    - [ ] Verificar biometría enrolled: `isEnrolledAsync()`
    - [ ] Autenticar: `authenticateAsync({ promptMessage: 'Acceder a EchoSmart' })`
  - [ ] Toggle en Settings para habilitar/deshabilitar
  - [ ] Auto-login con biometría si token válido en MMKV
  - [ ] Fallback a login con contraseña si biometría falla
  - [ ] Tests: check hardware, authenticate, fallback

- [ ] **Haptic Feedback**:
  - [ ] `expo-haptics`:
    - [ ] `impactAsync(ImpactFeedbackStyle.Light)` — Tab switches, swipes
    - [ ] `impactAsync(ImpactFeedbackStyle.Medium)` — Button press, acknowledge
    - [ ] `notificationAsync(NotificationFeedbackType.Success)` — Acción completada
    - [ ] `notificationAsync(NotificationFeedbackType.Error)` — Error
  - [ ] Configurar haptics en: swipe actions, pull-to-refresh complete, FAB press, login success/error

- [ ] **Orientación de Pantalla**:
  - [ ] Portrait lock por defecto para todas las pantallas
  - [ ] Landscape solo para ChartFullscreenScreen
  - [ ] Detectar orientación y adaptar layout

### 4.9 API Client Mobile (Compartido con Web)

- [ ] Configurar Axios instance (`lib/api-client.ts`):
  - [ ] Base URL desde env variable
  - [ ] Auth interceptor: token desde MMKV secure storage
  - [ ] Refresh token en 401
  - [ ] Error handler: mapear a tipo consistente
  - [ ] Timeout: 15s (mobile puede tener conexión lenta)
- [ ] React Query config para mobile:
  - [ ] `staleTime: 2 * 60 * 1000` (2 min, más agresivo que web)
  - [ ] `cacheTime: 60 * 60 * 1000` (1 hora, para offline)
  - [ ] `refetchOnReconnect: true` (refetch al reconectar)
  - [ ] Persistir cache en MMKV con `@tanstack/query-sync-storage-persister`
- [ ] Hooks por feature (mismos que web, adaptados):
  - [ ] `useSensors()`, `useSensor(id)`, `useSensorReadings(id, range)`
  - [ ] `useAlerts()`, `useAcknowledgeAlert()`
  - [ ] `useDashboardData()`
  - [ ] `useGateways()`
- [ ] WebSocket manager (compartido con web):
  - [ ] Conectar/desconectar según estado de la app (foreground/background)
  - [ ] Desconectar en background para ahorrar batería
  - [ ] Reconectar al volver a foreground

### 4.10 Android — Configuración, Build y Assets

- [ ] Configurar `eas.json` para Android:
  - [ ] Profile `development`: APK debug para testing
  - [ ] Profile `preview`: APK release para testers
  - [ ] Profile `production`: AAB (Android App Bundle) para Google Play
- [ ] Configurar `app.json` para Android:
  - [ ] `android.package: "com.echosmart.app"`
  - [ ] `android.versionCode: 1` (incrementar en cada build)
  - [ ] `android.adaptiveIcon.foregroundImage`: usar `assets/platform/android/adaptive-icon-foreground.png`
  - [ ] `android.adaptiveIcon.backgroundColor: "#000000"`
  - [ ] `android.permissions: ["INTERNET", "ACCESS_NETWORK_STATE", "RECEIVE_BOOT_COMPLETED", "VIBRATE"]`
  - [ ] `android.splash.image`: usar `assets/platform/android/splash-xxxhdpi.png`
  - [ ] `android.splash.backgroundColor: "#000000"`
- [ ] Generar Keystore para firma:
  - [ ] `keytool -genkey -v -keystore echosmart.keystore -alias echosmart -keyalg RSA -keysize 2048 -validity 10000`
  - [ ] Guardar keystore de forma segura (nunca en git)
  - [ ] Configurar en EAS Secrets
- [ ] Build APK de desarrollo: `eas build --platform android --profile development`
- [ ] Build APK de preview: `eas build --platform android --profile preview`
- [ ] Build AAB de producción: `eas build --platform android --profile production`
- [ ] Probar en emulador Android (Android Studio AVD):
  - [ ] Pixel 4 API 33 (Android 13)
  - [ ] Pixel 7 API 34 (Android 14)
  - [ ] Samsung Galaxy S21 (si disponible)
- [ ] Probar en dispositivos Android reales (3+ dispositivos, diferentes marcas):
  - [ ] Verificar que UI se ve como mockups
  - [ ] Verificar push notifications
  - [ ] Verificar biometría (fingerprint)
  - [ ] Verificar offline mode
  - [ ] Verificar performance (60fps en listas, scroll suave)
- [ ] Configurar Google Play Console:
  - [ ] Crear app "EchoSmart" con screenshots de `assets/mockups/mobile/`
  - [ ] Upload feature graphic de `assets/platform/android/feature-graphic.png`
  - [ ] Configurar internal testing track
  - [ ] Upload AAB
- [ ] Publicar en Google Play:
  - [ ] Internal testing → closed beta → open beta → production

### 4.11 iOS — Configuración, Build y Assets

- [ ] Configurar `eas.json` para iOS:
  - [ ] Profile `development`: build para simulador
  - [ ] Profile `preview`: ad-hoc IPA para testers (con provisioning profile)
  - [ ] Profile `production`: App Store build
- [ ] Configurar `app.json` para iOS:
  - [ ] `ios.bundleIdentifier: "com.echosmart.app"`
  - [ ] `ios.buildNumber: "1"` (incrementar en cada build)
  - [ ] `ios.supportsTablet: true`
  - [ ] `ios.icon`: usar `assets/platform/ios/app-icon-1024.png`
  - [ ] `ios.splash.image`: usar `assets/platform/ios/splash-super-retina.png`
  - [ ] `ios.splash.backgroundColor: "#000000"`
  - [ ] `ios.infoPlist`: configurar permisos con mensajes:
    - [ ] `NSCameraUsageDescription: "Para escanear códigos QR de sensores"`
    - [ ] `NSFaceIDUsageDescription: "Para login seguro con Face ID"`
  - [ ] `ios.config.usesNonExemptEncryption: false`
- [ ] Configurar Apple Developer account:
  - [ ] Crear App ID: `com.echosmart.app`
  - [ ] Crear provisioning profiles (development + distribution)
  - [ ] Configurar Push Notification capability (APNs key)
  - [ ] Configurar en EAS Credentials
- [ ] Adaptar UI para convenciones iOS:
  - [ ] SafeAreaView en todas las pantallas
  - [ ] Large titles en navigation bar (estilo iOS moderno)
  - [ ] Swipe from edge to go back (nativo de React Navigation)
  - [ ] Bottom tab bar con SafeArea (iPhone con notch/Dynamic Island)
  - [ ] Action sheets en vez de dropdowns (estilo iOS)
- [ ] Build para simulador: `eas build --platform ios --profile development`
- [ ] Build IPA ad-hoc: `eas build --platform ios --profile preview`
- [ ] Build App Store: `eas build --platform ios --profile production`
- [ ] Probar en simulador iOS (Xcode):
  - [ ] iPhone 15 Pro (iOS 17)
  - [ ] iPhone SE 3 (pantalla pequeña)
  - [ ] iPad Pro (tablet layout)
- [ ] Probar en dispositivo iOS real:
  - [ ] Verificar Face ID / Touch ID
  - [ ] Verificar push notifications via APNs
  - [ ] Verificar UI idéntica a mockups
  - [ ] Verificar SafeArea en diferentes modelos
- [ ] Configurar App Store Connect:
  - [ ] Crear app "EchoSmart" con screenshots de `assets/mockups/mobile/`
  - [ ] Configurar TestFlight
  - [ ] Upload build
- [ ] Publicar en App Store:
  - [ ] TestFlight internal → external → App Store review → release

### 4.12 Mobile — Tests Completos

- [ ] Configurar testing:
  - [ ] Jest + React Native Testing Library
  - [ ] Mock de módulos nativos: `@react-native-community/netinfo`, `expo-notifications`, etc.
  - [ ] Mock de `react-navigation`: `@react-navigation/native/testing`
- [ ] Tests unitarios para CADA hook personalizado
- [ ] Tests de componentes con React Native Testing Library:
  - [ ] Todos los componentes compartidos (Button, Input, Card, etc.)
  - [ ] SensorCard, MetricCard, AlertCard
- [ ] Tests de pantallas:
  - [ ] LoginScreen: input, validation, submit, error, biometric
  - [ ] DashboardScreen: render metrics, pull-to-refresh
  - [ ] SensorsScreen: list, filter, search, empty state
  - [ ] SensorDetailScreen: render chart, stats
  - [ ] AlertsScreen: list, swipe actions
- [ ] Tests de navegación:
  - [ ] Auth flow: Login → Dashboard
  - [ ] Sensor flow: Sensors → Detail → Fullscreen Chart
  - [ ] Deep linking: URL → correct screen
- [ ] Tests de integración:
  - [ ] Login → Dashboard → Sensor Detail (full flow)
  - [ ] Offline mode: cache, queue, reconnect sync
  - [ ] Push notification → deep link to screen
- [ ] Performance:
  - [ ] 60fps en FlatList con 100+ items (usar Flashlight)
  - [ ] App launch < 3 seconds
  - [ ] Memory: no leaks en navegación entre pantallas

### 4.13 Mobile — Calidad de Código

- [ ] ESLint + Prettier strict mode para React Native + TypeScript
- [ ] CERO `any` en TypeScript
- [ ] CERO `console.log` — usar `lib/logger.ts`
- [ ] Type-safe navigation con `@react-navigation/native` generic types
- [ ] Crear `mobile/README.md` con:
  - [ ] Guía de setup de desarrollo (Expo Go + EAS)
  - [ ] Estructura del proyecto explicada
  - [ ] Cómo compilar APK y IPA
  - [ ] Cómo probar push notifications
  - [ ] Cómo probar en emuladores y dispositivos reales
  - [ ] Design system: tokens, componentes, colores

---

## Fase 5: Aplicación de Escritorio — Electron + React (Semanas 17–20)

> 🏛️ **Clean Architecture en Electron**: Separar main process (Node.js) de renderer process (React). Comunicación exclusivamente vía IPC con preload scripts seguros.

> 🖥️ **Stack Definido**: Electron 28 + React 18 (mismo frontend/) + TypeScript. Compila a **EXE (Windows)** vía electron-builder NSIS, **DMG (macOS)** vía electron-builder DMG, y **AppImage (Linux)** vía electron-builder AppImage.

### 5.1 Definición de Tecnologías y Justificación

| Decisión | Elección | Justificación |
|----------|----------|---------------|
| **Framework** | Electron 28 | Permite reutilizar el frontend React web como renderer. Acceso a APIs del sistema (tray, menú, notificaciones nativas, filesystem) |
| **Renderer** | React 18 (mismo frontend/) | Reutilizar 100% del frontend web. Sin duplicar UI |
| **Lenguaje** | TypeScript | Consistencia con web y mobile. Type safety para IPC channels |
| **NO Tauri** | Descartado | Aunque más ligero, requiere Rust para el backend y no es tan maduro para nuestro uso |
| **NO .NET MAUI / WPF** | Descartado | Solo para Windows. Electron cubre las 3 plataformas |
| **NO Qt / C++** | Descartado | Complejidad excesiva, no permite reutilizar frontend React |
| **Builder** | electron-builder | Más maduro que electron-forge, soporta NSIS, DMG, AppImage, auto-update |
| **Auto-Update** | electron-updater | Integrado con electron-builder, soporta GitHub Releases como update server |
| **Storage** | electron-store | JSON encriptado en disco, API simple key-value |
| **IPC** | contextBridge | Exposición segura de APIs del main al renderer. NUNCA nodeIntegration: true |

### 5.2 Arquitectura Electron

```
desktop/
├── src/
│   ├── main/                    # Main process (Node.js)
│   │   ├── main.ts              # Entry point, BrowserWindow, lifecycle
│   │   ├── menu.ts              # Menú nativo por plataforma
│   │   ├── tray.ts              # Icono en bandeja del sistema
│   │   ├── ipc-handlers.ts      # Manejadores IPC tipados
│   │   ├── auto-updater.ts      # Auto-actualización vía GitHub Releases
│   │   ├── local-gateway.ts     # Descubrimiento y conexión a gateways LAN
│   │   ├── store.ts             # Configuración persistente (electron-store)
│   │   ├── notifications.ts     # Notificaciones nativas del OS
│   │   ├── protocol.ts          # Custom protocol handler (echosmart://)
│   │   └── logger.ts            # Logger para main process
│   ├── preload/
│   │   └── preload.ts           # contextBridge: exponer APIs seguras al renderer
│   ├── renderer/                # Frontend React (symlink o copy de frontend/dist)
│   │   └── index.html           # Entry point del renderer
│   └── shared/
│       └── ipc-channels.ts      # Constantes de IPC channels compartidas
├── assets/
│   ├── icon.ico                 # Windows icon (de assets/icons/ico/app.ico)
│   ├── icon.icns                # macOS icon (generado desde PNG 512px)
│   ├── icon.png                 # Linux icon (512px)
│   ├── tray-icon.png            # Tray icon 32px (de assets/platform/desktop/)
│   ├── tray-icon@2x.png         # Tray icon 64px (Retina)
│   ├── dmg-background.png       # DMG background (de assets/platform/desktop/)
│   └── installer-banner.bmp     # NSIS banner (de assets/platform/desktop/)
├── electron-builder.yml         # Configuración de build
├── package.json
├── tsconfig.json
└── README.md
```

### 5.3 Configuración del Proyecto

- [x] Configurar proyecto Electron
- [x] Implementar main process básico
- [x] Implementar preload scripts
- [x] Integrar frontend React como renderer
- [ ] Migrar main process a TypeScript:
  - [ ] `main.js` → `main.ts`
  - [ ] `preload.js` → `preload.ts`
  - [ ] Configurar `tsconfig.json` para main process (target: Node.js)
  - [ ] Configurar bundling con `electron-vite` o `esbuild`
- [ ] Configurar `electron-builder.yml`:
  ```yaml
  appId: "com.echosmart.desktop"
  productName: "EchoSmart"
  directories:
    output: "dist"
  files:
    - "src/**/*"
    - "assets/**/*"
  win:
    target: ["nsis"]
    icon: "assets/icon.ico"
  mac:
    target: ["dmg", "zip"]
    icon: "assets/icon.icns"
    category: "public.app-category.utilities"
  linux:
    target: ["AppImage", "deb"]
    icon: "assets/icon.png"
    category: "Utility"
  nsis:
    oneClick: false
    allowToChangeInstallationDirectory: true
    installerIcon: "assets/icon.ico"
    installerSidebar: "assets/installer-banner.bmp"
  dmg:
    background: "assets/dmg-background.png"
    iconSize: 128
    contents:
      - x: 130
        y: 220
      - x: 410
        y: 220
        type: "link"
        path: "/Applications"
  ```
- [ ] Copiar assets necesarios desde `assets/`:
  - [ ] `assets/icons/ico/app.ico` → `desktop/assets/icon.ico`
  - [ ] Generar `icon.icns` desde PNG 512px (con `png2icns` o script)
  - [ ] `assets/icons/png/app-icon-512.png` → `desktop/assets/icon.png`
  - [ ] `assets/platform/desktop/tray-icon-32.png` → `desktop/assets/tray-icon.png`
  - [ ] `assets/platform/desktop/tray-icon-64.png` → `desktop/assets/tray-icon@2x.png`
  - [ ] `assets/platform/desktop/dmg-background.png` → `desktop/assets/dmg-background.png`
  - [ ] `assets/platform/desktop/installer-banner.png` → convertir a BMP

### 5.4 Main Process — Ventana Principal

- [ ] **BrowserWindow** configuración:
  - [ ] Tamaño por defecto: 1280×800
  - [ ] Tamaño mínimo: 1024×768
  - [ ] Frame: `true` (usar frame nativo del OS)
  - [ ] titleBarStyle: `'hidden'` en macOS para look moderno
  - [ ] Background color: `#000000` (evitar flash blanco)
  - [ ] webPreferences: `{ nodeIntegration: false, contextIsolation: true, preload: './preload.ts' }`
  - [ ] Icon: `assets/icon.ico` (Windows) / `assets/icon.png` (Linux)
- [ ] **Window state persistence** (electron-store):
  - [ ] Guardar posición (x, y) y tamaño (width, height) al cerrar
  - [ ] Restaurar posición y tamaño al abrir
  - [ ] Guardar si estaba maximizada
  - [ ] Verificar que la ventana está en un monitor visible (multi-monitor)
- [ ] **Single instance lock**:
  - [ ] `app.requestSingleInstanceLock()`
  - [ ] Si segunda instancia: focus en la primera, no abrir nueva
  - [ ] Pasar argumentos de CLI de segunda instancia a primera
- [ ] **Splash screen al iniciar**:
  - [ ] Ventana pequeña con logo de EchoSmart durante carga
  - [ ] Cerrar splash y mostrar main window cuando renderer está listo
  - [ ] Timeout: máximo 5 segundos
- [ ] **Lifecycle events**:
  - [ ] `will-quit`: guardar estado, desconectar
  - [ ] `before-quit`: confirmar si hay datos no guardados
  - [ ] macOS: `activate` → mostrar ventana si está oculta
  - [ ] macOS: `window-all-closed` → NO quit (keep in dock)

### 5.5 IPC (Inter-Process Communication) — Tipado y Seguro

- [ ] Definir IPC channels tipados (`shared/ipc-channels.ts`):
  ```typescript
  export const IPC_CHANNELS = {
    // Gateway
    'gateway:discover': 'gateway:discover',        // () => Gateway[]
    'gateway:connect': 'gateway:connect',          // (gatewayId: string) => boolean
    'gateway:status': 'gateway:status',            // () => GatewayStatus
    // App
    'app:get-version': 'app:get-version',          // () => string
    'app:check-update': 'app:check-update',        // () => UpdateInfo | null
    'app:install-update': 'app:install-update',    // () => void
    'app:open-external': 'app:open-external',      // (url: string) => void
    // Store
    'store:get': 'store:get',                      // (key: string) => any
    'store:set': 'store:set',                      // (key: string, value: any) => void
    // Notifications
    'notification:show': 'notification:show',      // (title: string, body: string) => void
    // Export
    'export:csv': 'export:csv',                    // (data: any[], filename: string) => string
    'export:pdf': 'export:pdf',                    // (html: string, filename: string) => string
  } as const;
  ```
- [ ] Implementar IPC handlers en main (`ipc-handlers.ts`):
  - [ ] Cada handler tipado con input/output
  - [ ] Error handling: envolver en try/catch, devolver resultado o error
  - [ ] Validación de inputs (no confiar en renderer)
- [ ] Implementar preload bridge (`preload.ts`):
  - [ ] `contextBridge.exposeInMainWorld('electronAPI', { ... })`
  - [ ] Solo exponer funciones específicas, NUNCA `require`, `fs`, `child_process`
  - [ ] Cada función expuesta es un wrapper de `ipcRenderer.invoke`
- [ ] TypeScript declaration para `window.electronAPI`:
  - [ ] `global.d.ts` con tipo `ElectronAPI` para autocompletado en renderer
- [ ] Tests de seguridad:
  - [ ] Verificar que `nodeIntegration` es `false`
  - [ ] Verificar que `contextIsolation` es `true`
  - [ ] Verificar que renderer NO tiene acceso a `require`

### 5.6 Menú Nativo

- [ ] **Windows/Linux menú**:
  - [ ] File → Export Data (CSV/PDF), Preferences, Exit
  - [ ] View → Reload, Toggle DevTools (dev only), Fullscreen, Zoom In/Out/Reset
  - [ ] Gateway → Discover Gateways, Connect, Disconnect
  - [ ] Help → About EchoSmart, Check for Updates, Documentation (open URL), Report Bug
  - [ ] Shortcuts: Ctrl+R (reload), Ctrl+Shift+I (devtools), F11 (fullscreen), Ctrl+Q (quit)
- [ ] **macOS menú** (adaptar a convenciones):
  - [ ] EchoSmart → About, Preferences (Cmd+,), Services, Hide, Quit
  - [ ] File → Export, Close Window (Cmd+W)
  - [ ] Edit → Undo, Redo, Cut, Copy, Paste, Select All
  - [ ] View → Reload, Toggle DevTools, Fullscreen, Zoom
  - [ ] Gateway → Discover, Connect, Disconnect
  - [ ] Window → Minimize, Zoom, Close
  - [ ] Help → Search, About, Updates, Documentation
  - [ ] Shortcuts: Cmd+R, Cmd+Opt+I, Ctrl+Cmd+F, Cmd+Q
- [ ] Context menu: right-click en elements del renderer

### 5.7 System Tray

- [ ] **Tray icon**:
  - [ ] Usar `assets/tray-icon.png` (32px) y `tray-icon@2x.png` (64px Retina)
  - [ ] macOS: template icon (monocromo, adapta a dark/light menu bar)
  - [ ] Color del ícono según estado: normal (verde), alerta (rojo), offline (gris)
- [ ] **Context menu** del tray:
  - [ ] "Open EchoSmart" → mostrar ventana
  - [ ] "Status: X sensors online" (info, no clickeable)
  - [ ] Separator
  - [ ] "Alerts: X active" → abrir ventana en página de alertas
  - [ ] "Gateways: X online" → abrir ventana en página de gateways
  - [ ] Separator
  - [ ] "Check for Updates..."
  - [ ] "Quit EchoSmart"
- [ ] **Minimize to tray**:
  - [ ] Al cerrar ventana (click X): minimizar a tray, no quit
  - [ ] Para quit: usar tray menu → Quit, o File → Exit
  - [ ] Notificación en primera vez: "EchoSmart sigue corriendo en la bandeja"
- [ ] **Notificaciones nativas**:
  - [ ] Usar `Notification` API del OS
  - [ ] Mostrar notificaciones de alertas críticas incluso si la app está en tray
  - [ ] Click en notificación → abrir ventana en la página relevante
  - [ ] Sonido de notificación (opcional, configurable)

### 5.8 Auto-Update

- [ ] Configurar `electron-updater`:
  - [ ] Update server: GitHub Releases del repositorio
  - [ ] Check for updates al iniciar la app
  - [ ] Check periódico: cada 4 horas
  - [ ] Si hay update disponible: notificar al usuario con dialog
  - [ ] Dialog: "New version X.Y.Z available. Download now?"
  - [ ] Descargar en background con progress bar
  - [ ] Una vez descargado: "Restart to install?" o instalar al cerrar
  - [ ] Auto-download para updates de seguridad (patch versions)
- [ ] Configurar firma de código:
  - [ ] Windows: code signing certificate
  - [ ] macOS: Apple Developer certificate + notarización
  - [ ] Sin firma: warning de seguridad al instalar (no ideal, pero funcional)

### 5.9 Conexión Directa al Gateway (LAN)

- [ ] **Descubrimiento de gateways** en red local:
  - [ ] mDNS/Bonjour discovery (`bonjour-service` package)
  - [ ] Buscar servicios `_echosmart._tcp`
  - [ ] Listar gateways encontrados con nombre, IP, versión
- [ ] **Conexión HTTP directa**:
  - [ ] Conectar a gateway por IP local (ej: `http://192.168.1.100:5000`)
  - [ ] Obtener lecturas en tiempo real sin cloud
  - [ ] Indicador en UI: "Modo Directo" (ícono LAN) vs "Modo Cloud" (ícono nube)
  - [ ] Menor latencia: < 100ms vs cloud ~500ms
- [ ] **Fallback**:
  - [ ] Si gateway no accesible en LAN → fallback a cloud automáticamente
  - [ ] Reconectar a LAN cuando gateway vuelva a ser accesible
  - [ ] Priority: LAN > Cloud

### 5.10 Almacenamiento Local

- [ ] **electron-store** para configuración:
  - [ ] Credenciales: token encriptado
  - [ ] Preferencias: idioma, tema, units
  - [ ] Window state: posición, tamaño, maximizada
  - [ ] Gateway config: última conexión, modo (LAN/Cloud)
  - [ ] Cache de últimas lecturas (para acceso offline rápido)
- [ ] Encriptar store con clave derivada del OS keychain

### 5.11 Windows — Build y Distribución

- [ ] Build NSIS installer:
  - [ ] `electron-builder --win --publish never`
  - [ ] Installer con sidebar banner personalizado
  - [ ] Opciones: directorio de instalación, crear shortcut, auto-start
  - [ ] Output: `EchoSmart-Setup-{version}.exe`
- [ ] Generar MSI installer (alternativo):
  - [ ] Para deployment empresarial
- [ ] Desktop shortcut con ícono personalizado
- [ ] Start menu entry
- [ ] Auto-start con Windows (opcional, configurable)
- [ ] Probar en:
  - [ ] Windows 10 (21H2+)
  - [ ] Windows 11 (22H2+)
- [ ] Verificar: instalación, primera ejecución, auto-update, desinstalación

### 5.12 macOS — Build y Distribución

- [ ] Build DMG:
  - [ ] `electron-builder --mac --publish never`
  - [ ] DMG con fondo personalizado y drag-to-Applications
  - [ ] Output: `EchoSmart-{version}.dmg`
- [ ] Build ZIP (para auto-update):
  - [ ] `electron-builder --mac --publish never -c.mac.target=zip`
- [ ] Configurar Info.plist:
  - [ ] `LSMinimumSystemVersion: "10.15"` (Catalina+)
  - [ ] `CFBundleDocumentTypes` para archivos `.echosmart`
- [ ] Firmar con Apple Developer certificate:
  - [ ] Code signing con `codesign`
  - [ ] Notarización con `xcrun notarytool`
- [ ] Adaptar para convenciones macOS:
  - [ ] Menú en menu bar (no en ventana)
  - [ ] Dock icon con badge de alertas
  - [ ] Cmd+, para preferences
  - [ ] Traffic lights (close/minimize/maximize)
- [ ] Probar en:
  - [ ] macOS Ventura (13)
  - [ ] macOS Sonoma (14)
  - [ ] Apple Silicon (M1/M2) — verificar build arm64

### 5.13 Linux — Build y Distribución

- [ ] Build AppImage:
  - [ ] `electron-builder --linux --publish never`
  - [ ] Output: `EchoSmart-{version}.AppImage`
  - [ ] Portable, sin instalación
- [ ] Build .deb (Debian/Ubuntu):
  - [ ] `electron-builder --linux deb`
  - [ ] Desktop entry (`.desktop` file) con ícono
  - [ ] Integración con menú de aplicaciones
- [ ] Build .snap (opcional):
  - [ ] Para Snap Store
- [ ] Adaptar para Linux:
  - [ ] Notificaciones: libnotify (GNOME) / KDE
  - [ ] Tray icon: AppIndicator
- [ ] Probar en:
  - [ ] Ubuntu 22.04 LTS
  - [ ] Ubuntu 24.04 LTS
  - [ ] Fedora 39+ (opcional)

### 5.14 Desktop — Tests y Calidad

- [ ] Tests de IPC handlers:
  - [ ] Cada handler: input válido, input inválido, error handling
- [ ] Tests de preload scripts:
  - [ ] Verificar que SOLO expone funciones permitidas
  - [ ] Verificar que NO expone require, fs, child_process
- [ ] Tests de menú nativo:
  - [ ] Verificar items de menú por plataforma
  - [ ] Verificar shortcuts
- [ ] Tests de tray:
  - [ ] Minimize to tray
  - [ ] Context menu items
  - [ ] Notification click
- [ ] Tests de auto-update:
  - [ ] Check for updates
  - [ ] Download progress
  - [ ] Install and restart
- [ ] Security audit:
  - [ ] `nodeIntegration: false` ✓
  - [ ] `contextIsolation: true` ✓
  - [ ] `sandbox: true` (si posible) ✓
  - [ ] CSP (Content Security Policy) configurado
  - [ ] No `eval()` en renderer
  - [ ] Validar URLs antes de `shell.openExternal`
- [ ] ESLint para main process + renderer
- [ ] Crear `desktop/README.md` con:
  - [ ] Guía de setup de desarrollo
  - [ ] Arquitectura main/renderer/preload explicada
  - [ ] Cómo compilar para cada plataforma
  - [ ] Cómo configurar auto-update
  - [ ] Cómo firmar y notarizar

---

## Fase 6: Infraestructura Local de Desarrollo (Semanas 17–18)

> 🏗️ **PRIORIDAD**: La infraestructura local se despliega ANTES del testing. Se debe poder levantar todo el entorno de desarrollo con UN SOLO comando, incluyendo emuladores de sensores.

### 6.1 Script de Despliegue Local — `setup-dev.sh`

- [ ] Crear script principal `infra/scripts/setup-dev.sh` (idempotente, re-ejecutable)
- [ ] Detectar sistema operativo (Linux/macOS/Windows WSL2)
- [ ] Verificar prerequisitos: Docker, Docker Compose, Python 3.11+, Node.js 18+, Git
- [ ] Instalar prerequisitos faltantes automáticamente (apt/brew/choco)
- [ ] Crear directorio de trabajo `/opt/echosmart-dev/` o `$HOME/.echosmart/`
- [ ] Generar archivos `.env` desde templates `.env.example` con valores de desarrollo
- [ ] Generar claves JWT (RS256) automáticamente para desarrollo
- [ ] Generar certificados SSL self-signed para desarrollo local
- [ ] Ejecutar `docker-compose -f docker-compose.dev.yml up -d`
- [ ] Esperar a que todos los servicios estén healthy (health checks)
- [ ] Ejecutar migraciones de base de datos (Alembic)
- [ ] Ejecutar seed de datos iniciales (tenant, admin user, demo gateways/sensors)
- [ ] Iniciar emuladores de sensores (contenedor Docker)
- [ ] Verificar conectividad entre todos los servicios
- [ ] Imprimir resumen con URLs de acceso y credenciales de desarrollo
- [ ] Crear script `infra/scripts/teardown-dev.sh` para limpiar todo

### 6.2 Docker Compose para Desarrollo — `docker-compose.dev.yml`

- [ ] **PostgreSQL 16** (puerto 5432):
  - [ ] Volumen persistente para datos
  - [ ] Init script para crear bases de datos (`echosmart_dev`, `echosmart_test`)
  - [ ] Configuración de performance para desarrollo (shared_buffers, work_mem)
  - [ ] Health check: `pg_isready`
- [ ] **InfluxDB 2.7** (puerto 8086):
  - [ ] Setup automático: org `echosmart`, bucket `sensor_readings`
  - [ ] Retention policy: 30 días para desarrollo
  - [ ] Health check: `/health`
- [ ] **Redis 7** (puerto 6379):
  - [ ] Configuración: maxmemory 256MB, eviction policy allkeys-lru
  - [ ] Health check: `redis-cli ping`
- [ ] **Mosquitto MQTT** (puertos 1883, 9001 WebSocket):
  - [ ] Config: anonymous access para desarrollo
  - [ ] Listener WebSocket para frontend
  - [ ] Log de mensajes para debugging
  - [ ] Health check: `mosquitto_sub -t '$SYS/broker/version' -C 1`
- [ ] **Backend FastAPI** (puerto 8000):
  - [ ] Hot-reload con `--reload`
  - [ ] Volumen bind mount para código fuente
  - [ ] Depends on: postgres, redis, influxdb, mosquitto
  - [ ] Health check: `GET /health`
- [ ] **Frontend React** (puerto 3000):
  - [ ] Vite dev server con HMR
  - [ ] Volumen bind mount para código fuente
  - [ ] Proxy a backend para `/api/*`
- [ ] **Nginx** (puertos 80, 443):
  - [ ] Reverse proxy: `/` → frontend, `/api/` → backend, `/ws/` → backend WebSocket
  - [ ] SSL con certificados self-signed
  - [ ] Config de desarrollo (sin cache, logs verbose)
- [ ] **Mailhog** (puertos 1025 SMTP, 8025 UI):
  - [ ] Capturar emails de desarrollo (verificación, alertas, reportes)
  - [ ] UI web para visualizar emails
- [ ] **Adminer** (puerto 8080):
  - [ ] UI web para inspeccionar PostgreSQL en desarrollo
- [ ] Red Docker interna `echosmart-dev` (bridge)
- [ ] `.dockerignore` para cada servicio

### 6.3 Emulador de Sensores para Desarrollo

- [ ] Crear `gateway/emulator/` — Emulador de sensores como servicio independiente
- [ ] `sensor_emulator.py` — Proceso que genera lecturas realistas:
  - [ ] Temperatura: 18–32°C con variación diurna sinusoidal (frío noche, calor día)
  - [ ] Humedad: 55–85% inversamente correlacionada con temperatura
  - [ ] Luminosidad: 0–50,000 lux con ciclo día/noche
  - [ ] Humedad suelo: 30–80% con degradación gradual (simular secado)
  - [ ] CO₂: 350–1200 ppm con picos durante noche
- [ ] Publicar lecturas vía MQTT a topics `echosmart/gw-emulator/sensor/{type}`
- [ ] Soporte para múltiples gateways emulados simultáneamente
- [ ] Parámetros configurables: intervalo de polling, ruido, drift, eventos especiales
- [ ] Modo "escenarios": simular condiciones específicas:
  - [ ] Escenario `heat-wave`: temperatura sube gradualmente a 45°C
  - [ ] Escenario `frost`: temperatura baja a -2°C en 2 horas
  - [ ] Escenario `sensor-failure`: sensor deja de responder
  - [ ] Escenario `network-outage`: gateway se desconecta 10 minutos y reconecta
  - [ ] Escenario `normal-day`: ciclo completo de 24 horas comprimido en 10 minutos
- [ ] Dockerfile para emulador: `infra/docker/emulator.Dockerfile`
- [ ] Incluir emulador en `docker-compose.dev.yml`
- [ ] API REST del emulador para cambiar escenarios en runtime
- [ ] Tests: emulador genera datos dentro de rangos esperados

### 6.4 Scripts de Datos y Migración

- [ ] `infra/scripts/seed-data.sh` — Poblar datos de demo:
  - [ ] Crear tenant `EchoSmart Demo`
  - [ ] Crear usuarios: admin (`admin@echosmart.local`), operator, viewer
  - [ ] Crear gateway `gw-emulator-01` asociado al tenant
  - [ ] Crear 5 sensores asociados al gateway
  - [ ] Generar 7 días de lecturas históricas (una lectura/minuto por sensor)
  - [ ] Crear alertas de ejemplo (3 activas, 5 resueltas)
  - [ ] Crear reportes de ejemplo (PDF de la última semana)
- [ ] `infra/scripts/reset-dev.sh` — Resetear base de datos a estado limpio
- [ ] `infra/scripts/backup-dev.sh` — Backup del estado actual de desarrollo
- [ ] `infra/scripts/migrate.sh` — Ejecutar migraciones de Alembic
- [ ] `infra/scripts/generate-keys.sh` — Generar JWT keys, API keys, etc.
- [ ] `infra/scripts/check-health.sh` — Verificar estado de todos los servicios
- [ ] `infra/scripts/logs.sh` — Ver logs de todos los servicios (o uno específico)
- [ ] Todos los scripts documentados con `--help` y mensajes de error claros

### 6.5 Makefile para Desarrollo

- [ ] Crear `Makefile` en la raíz del proyecto:
  - [ ] `make setup` — Ejecutar setup-dev.sh completo
  - [ ] `make up` — Levantar todos los servicios
  - [ ] `make down` — Detener todos los servicios
  - [ ] `make restart` — Reiniciar todos los servicios
  - [ ] `make logs` — Ver logs en tiempo real
  - [ ] `make test` — Ejecutar TODOS los tests (backend + frontend + gateway)
  - [ ] `make test-backend` — Solo tests de backend con coverage
  - [ ] `make test-frontend` — Solo tests de frontend con coverage
  - [ ] `make test-gateway` — Solo tests de gateway con coverage
  - [ ] `make lint` — Linting de todos los componentes
  - [ ] `make format` — Formatear código (black + prettier)
  - [ ] `make migrate` — Ejecutar migraciones
  - [ ] `make seed` — Seed de datos de demo
  - [ ] `make reset` — Resetear todo el entorno
  - [ ] `make clean` — Limpiar volúmenes, cache, imágenes huérfanas
  - [ ] `make emulator-scenario SCENARIO=heat-wave` — Cambiar escenario del emulador
  - [ ] `make build` — Build de producción de todos los componentes
  - [ ] `make iso-server` — Generar ISO del servidor
  - [ ] `make iso-gateway` — Generar ISO del Raspberry Pi
  - [ ] Documentar cada target con `make help`

---

## Fase 7: Infraestructura de Producción y DevOps (Semanas 19–22)

> 🏛️ **Infrastructure as Code**: Toda la infraestructura definida en archivos versionados. Reproducible al 100%.

### 7.1 Docker — Containerización para Producción

- [ ] **Backend Dockerfile** (`infra/docker/backend.Dockerfile`):
  - [ ] Multi-stage build: builder (pip install) → runner (slim image < 200MB)
  - [ ] Non-root user (`echosmart:echosmart`, UID 1000)
  - [ ] Health check: `curl -f http://localhost:8000/health`
  - [ ] Optimizar layer caching (COPY requirements.txt primero)
  - [ ] Labels: version, commit SHA, build date
  - [ ] Security: no root, read-only filesystem donde sea posible
- [ ] **Frontend Dockerfile** (`infra/docker/frontend.Dockerfile`):
  - [ ] Multi-stage: node (build) → nginx:alpine (serve)
  - [ ] SPA fallback config en nginx (`try_files $uri /index.html`)
  - [ ] Gzip compression habilitado
  - [ ] Cache headers para assets estáticos (1 año)
  - [ ] Imagen final < 50MB
  - [ ] Build args para API_URL en tiempo de build
- [ ] **Gateway Dockerfile** (`infra/docker/gateway.Dockerfile`):
  - [ ] Para testing en contenedor (sin GPIO real)
  - [ ] Modo simulación por defecto
  - [ ] Health check: `echosmart sysinfo --version=true`
- [ ] `docker-compose.prod.yml`:
  - [ ] Backend: gunicorn con 4 workers + uvicorn
  - [ ] Frontend: nginx optimizado
  - [ ] PostgreSQL: configuración de producción (16GB RAM)
  - [ ] SSL termination en Nginx (Let's Encrypt)
  - [ ] Restart policies: `unless-stopped`
  - [ ] Resource limits (CPU, memory) para cada servicio
  - [ ] Logging driver: json-file con rotation (10MB, 5 archivos)
  - [ ] Networks separadas: frontend, backend, data
- [ ] `docker-compose.test.yml` para CI/CD
- [ ] `.dockerignore` optimizado para cada servicio

### 7.2 Kubernetes — Orquestación

- [x] Manifiestos básicos en `infra/k8s/`
- [ ] **Namespace**: `echosmart-prod`, `echosmart-staging`
- [ ] **Backend Deployment**:
  - [ ] 3 réplicas (min 2, max 10)
  - [ ] Readiness probe: `GET /health` cada 10s
  - [ ] Liveness probe: `GET /health` cada 30s
  - [ ] Startup probe: 60s max
  - [ ] Resource requests: 256Mi RAM, 250m CPU
  - [ ] Resource limits: 512Mi RAM, 500m CPU
  - [ ] Rolling update strategy (maxSurge=1, maxUnavailable=0)
  - [ ] Anti-affinity: no dos pods en el mismo nodo
- [ ] **Frontend Deployment** (Nginx serving static)
- [ ] **PostgreSQL StatefulSet**:
  - [ ] PVC 50GB (expandable)
  - [ ] Backup CronJob diario (pg_dump → S3)
  - [ ] Resource limits: 1Gi RAM, 1 CPU
- [ ] **InfluxDB StatefulSet** con PVC 100GB
- [ ] **Redis Deployment** (256Mi memory limit)
- [ ] **Mosquitto Deployment** (configuración de producción)
- [x] **Ingress** con TLS:
  - [ ] cert-manager con Let's Encrypt
  - [ ] Redirect HTTP → HTTPS
  - [ ] Rate limiting annotations
  - [ ] WebSocket passthrough
- [ ] **HPA** (Horizontal Pod Autoscaler): backend scale basado en CPU (target 70%)
- [ ] **NetworkPolicy**: segmentación de red (frontend → backend → data)
- [ ] **ConfigMap**: configuraciones no sensibles
- [ ] **Secret**: credenciales encriptadas (sealed-secrets)
- [ ] **PodDisruptionBudget**: mínimo 1 pod backend siempre disponible
- [ ] Kustomize overlays para `dev`, `staging`, `prod`
- [ ] Helm chart para deployment simplificado

### 7.3 CI/CD — GitHub Actions

- [ ] **CI Pipeline** (`.github/workflows/ci.yml`):
  - [ ] Trigger: push a cualquier branch + PR a main
  - [ ] Matrix: Python 3.11/3.12, Node 18/20
  - [ ] Jobs paralelos:
    - [ ] `lint-backend`: black + isort + ruff + mypy
    - [ ] `lint-frontend`: ESLint + Prettier + TypeScript check
    - [ ] `lint-gateway`: cppcheck + clang-format
    - [ ] `test-backend`: pytest con PostgreSQL service container + coverage
    - [ ] `test-frontend`: vitest con coverage
    - [ ] `test-gateway`: compilar y ejecutar binarios con --simulate
    - [ ] `security-scan`: bandit (Python) + npm audit (Node.js) + trivy (Docker)
  - [ ] Reportar cobertura como comentario en PR (codecov/coveralls)
  - [ ] Bloquear merge si cobertura < 80% o lint falla
  - [ ] Cache de dependencias (pip, npm) entre ejecuciones
- [ ] **CD Pipeline** (`.github/workflows/deploy.yml`):
  - [ ] Trigger: push a `main` (staging) o tag `v*` (producción)
  - [ ] Build Docker images multi-arch (amd64 + arm64)
  - [ ] Push a GitHub Container Registry (ghcr.io)
  - [ ] Tag: commit SHA + latest + semver
  - [ ] Deploy a staging automáticamente
  - [ ] Deploy a producción con manual approval
  - [ ] Rollback automático si health check falla post-deploy
  - [ ] Notificación Slack/Discord de deploy exitoso/fallido
- [ ] **Mobile Build** (`.github/workflows/mobile.yml`):
  - [ ] Trigger: tag `mobile-v*`
  - [ ] EAS Build Android (APK + AAB) + iOS (IPA)
  - [ ] Upload a GitHub Releases
  - [ ] Notificar a testers (TestFlight / Firebase App Distribution)
- [ ] **Desktop Build** (`.github/workflows/desktop.yml`):
  - [ ] Trigger: tag `desktop-v*`
  - [ ] Electron build: Windows (.exe, .msi), macOS (.dmg), Linux (.AppImage, .deb)
  - [ ] Code signing (Windows + macOS)
  - [ ] Upload a GitHub Releases
  - [ ] Auto-update feed (electron-updater)
- [ ] **ISO Build** (`.github/workflows/iso.yml`):
  - [ ] Trigger: tag `iso-v*`
  - [ ] Build ISO del servidor (Ubuntu 22.04 base)
  - [ ] Build ISO del Raspberry Pi (RPi OS Lite base)
  - [ ] Upload artefactos a GitHub Releases
- [ ] **Dependabot** (`.github/dependabot.yml`):
  - [ ] Python (pip): semanal
  - [ ] Node.js (npm): semanal
  - [ ] GitHub Actions: semanal
  - [ ] Docker: mensual
  - [ ] Auto-merge para patches de seguridad

### 7.4 Monitoreo y Observabilidad

- [ ] **Logging centralizado**:
  - [ ] Backend: structlog → JSON → stdout → Docker logs
  - [ ] Loki + Promtail para agregación de logs
  - [ ] Grafana Loki dashboards
  - [ ] Log retention: 30 días
- [ ] **Métricas**:
  - [ ] Prometheus scraping backend `/metrics`
  - [ ] Node Exporter para métricas del sistema
  - [ ] Custom metrics: requests/s, latency P50/P95/P99, error rate
  - [ ] Sensor readings/min, active gateways, alert rate
- [ ] **Dashboards Grafana**:
  - [ ] Dashboard: overview del sistema (CPU, RAM, disk, network)
  - [ ] Dashboard: API performance (latency, throughput, errors)
  - [ ] Dashboard: sensores (readings/min, valores actuales, tendencias)
  - [ ] Dashboard: gateways (online/offline, sync lag, errors)
  - [ ] Dashboard: alertas (activas, rate, tiempo de resolución)
- [ ] **Alertas de infraestructura** (Alertmanager):
  - [ ] CPU > 80% por 5 minutos
  - [ ] Memory > 85% por 5 minutos
  - [ ] Disk > 90%
  - [ ] API error rate > 5% por 2 minutos
  - [ ] API latency P99 > 2 segundos
  - [ ] Gateway offline > 10 minutos
  - [ ] PostgreSQL connection pool > 80%
  - [ ] Notificación vía email + Slack
- [ ] **Uptime monitoring**: Healthchecks.io o UptimeRobot
- [ ] **Error tracking**: Sentry (backend + frontend)

### 7.5 Seguridad de Infraestructura

- [ ] HTTPS obligatorio en todos los endpoints (redirect HTTP → HTTPS)
- [ ] Certificados SSL automáticos (Let's Encrypt + cert-manager)
- [ ] Firewall: solo puertos 22 (SSH), 80, 443, 8883 (MQTT TLS)
- [ ] SSH hardening: solo key-based auth, no root login, fail2ban
- [ ] Rate limiting a nivel de Nginx/Ingress (100 req/min general, 10/min login)
- [ ] WAF básico: bloquear ataques comunes (SQL injection, XSS, path traversal)
- [ ] Secrets management: Kubernetes Secrets + sealed-secrets (no hardcoded)
- [ ] Backups encriptados (GPG) con rotación (7 diarios, 4 semanales, 12 mensuales)
- [ ] Vulnerability scanning automático (Trivy en CI)
- [ ] CORS: solo dominios permitidos explícitamente
- [ ] Security headers: HSTS, X-Frame-Options, X-Content-Type-Options, CSP
- [ ] Procedimiento de incident response documentado
- [ ] Rotación de credenciales cada 90 días (automatizado)

### 7.6 Nginx — Configuración de Producción

- [ ] `infra/nginx/nginx.conf` — Configuración principal:
  - [ ] Worker processes: auto (basado en CPU cores)
  - [ ] Worker connections: 1024
  - [ ] Gzip compression para text, CSS, JS, JSON, SVG
  - [ ] Client max body size: 10MB
  - [ ] Proxy buffer sizes optimizados
- [ ] `infra/nginx/sites/echosmart.conf` — Virtual host:
  - [ ] Server block para HTTP (redirect a HTTPS)
  - [ ] Server block para HTTPS (SSL/TLS)
  - [ ] Location `/` → Frontend (React static files)
  - [ ] Location `/api/` → Backend (FastAPI proxy_pass)
  - [ ] Location `/ws/` → Backend WebSocket (proxy_pass con upgrade)
  - [ ] Location `/mqtt/` → Mosquitto WebSocket
  - [ ] Location `/grafana/` → Grafana dashboard
  - [ ] Location `/adminer/` → Adminer (solo en dev/staging)
  - [ ] Cache de assets estáticos (1 año para hashed files)
  - [ ] Security headers
  - [ ] Rate limiting zones
- [ ] SSL: protocolos TLSv1.2 y TLSv1.3 únicamente
- [ ] OCSP stapling
- [ ] Tests: verificar todas las rutas, SSL score A+ en SSL Labs

### 7.7 DNS y Dominios

- [ ] Configurar dominio principal: `echosmart.io` (o el dominio elegido)
- [ ] Subdominio API: `api.echosmart.io`
- [ ] Subdominio app web: `app.echosmart.io`
- [ ] Subdominio MQTT: `mqtt.echosmart.io`
- [ ] Subdominio Grafana: `monitor.echosmart.io`
- [ ] Subdominio de documentación: `docs.echosmart.io`
- [ ] Registros DNS: A, AAAA, CNAME, MX, TXT (SPF, DKIM, DMARC)
- [ ] Configurar CDN (CloudFlare o AWS CloudFront) para frontend
- [ ] DNS failover configurado

### 7.8 SMTP y Correo Electrónico

- [ ] Configurar servidor SMTP para envío de emails:
  - [ ] Opción A: Postfix local + DKIM + SPF
  - [ ] Opción B: Servicio externo (SendGrid / Amazon SES / Mailgun)
- [ ] Configurar registros DNS para email:
  - [ ] MX records
  - [ ] SPF: `v=spf1 include:_spf.google.com ~all`
  - [ ] DKIM: clave pública en TXT record
  - [ ] DMARC: `v=DMARC1; p=quarantine; rua=mailto:dmarc@echosmart.io`
- [ ] Templates de email HTML (Jinja2):
  - [ ] Email de verificación de cuenta
  - [ ] Email de reset de contraseña
  - [ ] Email de alerta de sensor
  - [ ] Email de reporte diario/semanal
  - [ ] Email de invitación a tenant
  - [ ] Email de bienvenida
- [ ] Cola de emails (Celery + Redis) para envío asíncrono
- [ ] Rate limiting de emails (no más de 100/hora por tenant)
- [ ] Logs de envío y bounce handling
- [ ] Tests: envío, templates, cola, SPF/DKIM validation

---

## Fase 8: ISO Personalizado del Servidor (Semanas 23–25)

> 💿 **El ISO del servidor contiene TODO el software necesario para desplegar EchoSmart en producción.** Un administrador solo necesita flashear el ISO, responder 5 preguntas de configuración, y el servidor queda 100% funcional.

### 8.1 Definición del ISO del Servidor

- [ ] Base: Ubuntu Server 22.04 LTS (64-bit, minimal)
- [ ] Nombre del ISO: `echosmart-server-v{VERSION}-amd64.iso`
- [ ] Tamaño objetivo: < 4GB
- [ ] Arquitectura soportada: amd64 (x86_64)
- [ ] Boot: UEFI + Legacy BIOS
- [ ] Particionamiento automático: 
  - [ ] `/` — 20GB (sistema operativo)
  - [ ] `/var/lib/docker` — 50GB+ (volúmenes Docker)
  - [ ] `/var/backups/echosmart` — 20GB+ (backups)
  - [ ] swap — 4GB

### 8.2 Software Pre-instalado en el ISO

- [ ] **Sistema operativo**: Ubuntu Server 22.04 LTS con actualizaciones de seguridad
- [ ] **Docker Engine** 24+ (CE, instalado desde repo oficial)
- [ ] **Docker Compose** v2 (plugin)
- [ ] **Nginx** como reverse proxy (instalado y pre-configurado)
- [ ] **Certbot** (Let's Encrypt) para certificados SSL automáticos
- [ ] **UFW** (firewall) pre-configurado: solo 22, 80, 443, 8883
- [ ] **fail2ban** para protección contra brute force SSH
- [ ] **unattended-upgrades** para actualizaciones de seguridad automáticas
- [ ] **logrotate** para rotación de logs
- [ ] **cron** jobs pre-configurados:
  - [ ] Backup de PostgreSQL diario a las 02:00
  - [ ] Backup de InfluxDB diario a las 03:00
  - [ ] Limpieza de Docker images cada semana
  - [ ] Renovación de certificados SSL (certbot renew)
  - [ ] Check de salud del sistema cada 5 minutos
- [ ] **Python 3.11+** para scripts de gestión
- [ ] **Node.js 18 LTS** (para frontend build en el servidor)
- [ ] **Git** para actualizaciones del código
- [ ] **htop**, **iotop**, **ncdu**, **tmux** para diagnóstico

### 8.3 Contenedores Docker Pre-configurados

- [ ] Imágenes Docker de EchoSmart pre-descargadas e incluidas en el ISO:
  - [ ] `echosmart-backend:latest`
  - [ ] `echosmart-frontend:latest`
  - [ ] `postgres:16-alpine`
  - [ ] `influxdb:2.7`
  - [ ] `redis:7-alpine`
  - [ ] `eclipse-mosquitto:2`
  - [ ] `grafana/grafana:latest`
  - [ ] `prom/prometheus:latest`
  - [ ] `grafana/loki:latest`
  - [ ] `grafana/promtail:latest`
- [ ] `docker-compose.prod.yml` listo para usar en `/opt/echosmart/`
- [ ] Volúmenes pre-creados con permisos correctos
- [ ] Red Docker `echosmart-prod` pre-creada

### 8.4 Script de Configuración Inicial — `echosmart-server-setup`

- [ ] Crear script interactivo `echosmart-server-setup` (wizard de configuración):
  - [ ] **Paso 1: Dominio** — Preguntar dominio principal (ej: `echosmart.miempresa.com`)
  - [ ] **Paso 2: Email admin** — Email del administrador (para SSL y cuenta admin)
  - [ ] **Paso 3: Contraseña admin** — Contraseña del usuario administrador (validar fortaleza)
  - [ ] **Paso 4: SMTP** — Configurar servidor de correo:
    - [ ] Host SMTP (ej: `smtp.gmail.com`)
    - [ ] Puerto (587 TLS / 465 SSL)
    - [ ] Usuario SMTP
    - [ ] Contraseña SMTP
    - [ ] Email "From" (ej: `noreply@echosmart.io`)
  - [ ] **Paso 5: Red** — Configurar IP estática o DHCP
  - [ ] **Paso 6: Timezone** — Seleccionar zona horaria
- [ ] Generar todas las credenciales automáticamente:
  - [ ] Contraseña PostgreSQL (32 chars random)
  - [ ] Contraseña InfluxDB (32 chars random)
  - [ ] Contraseña Redis (32 chars random)
  - [ ] JWT Secret Key (64 chars random)
  - [ ] MQTT password (32 chars random)
  - [ ] API keys iniciales
  - [ ] Grafana admin password
- [ ] Guardar credenciales en `/opt/echosmart/credentials.env` (permisos 600, solo root)
- [ ] Configurar Nginx con el dominio proporcionado
- [ ] Solicitar certificado SSL con Let's Encrypt (o self-signed si no hay dominio público)
- [ ] Configurar DNS registros (mostrar instrucciones al admin)
- [ ] Configurar SMTP en el backend
- [ ] Crear usuario administrador en la base de datos
- [ ] Crear tenant predeterminado
- [ ] Iniciar todos los servicios Docker
- [ ] Verificar que todos los servicios están healthy
- [ ] Enviar email de prueba al admin
- [ ] Imprimir resumen de la instalación con URLs

### 8.5 Gestión del Servidor — Scripts de Administración

- [ ] `echosmart-ctl status` — Estado de todos los servicios
- [ ] `echosmart-ctl start` — Iniciar todos los servicios
- [ ] `echosmart-ctl stop` — Detener todos los servicios
- [ ] `echosmart-ctl restart` — Reiniciar todos los servicios
- [ ] `echosmart-ctl logs [servicio]` — Ver logs (todos o uno específico)
- [ ] `echosmart-ctl backup` — Ejecutar backup manual
- [ ] `echosmart-ctl restore [archivo]` — Restaurar desde backup
- [ ] `echosmart-ctl update` — Actualizar a la última versión (pull images + restart)
- [ ] `echosmart-ctl reset-password [email]` — Resetear contraseña de usuario
- [ ] `echosmart-ctl add-user [email] [role]` — Crear usuario
- [ ] `echosmart-ctl ssl-renew` — Renovar certificado SSL
- [ ] `echosmart-ctl health` — Verificación completa de salud del sistema
- [ ] `echosmart-ctl config` — Re-ejecutar wizard de configuración
- [ ] `echosmart-ctl diagnostics` — Generar reporte de diagnóstico (para soporte)
- [ ] Instalar como servicio systemd: `echosmart.service`
- [ ] Auto-inicio al boot del servidor

### 8.6 Generación del ISO — Build System

- [ ] Crear `infra/iso/server/` — Directorio de build del ISO
- [ ] Script de build: `infra/iso/server/build-iso.sh`
- [ ] Usar `cubic` o `live-build` para personalizar Ubuntu ISO
- [ ] Preseed file (`preseed.cfg`) para instalación desatendida:
  - [ ] Idioma: español (configurable)
  - [ ] Teclado: latam/español
  - [ ] Particionamiento automático
  - [ ] Usuario del sistema: `echosmart`
  - [ ] Instalar OpenSSH server
  - [ ] Post-install: ejecutar script de provisioning
- [ ] Script de provisioning que se ejecuta en primer boot:
  - [ ] Instalar Docker, Docker Compose
  - [ ] Copiar archivos de EchoSmart a `/opt/echosmart/`
  - [ ] Cargar imágenes Docker pre-descargadas (`docker load`)
  - [ ] Instalar `echosmart-ctl` en `/usr/local/bin/`
  - [ ] Configurar cron jobs
  - [ ] Configurar firewall (UFW)
  - [ ] Configurar fail2ban
  - [ ] Configurar logrotate
  - [ ] Mostrar wizard de configuración en primer login
- [ ] Validación del ISO:
  - [ ] Test en VirtualBox: instalación completa en < 15 minutos
  - [ ] Test en VMware: instalación completa
  - [ ] Test en hardware físico (servidor real)
  - [ ] Verificar que todos los servicios inician correctamente
  - [ ] Verificar acceso web al dashboard
  - [ ] Verificar recepción de datos del emulador
- [ ] Documentar el proceso de build del ISO
- [ ] CI/CD: GitHub Action para build automático del ISO en cada release

### 8.7 Actualización Remota del Servidor

- [ ] Mecanismo de actualización Over-The-Air (OTA):
  - [ ] `echosmart-ctl update` descarga nuevas imágenes Docker
  - [ ] Verificar compatibilidad de versiones antes de actualizar
  - [ ] Ejecutar migraciones de base de datos automáticamente
  - [ ] Rollback automático si health check falla post-update
  - [ ] Notificar al admin por email del resultado de la actualización
- [ ] Versionado semántico del servidor (major.minor.patch)
- [ ] Changelog automático entre versiones
- [ ] Política de soporte: LTS para versiones major

---

## Fase 9: ISO Personalizado del Raspberry Pi Gateway (Semanas 26–28)

> 💿 **El ISO del Raspberry Pi contiene el gateway pre-configurado.** El usuario final solo necesita flashear la microSD, conectar los sensores, encender el RPi, y el gateway se conecta automáticamente al servidor.

### 9.1 Definición del ISO del Gateway

- [ ] Base: Raspberry Pi OS Lite 64-bit (Bookworm, sin desktop)
- [ ] Nombre del ISO: `echosmart-gateway-v{VERSION}-arm64.img`
- [ ] Tamaño objetivo: < 2GB (comprimido .xz < 500MB)
- [ ] Arquitectura: arm64 (aarch64) para RPi 3B+/4/5
- [ ] Boot: automático, sin intervención del usuario
- [ ] Filesystem: ext4, auto-expand en primer boot

### 9.2 Software Pre-instalado en el Gateway

- [ ] **Raspberry Pi OS Lite** con actualizaciones de seguridad
- [ ] **Paquete .deb `echosmart-gateway`** pre-instalado con:
  - [ ] `/usr/bin/echosmart` — binario unificado del gateway
  - [ ] `/usr/bin/echosmart (binario)` — binario C++ del daemon
  - [ ] `/usr/bin/echosmart sysinfo` — diagnósticos del sistema (C++)
  - [ ] `/usr/bin/echosmart read` — lectura de sensores (C++)
  - [ ] `/usr/bin/echosmart setup` — wizard de configuración
  - [ ] `/etc/echosmart/gateway.env` — configuración por defecto
  - [ ] `/etc/echosmart/sensors.json` — definición de sensores
  - [ ] `/lib/systemd/system/echosmart-gateway.service` — unidad systemd
- [ ] **SQLite3** para almacenamiento local
- [ ] **Mosquitto client** para MQTT
- [ ] **Interfaces habilitadas**: I2C, 1-Wire, UART, SPI
- [ ] **Device tree overlays** configurados:
  - [ ] `dtoverlay=w1-gpio,gpiopin=4` (DS18B20)
  - [ ] `enable_uart=1` (MH-Z19C)
  - [ ] `dtparam=i2c_arm=on` (BH1750, ADS1115)
  - [ ] `dtoverlay=disable-bt` (liberar UART principal)
  - [ ] `gpu_mem=16` (mínima GPU, es headless)
- [ ] **Watchdog de hardware** habilitado (reinicio automático si se congela)
- [ ] **Servicios systemd**:
  - [ ] `echosmart-gateway.service` — Servicio principal del gateway
  - [ ] `echosmart-watchdog.service` — Monitor de salud
  - [ ] `echosmart-updater.timer` — Actualización automática diaria

### 9.3 Script de Configuración del Gateway — `echosmart setup`

- [ ] Crear script de configuración de primer boot:
  - [ ] **Paso 1: Nombre del gateway** — Identificador único (ej: `invernadero-norte-01`)
  - [ ] **Paso 2: URL del servidor** — Dirección del servidor EchoSmart (ej: `https://api.echosmart.io`)
  - [ ] **Paso 3: API Key** — Clave de autenticación del gateway (generada en el servidor)
  - [ ] **Paso 4: WiFi** (opcional) — SSID y contraseña de la red WiFi
  - [ ] **Paso 5: IP** — DHCP (default) o IP estática
- [ ] Auto-registro del gateway en el servidor:
  - [ ] POST `/api/v1/gateways/register` con API key
  - [ ] Recibir y guardar `gateway_id` y `mqtt_credentials`
  - [ ] Configurar conexión MQTT con credenciales recibidas
- [ ] Verificar conectividad con el servidor
- [ ] Verificar que los sensores son detectados (I2C, 1-Wire, UART)
- [ ] Iniciar servicio del gateway
- [ ] LED indicator (si RPi tiene LED): parpadeo lento = conectando, fijo = conectado

### 9.4 Auto-Conexión al Servidor

- [ ] Implementar auto-discovery del servidor en red local (mDNS/Bonjour)
- [ ] Fallback: el gateway busca `echosmart-server.local` en la red
- [ ] Si no encuentra, usar la URL configurada manualmente
- [ ] Reconexión automática si pierde conexión al servidor:
  - [ ] Retry con backoff exponencial (1s, 2s, 4s, 8s... max 5min)
  - [ ] Almacenar lecturas en SQLite local durante desconexión
  - [ ] Sincronizar datos acumulados al reconectar (batch upload)
  - [ ] Notificar al servidor que hubo desconexión (con timestamps)
- [ ] Heartbeat: ping al servidor cada 30 segundos
- [ ] Si el servidor cambia de IP (DNS dinámico), actualizar automáticamente

### 9.5 Gestión Remota del Gateway

- [ ] Actualización OTA del software del gateway:
  - [ ] El servidor envía comando MQTT `echosmart/gw/{id}/update`
  - [ ] El gateway descarga nueva versión desde servidor o GitHub
  - [ ] Aplica actualización y reinicia servicio
  - [ ] Reporta versión nueva al servidor
  - [ ] Rollback si la nueva versión falla
- [ ] Reinicio remoto:
  - [ ] Comando MQTT `echosmart/gw/{id}/reboot`
  - [ ] El gateway hace reboot limpio (flush datos, stop service, reboot)
- [ ] Configuración remota:
  - [ ] Cambiar intervalo de polling vía MQTT
  - [ ] Habilitar/deshabilitar sensores específicos
  - [ ] Cambiar nivel de logging
- [ ] Diagnóstico remoto:
  - [ ] Comando MQTT `echosmart/gw/{id}/diagnostics`
  - [ ] El gateway responde con: CPU, RAM, disk, uptime, sensor status, network, versión
- [ ] SSH tunneling inverso (opcional, para soporte remoto)

### 9.6 Generación del ISO del Gateway — Build System

- [ ] Crear `infra/iso/gateway/` — Directorio de build
- [ ] Script de build: `infra/iso/gateway/build-gateway-image.sh`
- [ ] Usar `pi-gen` (herramienta oficial de RPi Foundation) para customizar imagen
- [ ] Customizaciones de pi-gen:
  - [ ] Stage 0: Bootstrap Debian
  - [ ] Stage 1: Mínimo OS (sin desktop)
  - [ ] Stage 2: Sistema base con networking
  - [ ] Stage 3: Paquete .deb EchoSmart (binarios C++, systemd, config)
  - [ ] Stage 4: Configuración final (services, config, first-boot script)
- [ ] First-boot script (`/opt/echosmart/first-boot.sh`):
  - [ ] Expandir filesystem a toda la SD
  - [ ] Generar hostname único basado en MAC address
  - [ ] Generar SSH host keys únicos
  - [ ] Verificar y habilitar interfaces de hardware
  - [ ] Iniciar wizard de configuración (en consola serial o SSH)
  - [ ] Iniciar servicio del gateway
  - [ ] Marcar first-boot como completado
- [ ] Comprimir imagen con `xz` para distribución
- [ ] Checksum SHA256 para verificación de integridad
- [ ] Validación:
  - [ ] Test en RPi 4 (hardware real)
  - [ ] Test en QEMU (emulación ARM)
  - [ ] Verificar boot < 30 segundos
  - [ ] Verificar que los sensores son detectados
  - [ ] Verificar conexión automática al servidor
  - [ ] Verificar transmisión de datos de sensores
- [ ] CI/CD: GitHub Action para build automático de la imagen

### 9.7 Documentación del Usuario Final

- [ ] Guía rápida (1 página) incluida en caja del producto:
  - [ ] Paso 1: Flashear la microSD con Balena Etcher
  - [ ] Paso 2: Insertar SD en Raspberry Pi
  - [ ] Paso 3: Conectar sensores según diagrama incluido
  - [ ] Paso 4: Conectar alimentación y cable de red
  - [ ] Paso 5: Acceder a `http://echosmart-gw-XXXX.local` para configurar
- [ ] Diagrama de conexión de sensores (impreso, a color)
- [ ] FAQ de problemas comunes
- [ ] QR code que lleva a documentación online

---

## Fase 10: Features Avanzadas (Semanas 29+)

### 10.1 Control de Actuadores

- [ ] Modelo de datos: `Actuator(id, name, type, gpio_pin, state, gateway_id)`
- [ ] Driver de relés en gateway: `RelayDriver` (On/Off via GPIO)
- [ ] Protección contra switching rápido (debounce)
- [ ] Programación horaria tipo CRON
- [ ] Automatización por reglas:
  - [ ] `IF temp > 35°C AND duration > 5min THEN ventilación ON`
  - [ ] `IF soil_moisture < 40% THEN riego ON por 10 min`
  - [ ] `IF light < 5000 lux THEN iluminación ON`
- [ ] API REST para control remoto
- [ ] UI en frontend para gestión de actuadores
- [ ] UI en mobile para control rápido
- [ ] Tests: drivers, scheduling, automatización, UI

### 10.2 Analítica Predictiva (ML)

- [ ] Dataset de entrenamiento (30+ días de datos reales)
- [ ] Predicción de temperatura (LSTM/Prophet, horizontes: 1h/6h/24h)
- [ ] Predicción de humedad del suelo (para optimizar riego)
- [ ] Detección de anomalías (Isolation Forest / Autoencoders)
- [ ] Recomendaciones automáticas de riego basadas en predicción
- [ ] API de predicciones: `GET /api/v1/predictions/{sensor_id}`
- [ ] Visualización en dashboard: gráfica con predicción + intervalo de confianza
- [ ] Re-entrenamiento periódico del modelo (cada semana)
- [ ] Tests con datos históricos (backtesting)

### 10.3 Integraciones Externas

- [ ] **WhatsApp Business API** para alertas críticas
- [ ] **Telegram Bot** (`@EchoSmartBot`):
  - [ ] Comandos: `/status`, `/sensors`, `/alerts`, `/photo`
  - [ ] Notificaciones push de alertas
- [ ] **Slack / Microsoft Teams** webhooks para alertas
- [ ] **API Meteorológica** (OpenWeatherMap):
  - [ ] Pronóstico 5 días para ubicación del invernadero
  - [ ] Correlación automática: clima externo vs lecturas internas
  - [ ] Alerta proactiva: "Helada prevista en 6 horas"
- [ ] **Google Sheets** export de datos
- [ ] Tests con APIs mockeadas (responses/httpretty)

### 10.4 Administración Avanzada

- [ ] **Audit Log** completo:
  - [ ] Registrar TODA acción: login, CRUD, config changes
  - [ ] Campos: user_id, action, resource, old_value, new_value, ip, timestamp
  - [ ] UI para buscar y filtrar audit trail
  - [ ] Retención configurable (90 días default)
- [ ] **SSO** (Single Sign-On):
  - [ ] Google OAuth2
  - [ ] Microsoft Azure AD
  - [ ] SAML 2.0 para enterprise
- [ ] **2FA** (Two-Factor Authentication):
  - [ ] TOTP con Google Authenticator / Authy
  - [ ] Backup codes (10 códigos de un solo uso)
  - [ ] Forzar 2FA para admins
- [ ] **Suscripciones y Billing**:
  - [ ] Planes: Free (1 gateway, 5 sensors) / Pro (10 gw, 50 sensors) / Enterprise (ilimitado)
  - [ ] Stripe integration para pagos
  - [ ] UI de billing, facturas, upgrade/downgrade
- [ ] Tests: audit trail, SSO flow, 2FA setup, billing

### 10.5 API Pública y Documentación para Desarrolladores

- [ ] API keys con scopes granulares (read:sensors, write:config, admin)
- [ ] Rate limiting por API key (100 req/min free, 1000 pro, ilimitado enterprise)
- [ ] Portal de desarrolladores (`developers.echosmart.io`)
- [ ] Documentación OpenAPI 3.1 interactiva (Swagger UI + ReDoc)
- [ ] SDKs oficiales: Python, JavaScript, cURL examples
- [ ] Webhooks salientes configurables (sensor reading, alert, gateway status)
- [ ] Sandbox environment para testing de integraciones
- [ ] Tests: API keys, rate limiting, webhooks delivery

### 10.6 Internacionalización y Accesibilidad

- [ ] Traducciones completas: español, inglés, portugués, francés
- [ ] Sistema de traducciones: react-i18next (frontend) + gettext (backend)
- [ ] WCAG 2.1 AA en frontend web
- [ ] VoiceOver (iOS) / TalkBack (Android) en mobile
- [ ] Modo alto contraste
- [ ] Keyboard navigation completa (no mouse-only interactions)
- [ ] Tests de accesibilidad automatizados (axe-core, Lighthouse)

---

## Fase 11: Testing con Hardware Real (Final)

> 🔧 **Esta fase se ejecuta ÚNICAMENTE cuando todo el software está completo, probado en modo simulación, y la infraestructura está desplegada.** Aquí se adquiere el hardware físico y se validan los drivers contra sensores reales.

### 11.1 Adquisición de Hardware
- [ ] Adquirir Raspberry Pi 4 Model B (4GB+ RAM)
- [ ] Adquirir fuente de alimentación oficial RPi (5V 3A USB-C)
- [ ] Adquirir tarjeta microSD (32GB+ clase 10)
- [ ] Adquirir sensor DS18B20 (versión encapsulada impermeable)
- [ ] Adquirir sensor DHT22 / AM2302
- [ ] Adquirir sensor BH1750FVI (módulo breakout)
- [ ] Adquirir sensor capacitivo de humedad de suelo v1.2
- [ ] Adquirir módulo ADC ADS1115 (16-bit, 4 canales)
- [ ] Adquirir sensor MH-Z19C (CO₂ NDIR)
- [ ] Adquirir protoboard, cables jumper, resistencias pull-up (4.7kΩ para 1-Wire, 10kΩ para DHT22)
- [ ] Adquirir carcasa/case para RPi con ventilación
- [ ] Verificar que todos los componentes sean compatibles con RPi 3.3V/5V

### 11.2 Flashear ISO del Gateway
- [ ] Descargar `echosmart-gateway-v{VERSION}-arm64.img`
- [ ] Flashear con Balena Etcher o RPi Imager
- [ ] Insertar microSD en Raspberry Pi
- [ ] Conectar alimentación y red
- [ ] Ejecutar wizard de configuración (`echosmart setup`)
- [ ] Verificar que el gateway aparece en el dashboard del servidor

### 11.3 Conexión Física de Sensores
- [ ] Conectar DS18B20 a GPIO 4 con resistencia pull-up de 4.7kΩ entre DATA y VCC (3.3V)
- [ ] Conectar DHT22 a GPIO 17 con resistencia pull-up de 10kΩ (si el módulo no la incluye)
- [ ] Conectar BH1750 a bus I2C (SDA → GPIO 2, SCL → GPIO 3), alimentar a 3.3V
- [ ] Conectar ADS1115 a bus I2C (SDA → GPIO 2, SCL → GPIO 3), dirección 0x48
- [ ] Conectar sensor de humedad de suelo al canal A0 del ADS1115
- [ ] Conectar MH-Z19C a UART (TX sensor → RX RPi GPIO 15, RX sensor → TX RPi GPIO 14), alimentar a 5V
- [ ] Verificar pinout con diagrama incluido antes de encender

### 11.4 Validación de Drivers con Hardware Real
- [ ] Cambiar configuración del gateway a `simulation=False`
- [ ] Verificar cada sensor individualmente desde la CLI del gateway
- [ ] Verificar que las lecturas aparecen en el dashboard web
- [ ] Verificar que las alertas se generan correctamente
- [ ] Comparar lecturas contra instrumentos de referencia (termómetro, higrómetro)

### 11.5 Calibración y Ajustes
- [ ] Calibrar DS18B20: verificar offset vs termómetro de referencia
- [ ] Calibrar DHT22: verificar humedad vs higrómetro de referencia
- [ ] Calibrar BH1750: verificar lux vs luxómetro
- [ ] Calibrar sensor de suelo: definir curva seco (0%) vs saturado (100%)
- [ ] Calibrar MH-Z19C: autocalibración ABC o manual a 400ppm (aire exterior)
- [ ] Ajustar intervalos de polling según estabilidad de lecturas
- [ ] Documentar offsets y factores de corrección

### 11.6 Testing de Integración End-to-End
- [ ] Ejecutar gateway con los 5 sensores reales conectados
- [ ] Verificar datos en tiempo real en dashboard web
- [ ] Verificar datos en app mobile
- [ ] Verificar datos en app desktop
- [ ] Verificar alertas por email (SMTP)
- [ ] Verificar reconexión después de corte de red
- [ ] Verificar reconexión después de reinicio del RPi
- [ ] Verificar sincronización de datos offline
- [ ] Medir consumo de CPU/RAM del Raspberry Pi bajo carga
- [ ] Prueba de estrés: **24 horas continuas** de operación con todos los sensores
- [ ] Prueba de estrés: **72 horas** con cortes de red simulados cada 4 horas

---

## Fase 12: Producción y Comercialización del Kit

> 🏭 **El kit EchoSmart se comercializa como producto llave en mano.** Esta fase cubre
> la producción en masa, control de calidad, empaque y canales de venta.

### 12.1 BOM (Bill of Materials) por Kit

- [ ] Definir BOM final con proveedores y costos unitarios:
  - [ ] Raspberry Pi 4B 4 GB (~$55)
  - [ ] Fuente USB-C 5V 3A (~$8)
  - [ ] microSD 32 GB con imagen pre-grabada (~$7)
  - [ ] DS18B20 encapsulado impermeable (~$2)
  - [ ] DHT22 módulo (~$3)
  - [ ] BH1750 breakout (~$2)
  - [ ] Sensor suelo capacitivo v1.2 (~$2)
  - [ ] ADS1115 módulo ADC (~$3)
  - [ ] MH-Z19C CO₂ NDIR (~$18)
  - [ ] Carcasa Raspberry Pi (~$5)
  - [ ] Protoboard + cables + resistencias 4.7kΩ/10kΩ (~$5)
  - [ ] Caja del kit + manual impreso + sticker GPIO (~$8)
  - [ ] **COGS total estimado: ~$118 USD**
- [ ] Negociar precios por volumen con proveedores (lotes de 100+)
- [ ] Establecer proveedor de respaldo para cada componente crítico

### 12.2 Precios de Venta y Planes

- [ ] Definir estructura de precios:
  - [ ] **Kit Básico** ($299) — Hardware + microSD + manual impreso
  - [ ] **Kit Pro** ($449) — Kit Básico + 1 año soporte + dashboard cloud
  - [ ] **Enterprise** (cotización) — 10× Kit Pro + instalación + SLA 24/7
- [ ] Crear landing page `echosmart.io` con planes y checkout
- [ ] Integrar Stripe para pagos online
- [ ] Crear programa de distribuidores / revendedores

### 12.3 Proceso de Ensamblaje (Producción en Masa)

- [ ] Definir línea de ensamblaje (objetivo: 10 unidades/hora)
- [ ] Crear checklist de ensamblaje por unidad:
  - [ ] Flashear microSD con imagen ISO (batch de 50)
  - [ ] Insertar Raspberry Pi en carcasa
  - [ ] Empaquetar sensores en bolsa antiestática
  - [ ] Incluir protoboard, cables, resistencias
  - [ ] Incluir manual impreso y sticker GPIO
  - [ ] Etiquetar con número de serie (formato: `ES-YYYYMM-XXXX`)
  - [ ] Colocar todo en caja del kit
  - [ ] Sellar caja
- [ ] Crear estación de flasheo de microSD (duplicador para lotes grandes)

### 12.4 Control de Calidad (QA) por Unidad

- [ ] Crear procedimiento de QA por unidad antes de empaquetar:
  - [ ] Encender Raspberry Pi → boot completo < 60 s
  - [ ] Ejecutar `echosmart sysinfo` → JSON válido con modelo y versión
  - [ ] Ejecutar `echosmart read ds18b20 --simulate=true` → JSON válido
  - [ ] Ejecutar `echosmart run --simulate=true --once=true` → ciclo completo OK
  - [ ] Verificar `systemctl status echosmart-gateway` → loaded
  - [ ] Verificar wizard `echosmart setup` → escribe config
- [ ] Criterios de PASS/FAIL documentados
- [ ] Registro de resultados QA por número de serie
- [ ] Tasa de rechazo objetivo: < 2%

### 12.5 Makefile de Producción

- [ ] Crear `Makefile` en raíz del repositorio con targets:
  - [ ] `help` — lista de targets disponibles
  - [ ] `build` — compilar binarios C++ (host)
  - [ ] `build-arm64` — cross-compilar para arm64
  - [ ] `deb` — construir paquete .deb
  - [ ] `test` — ejecutar binarios con --simulate y verificar salida
  - [ ] `lint` — cppcheck / clang-tidy sobre gateway/cpp/
  - [ ] `clean` — limpiar artefactos de compilación
  - [ ] `install` — instalar binarios localmente
  - [ ] `docker-up` / `docker-down` — infraestructura local

### 12.6 CI/CD para .deb (GitHub Actions)

- [ ] Crear `.github/workflows/build-deb.yml`:
  - [ ] Trigger: tags `v*` (e.g. `v1.0.0`)
  - [ ] Instalar `gcc-aarch64-linux-gnu` y `g++-aarch64-linux-gnu`
  - [ ] Cross-compilar binarios C++ para arm64
  - [ ] Construir .deb con `dpkg-buildpackage`
  - [ ] Ejecutar tests con `--simulate` en host
  - [ ] Subir .deb como artefacto a GitHub Releases
  - [ ] Generar checksum SHA256
- [ ] Actualizar `ci.yml` para incluir compilación y tests de binarios C++

### 12.7 Documentación de Producción

- [ ] Crear `docs/production-kit.md` — BOM, precios, ensamblaje, QA
- [ ] Crear `docs/deb-packaging.md` — cómo construir, instalar y actualizar .deb
- [ ] Actualizar `docs/gateway-edge-computing.md` — binarios C++, systemd, sin Python
- [ ] Actualizar `docs/project-structure.md` — nueva estructura gateway/cpp/
- [ ] Actualizar `docs/getting-started.md` — instrucciones con binarios C++
- [ ] Actualizar `docs/README.md` — índice con nuevos documentos
- [ ] Manual de inicio rápido impreso (4 páginas, incluido en caja)
- [ ] Guía de conexión de sensores con diagramas GPIO
- [ ] Sticker con pinout GPIO para pegar en la carcasa

### 12.8 Portal SaaS (Dashboard Cloud)

- [ ] Landing page: `echosmart.io`
- [ ] Registro de kits por número de serie
- [ ] Dashboard cloud por suscripción (Kit Pro y Enterprise)
- [ ] API de provisioning para gateways nuevos
- [ ] Stripe para pagos recurrentes
- [ ] Documentación para el usuario final

### 12.9 Logística y Envío

- [ ] Definir métodos de envío por zona:
  - [ ] Nacional (México): Fedex/Estafeta, 3-5 días, ~$10-15
  - [ ] EE.UU./Canadá: DHL Express, 5-7 días, ~$25-35
  - [ ] Internacional: DHL/UPS, 7-14 días, ~$35-50
- [ ] Definir política de garantía:
  - [ ] Hardware: 1 año contra defectos de fabricación
  - [ ] Software: actualizaciones de seguridad vía `apt upgrade`
  - [ ] Soporte: email + chat (Kit Pro y Enterprise)

### 12.10 Actualización de Software en Campo

- [ ] Documentar proceso de actualización para el cliente:
  - [ ] `sudo dpkg -i echosmart-gateway_X.Y.Z-1_arm64.deb`
  - [ ] O via repositorio APT: `sudo apt update && sudo apt upgrade echosmart-gateway`
- [ ] Implementar notificación al dashboard cuando hay nueva versión disponible
- [ ] Implementar OTA (Over-The-Air) update via MQTT comando remoto

---

## Resumen de Plataformas

| Plataforma | Tecnología | Directorio | Estado |
|------------|-----------|------------|--------|
| **Backend (Cloud)** | FastAPI · PostgreSQL · InfluxDB · Redis | `backend/` | 🟡 Scaffolding completo |
| **Frontend (Web)** | React 18 · Vite · Redux Toolkit · Recharts | `frontend/` | 🟡 Scaffolding completo |
| **Gateway (Edge)** | C++17 · CMake · .deb · systemd · Raspberry Pi | `gateway/` | 🟡 Binarios C++ completos |
| **Móvil (Android)** | React Native · Expo | `mobile/` | 🟠 Estructura inicial |
| **Móvil (iOS)** | React Native · Expo | `mobile/` | 🟠 Estructura inicial |
| **Escritorio (Windows)** | Electron · React | `desktop/` | 🟠 Estructura inicial |
| **Escritorio (macOS)** | Electron · React | `desktop/` | 🟠 Estructura inicial |
| **Escritorio (Linux)** | Electron · React | `desktop/` | 🟠 Estructura inicial |
| **Infra Local (Dev)** | Docker Compose · Makefile · Scripts | `infra/` | 🟠 Pendiente |
| **Infra Producción** | Docker · K8s · Nginx · Prometheus · Grafana | `infra/` | 🟡 Docker + K8s parcial |
| **ISO Servidor** | Ubuntu 22.04 · Docker · echosmart-ctl | `infra/iso/server/` | 🟠 Pendiente |
| **ISO Gateway RPi** | RPi OS Lite · .deb (C++) · pi-gen | `infra/iso/gateway/` | 🟠 Pendiente |
| **Assets / Diseño** | SVG · PNG · JPG · ICO | `assets/` | 🟢 312 archivos generados |
| **Documentación** | Markdown · SVG | `docs/` | 🟢 26+ documentos |

## Resumen de Fases

| Fase | Nombre | Semanas | Tareas | Estado |
|------|--------|---------|--------|--------|
| 0 | Estructura y Assets | — | ~130 | ✅ Completado |
| 1 | Gateway C++ (Binarios + .deb) | 1–3 | ~180 | 🟡 Binarios completos |
| 2 | Backend Cloud | 4–7 | ~300 | 🟡 Scaffolding |
| 3 | Frontend Web | 8–10 | ~250 | 🟡 Scaffolding |
| 4 | Mobile (Android + iOS) | 11–16 | ~120 | 🟠 Estructura |
| 5 | Desktop (Win/Mac/Linux) | 17–20 | ~70 | 🟠 Estructura |
| 6 | **Infra Local + Emulador** | 17–18 | ~100 | 🟠 Pendiente |
| 7 | **Infra Producción + DevOps** | 19–22 | ~150 | 🟠 Pendiente |
| 8 | **ISO Servidor** | 23–25 | ~120 | 🟠 Pendiente |
| 9 | **ISO Raspberry Pi Gateway** | 26–28 | ~100 | 🟠 Pendiente |
| 10 | Features Avanzadas | 29+ | ~80 | 🟠 Pendiente |
| 11 | Testing con Hardware Real | Final | ~40 | 🟠 Pendiente |
| 12 | **Producción y Comercialización** | Final | ~80 | 🟠 Pendiente |
| | **TOTAL** | | **~1720+** | |

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

*Última actualización: 29 de marzo de 2026*
