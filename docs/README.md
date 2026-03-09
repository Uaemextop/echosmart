# EchoSmart — Índice de Documentación

Bienvenido a la documentación técnica de **EchoSmart**, la plataforma IoT de agricultura de precisión para monitoreo ambiental inteligente en invernaderos.

---

## Inicio Rápido

| Documento | Descripción |
|-----------|-------------|
| [Primeros Pasos](getting-started.md) | Instalación, configuración y puesta en marcha |
| [Funcionalidad de la Aplicación](app-functionality.md) | Descripción completa de las funciones del sistema |

---

## Arquitectura y Diseño

| Documento | Descripción |
|-----------|-------------|
| [Arquitectura de Software](architecture.md) | Visión general de la arquitectura de 3 capas (Edge, Cloud, Frontend) |
| [Protocolos de Comunicación](communication-protocols.md) | MQTT, 1-Wire, I2C, UART, HTTP REST y WebSocket |
| [Roadmap Ejecutivo](roadmap.md) | Fases de implementación, milestones y KPIs |

---

## Backend

| Documento | Descripción |
|-----------|-------------|
| [Integración Backend](backend-integration.md) | Arquitectura del backend, esquemas de base de datos, flujos de datos E2E |
| [Funciones del Backend](backend-functions.md) | Documentación detallada de servicios y funciones del backend (FastAPI) |
| [API, Testing y DevOps](api-testing-devops.md) | Especificación REST API, estrategia de testing y pipeline CI/CD |

---

## Frontend

| Documento | Descripción |
|-----------|-------------|
| [Frontend React](frontend.md) | Componentes React, Redux, hooks personalizados, i18n y testing |

---

## Gateway y Hardware

| Documento | Descripción |
|-----------|-------------|
| [Configuración de Raspberry Pi OS](raspberry-pi-setup.md) | Instalación del SO, configuración de red, interfaces de hardware y servicios del sistema |
| [Gateway y Edge Computing](gateway-edge-computing.md) | Arquitectura del gateway, HAL, drivers y sincronización |
| [Sensores y Hardware](sensors-hardware.md) | Catálogo de 5 sensores soportados, conexión, código Python y calibración |

---

## Operaciones

| Documento | Descripción |
|-----------|-------------|
| [Despliegue](deployment.md) | Guía de despliegue con Docker, Kubernetes y configuración de producción |
| [Seguridad](security.md) | Autenticación, autorización, protección de datos y auditoría |

---

## Comunidad

| Documento | Descripción |
|-----------|-------------|
| [Contribución al Proyecto](contributing.md) | Cómo contribuir, convenciones de código y flujo de trabajo |

---

## Guías por Rol

### Arquitectos / Tomadores de Decisión
1. [Roadmap Ejecutivo](roadmap.md)
2. [Arquitectura de Software](architecture.md)
3. [Funcionalidad de la Aplicación](app-functionality.md)

### Ingenieros Backend
1. [Integración Backend](backend-integration.md)
2. [Funciones del Backend](backend-functions.md)
3. [API, Testing y DevOps](api-testing-devops.md)

### Ingenieros Frontend
1. [Frontend React](frontend.md)
2. [API, Testing y DevOps](api-testing-devops.md)

### Ingenieros de Hardware / Gateway
1. [Configuración de Raspberry Pi OS](raspberry-pi-setup.md)
2. [Sensores y Hardware](sensors-hardware.md)
3. [Gateway y Edge Computing](gateway-edge-computing.md)
4. [Protocolos de Comunicación](communication-protocols.md)

### DevOps / Operaciones
1. [Despliegue](deployment.md)
2. [Seguridad](security.md)
3. [API, Testing y DevOps](api-testing-devops.md)

---

## Estadísticas de Documentación

| Métrica | Valor |
|---------|-------|
| Total de documentos | 16 |
| Endpoints API documentados | 30+ |
| Sensores documentados | 5 tipos |
| Protocolos documentados | 7 (MQTT, 1-Wire, I2C, UART, GPIO, HTTP, WebSocket) |
| Ejemplos de código | 100+ |
| Test cases | 50+ |

---

## Referencias Externas

- [Raspberry Pi Docs](https://www.raspberrypi.com/documentation/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [InfluxDB](https://docs.influxdata.com/)
- [Mosquitto MQTT](https://mosquitto.org/documentation/)

---

*Última actualización: Marzo 2026 · Mantenido por EchoSmart Dev Team*
