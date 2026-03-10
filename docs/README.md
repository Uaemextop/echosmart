# 🌱 EchoSmart — Índice de Documentación

Bienvenido a la documentación técnica de **EchoSmart**, la plataforma IoT de **invernadero inteligente** para monitoreo ambiental, control de actuadores y analítica predictiva en agricultura de precisión.

---

## 🌐 Página Web

| Recurso | Descripción |
|---------|-------------|
| [Landing Page](../web/index.html) | Página principal con funcionalidades, sensores, arquitectura y normativas |
| [Dashboard](../web/dashboard.html) | Dashboard interactivo con datos simulados en tiempo real |

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
| [Diagramas, Bocetos y Esquemas](diagramas-esquemas.md) | Diagramas Mermaid: arquitectura, ER, flujos E2E, alertas, JWT, gateway, MQTT, frontend, despliegue y roadmap |
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

## Normativas y Directivas

| Documento | Descripción |
|-----------|-------------|
| [Normas y Estándares](normas-estandares.md) | NOM mexicanas, ISO/IEC, estándares IoT, comunicación, calidad de software y normas agrícolas |
| [Directivas del Proyecto](directivas-proyecto.md) | Directivas de gobernanza, arquitectura, desarrollo, seguridad, calidad, datos y operación |

---

## Operaciones

| Documento | Descripción |
|-----------|-------------|
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

## Guías de Usuario

| Documento | Descripción |
|-----------|-------------|
| [Manual de Usuario](manual-usuario.md) | Guía completa para usuarios finales del sistema |
| [Glosario Técnico](glosario.md) | Definiciones de los términos técnicos utilizados en la documentación |

---

## Bocetos y Wireframes

Wireframes de las páginas principales de la aplicación web en formato PNG:

| Boceto | Página |
|--------|--------|
| [01-login.png](bocetos/01-login.png) | Pantalla de inicio de sesión |
| [02-dashboard.png](bocetos/02-dashboard.png) | Dashboard principal del invernadero |
| [03-sensores.png](bocetos/03-sensores.png) | Gestión de sensores |
| [04-alertas.png](bocetos/04-alertas.png) | Centro de alertas |
| [05-reportes.png](bocetos/05-reportes.png) | Generación de reportes |
| [06-admin.png](bocetos/06-admin.png) | Panel de administración |

---

## Guías por Rol

### Arquitectos / Tomadores de Decisión
1. [Roadmap Ejecutivo](roadmap.md)
2. [Arquitectura de Software](architecture.md)
3. [Diagramas, Bocetos y Esquemas](diagramas-esquemas.md)
4. [Normas y Estándares](normas-estandares.md)
5. [Directivas del Proyecto](directivas-proyecto.md)
6. [Funcionalidad de la Aplicación](app-functionality.md)
7. [Funcionalidades y Roadmap de Features](features-roadmap.md)

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

### DevOps / Operaciones
1. [Despliegue en la Nube](cloud-deployment.md)
2. [Despliegue General](deployment.md)
3. [Variables de Entorno](environment-variables.md)
4. [Seguridad](security.md)
5. [Resolución de Problemas](troubleshooting.md)

### Usuarios Finales / Agrónomos
1. [Manual de Usuario](manual-usuario.md)
2. [Glosario Técnico](glosario.md)
3. [Resolución de Problemas](troubleshooting.md)

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
| Normas aplicables | 10+ (NOM, ISO, IEC) |
| Directivas del proyecto | 30+ |
| Bocetos de páginas | 6 |
| Diagramas Mermaid | 15 |

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
