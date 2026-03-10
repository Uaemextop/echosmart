# EchoSmart — Directivas del Proyecto

Este documento define las directivas de gobernanza, calidad, desarrollo y operación que rigen el proyecto EchoSmart como plataforma IoT para invernaderos inteligentes.

---

## Índice

1. [Directiva de Visión y Alcance](#1-directiva-de-visión-y-alcance)
2. [Directiva de Arquitectura](#2-directiva-de-arquitectura)
3. [Directiva de Desarrollo](#3-directiva-de-desarrollo)
4. [Directiva de Seguridad](#4-directiva-de-seguridad)
5. [Directiva de Calidad](#5-directiva-de-calidad)
6. [Directiva de Datos](#6-directiva-de-datos)
7. [Directiva de Operación](#7-directiva-de-operación)
8. [Directiva de Hardware](#8-directiva-de-hardware)
9. [Directiva de Documentación](#9-directiva-de-documentación)
10. [Directiva de Sostenibilidad](#10-directiva-de-sostenibilidad)

---

## 1. Directiva de Visión y Alcance

### DIR-001: Propósito del Sistema

> EchoSmart es una plataforma IoT diseñada exclusivamente para el **monitoreo ambiental inteligente de invernaderos**, con el objetivo de optimizar las condiciones de cultivo, reducir pérdidas y aumentar la productividad agrícola mediante tecnología accesible.

### DIR-002: Alcance Funcional

El sistema **DEBE** incluir las siguientes capacidades:

| Capacidad | Prioridad | Estado |
|-----------|-----------|--------|
| Monitoreo de 5 variables ambientales | Alta | ✅ |
| Alertas configurables por sensor | Alta | ✅ |
| Dashboard web en tiempo real | Alta | ✅ |
| Generación de reportes PDF/Excel | Media | ✅ |
| Control de actuadores (riego, ventilación, iluminación) | Media | 🔶 Roadmap |
| App móvil (iOS/Android) | Media | 🔶 Roadmap |
| Analítica predictiva con ML | Baja | 🔶 Roadmap |
| Multi-tenancy | Media | ✅ |

### DIR-003: Usuarios Objetivo

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Agrónomo** | Monitorea condiciones y toma decisiones de cultivo | Lectura + alertas |
| **Operador** | Gestiona sensores y responde a alertas | Lectura + escritura operativa |
| **Administrador** | Configura el sistema, usuarios y reglas | Acceso completo del tenant |
| **Investigador** | Analiza datos históricos y tendencias | Lectura + reportes + exportación |

---

## 2. Directiva de Arquitectura

### DIR-010: Arquitectura de 3 Capas

El sistema **DEBE** implementar la arquitectura edge-to-cloud de 3 capas:

```
Sensores → Gateway (Edge) → Backend (Cloud) → Frontend (Cliente)
```

- **Edge (Gateway):** Opera de forma autónoma; no depende de conectividad para funciones críticas.
- **Cloud (Backend):** Procesa, almacena y distribuye datos; orquesta alertas y reportes.
- **Cliente (Frontend):** Presenta datos en tiempo real; permite gestión y configuración.

### DIR-011: Independencia de Capas

Cada capa **DEBE** poder desarrollarse, desplegarse y escalarse de forma independiente. La comunicación entre capas se realiza exclusivamente mediante APIs REST, MQTT y WebSocket.

### DIR-012: Resiliencia Offline

El gateway **DEBE** operar de forma autónoma ante la pérdida de conectividad con la nube:
- Almacenar lecturas localmente en SQLite.
- Evaluar reglas de alerta localmente.
- Sincronizar datos automáticamente al recuperar conexión.
- Máximo 72 horas de operación offline sin pérdida de datos.

### DIR-013: Escalabilidad

- El backend **DEBE** soportar escalamiento horizontal (múltiples réplicas).
- El sistema **DEBE** soportar al menos 50 gateways y 250 sensores concurrentes.
- La latencia p99 del API **DEBE** ser inferior a 200 ms.

---

## 3. Directiva de Desarrollo

### DIR-020: Stack Tecnológico

| Capa | Tecnología Obligatoria |
|------|----------------------|
| Gateway | Python 3.9+ · SQLite 3 · Mosquitto MQTT |
| Backend | FastAPI · PostgreSQL 14+ · InfluxDB 2.7+ · Redis 7+ |
| Frontend Web | React 18+ · Redux Toolkit · Recharts |
| Frontend Móvil | React Native (Expo) |
| Infraestructura | Docker · Docker Compose · GitHub Actions |

### DIR-021: Convenciones de Código

- **Python:** PEP 8, type hints obligatorios, docstrings en funciones públicas.
- **JavaScript/TypeScript:** ESLint + Prettier, TypeScript preferido sobre JavaScript.
- **Git:** Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
- **Ramas:** `main` (producción), `develop` (integración), `feature/*`, `fix/*`, `release/*`.

### DIR-022: Testing

| Tipo | Cobertura Mínima | Herramienta |
|------|-----------------|-------------|
| Unitarios | 80% | pytest (Python), Jest (JS) |
| Integración | 60% | pytest + httpx, Supertest |
| E2E | Flujos críticos | Cypress / Playwright |
| Hardware | Mock de sensores | pytest-mock |

### DIR-023: CI/CD Pipeline

Todo código **DEBE** pasar por el pipeline antes de ser integrado a `main`:

1. **Lint:** Formateo y análisis estático.
2. **Test:** Ejecución de tests unitarios e integración.
3. **Build:** Construcción de artefactos (Docker images).
4. **Security:** Escaneo de dependencias (Dependabot, CodeQL).
5. **Deploy:** Despliegue automático a staging; manual a producción.

---

## 4. Directiva de Seguridad

### DIR-030: Autenticación y Autorización

- **OBLIGATORIO:** JWT (JSON Web Tokens) para todas las APIs.
- **OBLIGATORIO:** RBAC con 4 roles (Superadmin, Admin, Operador, Viewer).
- **OBLIGATORIO:** Contraseñas hasheadas con bcrypt (factor ≥ 12).
- **OBLIGATORIO:** Refresh tokens en cookies HttpOnly, Secure, SameSite.
- **OBLIGATORIO:** Expiración de access tokens ≤ 15 minutos.

### DIR-031: Comunicaciones

- **OBLIGATORIO:** HTTPS (TLS 1.2+) para toda comunicación externa.
- **OBLIGATORIO:** MQTTS (TLS) para comunicación gateway ↔ cloud.
- **OBLIGATORIO:** WSS (WebSocket Secure) para el dashboard.
- **PROHIBIDO:** Transmisión de credenciales en texto plano.

### DIR-032: Datos Sensibles

- **OBLIGATORIO:** Cifrado en reposo para datos de usuarios (AES-256).
- **OBLIGATORIO:** Aislamiento de datos por tenant (row-level security).
- **OBLIGATORIO:** No almacenar datos personales innecesarios.
- **OBLIGATORIO:** Registro de auditoría inmutable para accesos y cambios.

### DIR-033: Actualizaciones

- Las dependencias **DEBEN** actualizarse mensualmente.
- Las vulnerabilidades críticas (CVSS ≥ 9.0) **DEBEN** parchearse en 24 horas.
- Las vulnerabilidades altas (CVSS ≥ 7.0) **DEBEN** parchearse en 7 días.

---

## 5. Directiva de Calidad

### DIR-040: Métricas de Rendimiento

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Latencia API (p99) | < 200 ms | Prometheus |
| Tiempo de lectura de sensor | < 100 ms | Logs del gateway |
| Actualización WebSocket | < 1 s | Medición E2E |
| Renderizado de gráfica | < 500 ms | Lighthouse |
| Disponibilidad (SLA) | 99.9% | Uptime monitor |

### DIR-041: Calidad de Datos

- Todas las lecturas de sensores **DEBEN** incluir un indicador de calidad (0-100).
- Lecturas con calidad < 50 **DEBEN** marcarse como "no confiables".
- Las lecturas fuera de rango físico **DEBEN** descartarse (e.g., temperatura > 150°C).
- El sistema **DEBE** detectar y reportar lecturas repetidas o estancadas.

### DIR-042: UX/UI

- El dashboard **DEBE** ser responsive (mobile-first).
- Score mínimo de Lighthouse: Rendimiento ≥ 90, Accesibilidad ≥ 90.
- Soporte para tema claro y oscuro.
- Internacionalización (español e inglés mínimo).

---

## 6. Directiva de Datos

### DIR-050: Almacenamiento

| Tipo de Dato | Base de Datos | Retención |
|-------------|---------------|-----------|
| Lecturas crudas | InfluxDB | 90 días |
| Agregaciones (1h) | InfluxDB | 1 año |
| Agregaciones (1d) | InfluxDB | 5 años |
| Metadatos (sensores, usuarios) | PostgreSQL | Indefinido |
| Sesiones y caché | Redis | 30 días / 5 min |
| Caché local (edge) | SQLite | 72 horas |

### DIR-051: Backups

- **OBLIGATORIO:** Backup diario de PostgreSQL (retención 30 días).
- **OBLIGATORIO:** Backup semanal completo (retención 90 días).
- **OBLIGATORIO:** Prueba de restauración mensual.
- **RECOMENDADO:** Replicación en tiempo real para alta disponibilidad.

### DIR-052: Privacidad

- Los datos del invernadero pertenecen al tenant/propietario.
- No se comparten datos entre tenants bajo ninguna circunstancia.
- Los datos pueden exportarse en formato CSV, JSON, PDF o Excel.
- Los datos pueden eliminarse a solicitud del propietario (derecho al olvido).

---

## 7. Directiva de Operación

### DIR-060: Monitoreo del Sistema

El sistema **DEBE** monitorear su propia salud:

- Estado de cada gateway (online, offline, maintenance).
- Estado de cada sensor (online, warning, offline, error).
- Uso de recursos del backend (CPU, memoria, disco).
- Latencia de API y tasa de errores.
- Cola de mensajes (RabbitMQ) — profundidad y tasa de procesamiento.

### DIR-061: Alertas Operativas

Además de las alertas de sensores, el sistema **DEBE** generar alertas operativas para:

- Gateway offline por más de 5 minutos.
- Sensor sin lecturas por más de 3× su intervalo de polling.
- Error rate del API > 1%.
- Espacio en disco < 20%.
- Certificados TLS próximos a expirar (30 días).

### DIR-062: Mantenimiento

- **Ventanas de mantenimiento:** Domingos 02:00 – 06:00 (hora local).
- **Notificación previa:** Mínimo 48 horas antes de mantenimiento planificado.
- **Zero-downtime deployments:** Rolling updates en Kubernetes.

---

## 8. Directiva de Hardware

### DIR-070: Gateway

- **Hardware:** Raspberry Pi 4 Model B (4 GB RAM mínimo).
- **Sistema Operativo:** Raspberry Pi OS 64-bit (Lite recomendado).
- **Alimentación:** Fuente de alimentación certificada de 5V/3A con respaldo UPS.
- **Conectividad:** WiFi 2.4/5 GHz o Ethernet. Ethernet preferido para estabilidad.
- **Almacenamiento:** microSD Clase 10 ≥ 32 GB. Se recomienda SSD vía USB para producción.

### DIR-071: Sensores

| Sensor | Requisito | Calibración |
|--------|-----------|-------------|
| DS18B20 | Resistencia pull-up 4.7 kΩ obligatoria | Cada 6 meses |
| DHT22 | Resistencia pull-up 10 kΩ recomendada | Cada 6 meses |
| BH1750 | Dirección I2C 0x23 por defecto | Anual |
| Soil Moisture | ADC ADS1115 obligatorio | Cada 3 meses |
| MHZ-19C | Precalentamiento 3 min al encender | Cada 6 meses |

### DIR-072: Instalación en Invernadero

- Los sensores **DEBEN** instalarse protegidos de la lluvia directa.
- El gateway **DEBE** ubicarse en una caja protectora IP40+ con ventilación.
- Los cables **DEBEN** canalizarse para evitar daños por herramientas agrícolas.
- La distancia máxima entre sensor y gateway no debe exceder 100 metros (1-Wire).

---

## 9. Directiva de Documentación

### DIR-080: Documentación Obligatoria

Todo componente del sistema **DEBE** documentarse en los siguientes niveles:

| Nivel | Documento | Audiencia |
|-------|-----------|-----------|
| Visión | README.md, Roadmap | Todos |
| Arquitectura | architecture.md, diagramas-esquemas.md | Arquitectos, desarrolladores |
| API | api-testing-devops.md, Swagger/OpenAPI | Desarrolladores |
| Usuario | manual-usuario.md | Usuarios finales |
| Operación | deployment.md, troubleshooting.md | DevOps |
| Normativo | normas-estandares.md, directivas-proyecto.md | Gestión, auditoría |

### DIR-081: Formato de Documentación

- Formato: Markdown (`.md`).
- Idioma: Español (documentación principal), inglés (comentarios en código).
- Diagramas: Mermaid (renderizable en GitHub).
- Nombrado: kebab-case (`nombre-del-documento.md`).
- Actualización: Toda documentación debe actualizarse cuando se modifique la funcionalidad relacionada.

### DIR-082: Versionado

- La documentación sigue el mismo versionado que el software (SemVer).
- Los cambios significativos en documentación se registran en CHANGELOG.md.

---

## 10. Directiva de Sostenibilidad

### DIR-090: Eficiencia Energética

- El gateway **DEBE** operar con consumo < 10W en operación normal.
- Los sensores **DEBEN** apagarse cuando no están en ciclo de lectura (cuando sea posible).
- El polling de sensores debe ser configurable para reducir consumo.

### DIR-091: Impacto Ambiental

- El sistema **DEBE** contribuir a la reducción del uso de agua mediante alertas de humedad del suelo.
- Los reportes **DEBEN** incluir métricas de eficiencia hídrica cuando se integren actuadores de riego.
- Se favorecen componentes de hardware reutilizables y reparables.

### DIR-092: Accesibilidad

- La interfaz web **DEBE** cumplir con WCAG 2.1 nivel AA.
- Los reportes **DEBEN** ser accesibles en formato texto (no solo gráficas).
- El sistema **DEBE** soportar conexiones de bajo ancho de banda (< 1 Mbps).

---

## Historial de Revisiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | Marzo 2026 | Versión inicial — 10 directivas, 30+ sub-directivas |

---

*Última actualización: Marzo 2026 · EchoSmart Dev Team*
