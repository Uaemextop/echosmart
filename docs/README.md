# EchoSmart — Índice de Documentación

Documentación técnica de **EchoSmart**, kit IoT de agricultura de precisión
para monitoreo ambiental en invernaderos.

El gateway se ejecuta como **binarios C++ nativos** empaquetados en un
**paquete `.deb`** para Raspberry Pi OS (arm64).

---

## Inicio Rápido

| Documento | Descripción |
|-----------|-------------|
| [Primeros Pasos](getting-started.md) | Instalación del kit y puesta en marcha |
| [Estructura del Proyecto](project-structure.md) | Organización del monorepo |
| [Funcionalidad de la Aplicación](app-functionality.md) | Funciones del sistema |

---

## Gateway (C++ / .deb)

| Documento | Descripción |
|-----------|-------------|
| [Gateway y Edge Computing](gateway-edge-computing.md) | Arquitectura del gateway, binarios C++, systemd |
| [Empaquetado .deb](deb-packaging.md) | Cómo construir, instalar y actualizar el paquete .deb |
| [Kit de Producción](production-kit.md) | BOM, precios, ensamblaje y control de calidad |
| [Sensores y Hardware](sensors-hardware.md) | Catálogo de sensores, conexión y calibración |
| [Configuración de Raspberry Pi](raspberry-pi-setup.md) | Instalación del SO y configuración de interfaces |
| [ISO del Gateway](gateway-iso-setup.md) | Imagen pre-configurada para microSD |

---

## Arquitectura y Diseño

| Documento | Descripción |
|-----------|-------------|
| [Arquitectura de Software](architecture.md) | Diseño de 3 capas: Edge (C++), Cloud, Frontend |
| [Protocolos de Comunicación](communication-protocols.md) | 1-Wire, I2C, UART, GPIO, MQTT, HTTP, WebSocket |
| [Esquema de Base de Datos](database-schema.md) | PostgreSQL, InfluxDB, Redis |
| [Roadmap Ejecutivo](roadmap.md) | Fases, milestones y KPIs |

---

## Backend y API

| Documento | Descripción |
|-----------|-------------|
| [Integración Backend](backend-integration.md) | Flujos de datos gateway → cloud |
| [Funciones del Backend](backend-functions.md) | Servicios FastAPI |
| [API, Testing y DevOps](api-testing-devops.md) | REST API, testing y CI/CD |

---

## Frontend

| Documento | Descripción |
|-----------|-------------|
| [Frontend React](frontend.md) | Dashboard, gráficas, alertas |

---

## Operaciones

| Documento | Descripción |
|-----------|-------------|
| [Infraestructura Local](local-dev-infrastructure.md) | Docker Compose para desarrollo |
| [ISO del Servidor](server-iso-setup.md) | ISO del backend cloud |
| [Despliegue en la Nube](cloud-deployment.md) | AWS, DigitalOcean |
| [Despliegue General](deployment.md) | Docker, Kubernetes |
| [Variables de Entorno](environment-variables.md) | Referencia por componente |
| [Seguridad](security.md) | Autenticación y protección |
| [Resolución de Problemas](troubleshooting.md) | Diagnóstico y soluciones |
| [Contribución](contributing.md) | Cómo contribuir al proyecto |

---

*Última actualización: Marzo 2026*
