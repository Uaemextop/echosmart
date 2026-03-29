# EchoSmart — Índice de Documentación

Bienvenido a la documentación técnica de **EchoSmart**, la plataforma IoT de agricultura de precisión para monitoreo ambiental inteligente en invernaderos.

---

## Inicio Rápido

| Documento | Descripción |
|-----------|-------------|
| [Primeros Pasos](getting-started.md) | Instalación, configuración y puesta en marcha |
| [Funcionalidad de la Aplicación](app-functionality.md) | Descripción completa de las funciones del sistema |
| [Estructura del Proyecto](project-structure.md) | Organización de carpetas, módulos y dependencias |

---

## Arquitectura y Diseño

| Documento | Descripción |
|-----------|-------------|
| [Arquitectura de Software](architecture.md) | Visión general de la arquitectura de 3 capas (Edge, Cloud, Frontend) |
| [Protocolos de Comunicación](communication-protocols.md) | MQTT, 1-Wire, I2C, UART, HTTP REST y WebSocket |
| [Esquema de Base de Datos](database-schema.md) | PostgreSQL, InfluxDB, Redis y SQLite |
| [Roadmap Ejecutivo](roadmap.md) | Fases de implementación, milestones y KPIs |
| [Funcionalidades y Roadmap de Features](features-roadmap.md) | Catálogo completo de features actuales y futuras |

---

## Backend

| Documento | Descripción |
|-----------|-------------|
| [Integración Backend](backend-integration.md) | Arquitectura del backend, flujos de datos E2E |
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

## Producción y Comercialización

| Documento | Descripción |
|-----------|-------------|
| [Kit de Producción](production-kit.md) | BOM, ensamblaje, empaquetado, precios y flujo de producción en masa |
| [Empaquetado .deb](deb-packaging.md) | Construcción, instalación y distribución del paquete Debian del gateway |

---

## Operaciones

| Documento | Descripción |
|-----------|-------------|
| [Infraestructura Local de Desarrollo](local-dev-infrastructure.md) | Setup del entorno de desarrollo con un solo comando, emuladores de sensores, Makefile |
| [ISO del Servidor](server-iso-setup.md) | ISO personalizado con todo el software del servidor, wizard de configuración, echosmart-ctl |
| [ISO del Gateway Raspberry Pi](gateway-iso-setup.md) | Imagen personalizada del RPi, auto-conexión al servidor, gestión remota |
| [Despliegue en la Nube](cloud-deployment.md) | Despliegue real en AWS y DigitalOcean, configuración de Raspberry Pi en producción |
| [Despliegue General](deployment.md) | Docker, Kubernetes y configuración local |
| [Variables de Entorno](environment-variables.md) | Referencia completa de variables de entorno por componente |
| [Seguridad](security.md) | Autenticación, autorización, protección de datos y auditoría |
| [Resolución de Problemas](troubleshooting.md) | Diagnóstico y solución de problemas frecuentes |

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
4. [Funcionalidades y Roadmap de Features](features-roadmap.md)

### Ingenieros Backend
1. [Estructura del Proyecto](project-structure.md)
2. [Integración Backend](backend-integration.md)
3. [Funciones del Backend](backend-functions.md)
4. [Esquema de Base de Datos](database-schema.md)
5. [API, Testing y DevOps](api-testing-devops.md)
6. [Variables de Entorno](environment-variables.md)

### Ingenieros Frontend
1. [Frontend React](frontend.md)
2. [API, Testing y DevOps](api-testing-devops.md)
3. [Variables de Entorno](environment-variables.md)

### Ingenieros de Hardware / Gateway
1. [Configuración de Raspberry Pi OS](raspberry-pi-setup.md)
2. [Sensores y Hardware](sensors-hardware.md)
3. [Gateway y Edge Computing](gateway-edge-computing.md)
4. [Protocolos de Comunicación](communication-protocols.md)
5. [Resolución de Problemas](troubleshooting.md)

### Producción / Comercialización
1. [Kit de Producción](production-kit.md)
2. [Empaquetado .deb](deb-packaging.md)

### DevOps / Operaciones
1. [Infraestructura Local de Desarrollo](local-dev-infrastructure.md)
2. [ISO del Servidor](server-iso-setup.md)
3. [ISO del Gateway Raspberry Pi](gateway-iso-setup.md)
4. [Despliegue en la Nube](cloud-deployment.md)
5. [Despliegue General](deployment.md)
6. [Variables de Entorno](environment-variables.md)
7. [Seguridad](security.md)
8. [Resolución de Problemas](troubleshooting.md)

---

## Estadísticas de Documentación

| Métrica | Valor |
|---------|-------|
| Total de documentos | 26 |
| Endpoints API documentados | 30+ |
| Sensores documentados | 5 tipos (+8 futuros) |
| Protocolos documentados | 7 (MQTT, 1-Wire, I2C, UART, GPIO, HTTP, WebSocket) |
| Variables de entorno documentadas | 40+ |
| Ejemplos de código | 100+ |
| Test cases | 50+ |
| Scripts de automatización | 15+ |
| ISOs documentados | 2 (servidor + RPi gateway) |

---

## Referencias Externas

- [Raspberry Pi Docs](https://www.raspberrypi.com/documentation/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [InfluxDB](https://docs.influxdata.com/)
- [Mosquitto MQTT](https://mosquitto.org/documentation/)
- [Docker](https://docs.docker.com/)
- [Kubernetes](https://kubernetes.io/docs/)

---

*Última actualización: Marzo 2026 · Mantenido por EchoSmart Dev Team*
