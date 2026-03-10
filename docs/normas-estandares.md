# EchoSmart — Normas y Estándares Aplicables

Este documento describe las normas nacionales (mexicanas) e internacionales que aplican al diseño, desarrollo y operación de la plataforma EchoSmart como sistema IoT para invernaderos inteligentes.

---

## Índice

1. [Normas Mexicanas (NOM / NMX)](#1-normas-mexicanas-nom--nmx)
2. [Normas Internacionales (ISO / IEC)](#2-normas-internacionales-iso--iec)
3. [Estándares de Comunicación IoT](#3-estándares-de-comunicación-iot)
4. [Normas de Seguridad Eléctrica y Hardware](#4-normas-de-seguridad-eléctrica-y-hardware)
5. [Estándares de Calidad de Software](#5-estándares-de-calidad-de-software)
6. [Normas Ambientales y Agrícolas](#6-normas-ambientales-y-agrícolas)
7. [Matriz de Cumplimiento](#7-matriz-de-cumplimiento)

---

## 1. Normas Mexicanas (NOM / NMX)

### NOM-001-SAGARPA/SEMARNAT (Agricultura Protegida)

- **Alcance:** Regula las especificaciones técnicas para la producción agrícola en ambientes controlados (invernaderos, casas sombra, macrotúnel).
- **Aplicación en EchoSmart:** El sistema de monitoreo asegura que las condiciones ambientales del invernadero se mantengan dentro de los rangos que establece la norma para cada tipo de cultivo.

### NMX-I-27001-NYCE-2015

- **Alcance:** Adaptación mexicana de ISO/IEC 27001 para sistemas de gestión de seguridad de la información (SGSI).
- **Aplicación en EchoSmart:**
  - Cifrado TLS/SSL para todas las comunicaciones.
  - Autenticación JWT con tokens de corta duración.
  - Control de acceso basado en roles (RBAC).
  - Auditoría de eventos y accesos.

### NOM-019-SCFI (Seguridad en Equipos Electrónicos)

- **Alcance:** Requisitos de seguridad para equipos de procesamiento de datos y equipos electrónicos de oficina.
- **Aplicación en EchoSmart:** El gateway (Raspberry Pi) y los sensores conectados deben cumplir con los requisitos de seguridad eléctrica establecidos.

### NMX-I-62443-NYCE (Ciberseguridad Industrial)

- **Alcance:** Adaptación mexicana de IEC 62443 para seguridad en sistemas de automatización y control industrial.
- **Aplicación en EchoSmart:**
  - Segmentación de red entre zona IoT y zona de gestión.
  - Autenticación mutua entre gateway y backend.
  - Actualización segura de firmware OTA.

### NOM-001-SEDE (Instalaciones Eléctricas)

- **Alcance:** Requisitos de seguridad para instalaciones eléctricas en México.
- **Aplicación en EchoSmart:** Las instalaciones eléctricas del invernadero (alimentación de sensores, actuadores, gateway) deben cumplir con los lineamientos de esta norma.

---

## 2. Normas Internacionales (ISO / IEC)

### ISO/IEC 30141:2018 — Arquitectura de Referencia IoT

- **Alcance:** Define un marco de referencia para la arquitectura de sistemas IoT, incluyendo dominios funcionales, modelos de referencia y patrones de interoperabilidad.
- **Aplicación en EchoSmart:**
  - Arquitectura de 3 capas (Edge, Cloud, Cliente) alineada con los dominios funcionales de la norma.
  - Separación clara de responsabilidades entre capas.
  - Interoperabilidad mediante protocolos estándar (MQTT, HTTP REST, WebSocket).

### ISO/IEC 27001:2022 — Seguridad de la Información

- **Alcance:** Especifica los requisitos para establecer, implementar, mantener y mejorar un SGSI.
- **Aplicación en EchoSmart:**
  - Política de contraseñas (bcrypt, mínimo 12 caracteres).
  - Cifrado en tránsito (TLS 1.3) y en reposo (AES-256).
  - Gestión de sesiones con expiración automática.
  - Registro de auditoría inmutable.

### ISO/IEC 27017:2015 — Seguridad en Servicios Cloud

- **Alcance:** Guía de controles de seguridad para servicios en la nube.
- **Aplicación en EchoSmart:**
  - Aislamiento multi-tenant en la capa de datos.
  - Row-level security en PostgreSQL.
  - Cifrado de datos por tenant.

### IEC 62443 — Seguridad en Automatización Industrial

- **Alcance:** Serie de estándares para seguridad de sistemas de automatización y control industrial (IACS).
- **Aplicación en EchoSmart:**
  - Zonas y conductos de seguridad entre capas.
  - Evaluación de riesgos de componentes IoT.
  - Políticas de actualización y parcheo.

### ISO 22000 / ISO 22005 — Seguridad Alimentaria y Trazabilidad

- **Alcance:** Sistemas de gestión de seguridad alimentaria y trazabilidad en la cadena de alimentos.
- **Aplicación en EchoSmart:**
  - Registro histórico de condiciones ambientales vinculadas a lotes de cultivo.
  - Trazabilidad completa de alertas y acciones correctivas.
  - Reportes de condiciones de producción para certificaciones.

---

## 3. Estándares de Comunicación IoT

### MQTT 3.1.1 / 5.0 (OASIS)

| Aspecto | Detalle |
|---------|---------|
| **Estándar** | OASIS MQTT v3.1.1 (ISO/IEC 20922:2016) |
| **Uso en EchoSmart** | Comunicación entre sensores, gateway y nube |
| **QoS** | Nivel 1 (al menos una vez) |
| **Seguridad** | TLS 1.3, autenticación usuario/contraseña |
| **Broker** | Mosquitto 2.0+ |

### HTTP/HTTPS — REST API

| Aspecto | Detalle |
|---------|---------|
| **Estándar** | RFC 7231 (HTTP/1.1), RFC 7540 (HTTP/2) |
| **Uso en EchoSmart** | API REST del backend, sincronización gateway-nube |
| **Seguridad** | HTTPS obligatorio, certificados Let's Encrypt |
| **Formato** | JSON (RFC 8259) |

### WebSocket (RFC 6455)

| Aspecto | Detalle |
|---------|---------|
| **Estándar** | RFC 6455 |
| **Uso en EchoSmart** | Actualización en tiempo real del dashboard |
| **Seguridad** | WSS (WebSocket sobre TLS) |
| **Eventos** | readings.new, alerts.triggered, sensor.status |

### Protocolos de Bus de Sensores

| Protocolo | Estándar | Sensores |
|-----------|----------|----------|
| 1-Wire | Dallas Semiconductor | DS18B20 (temperatura) |
| I2C | NXP Semiconductors | BH1750 (luz), ADS1115 (ADC) |
| GPIO | Broadcom BCM2711 | DHT22 (temp+humedad) |
| UART | RS-232 / TTL | MHZ-19C (CO₂) |

---

## 4. Normas de Seguridad Eléctrica y Hardware

### IEC 61010-1 — Seguridad de Equipos de Medición

- **Alcance:** Requisitos de seguridad para equipos eléctricos de medición, control y uso en laboratorio.
- **Aplicación:** Sensores y circuitos de medición del gateway.

### IEC 60529 — Grados de Protección IP

- **Aplicación en EchoSmart:**
  - Gateway (interior): IP40 mínimo.
  - Sensores de suelo: IP67 recomendado.
  - Sensor de temperatura exterior: IP65 mínimo.

### CE / FCC — Compatibilidad Electromagnética

- **Alcance:** Regulaciones de emisiones e inmunidad electromagnética.
- **Aplicación:** La Raspberry Pi 4B cuenta con certificación CE y FCC. Los sensores deben verificar cumplimiento EMC.

---

## 5. Estándares de Calidad de Software

### ISO/IEC 25010 — Calidad del Producto de Software

La plataforma EchoSmart se evalúa según las 8 características de calidad:

| Característica | Implementación |
|----------------|----------------|
| **Funcionalidad** | 30+ endpoints API, 5 tipos de sensor, alertas, reportes |
| **Rendimiento** | p99 < 200 ms, WebSocket < 1s, edge < 100ms |
| **Compatibilidad** | REST API estándar, MQTT estándar, JSON |
| **Usabilidad** | Dashboard responsive, i18n, accesibilidad WCAG 2.1 |
| **Fiabilidad** | 99.9% SLA, operación offline, reintentos automáticos |
| **Seguridad** | JWT, RBAC, TLS, cifrado, auditoría |
| **Mantenibilidad** | Arquitectura modular, CI/CD, cobertura > 80% |
| **Portabilidad** | Docker, Kubernetes, multi-cloud |

### ISO/IEC 12207 — Procesos del Ciclo de Vida del Software

- **Aplicación:** Procesos de desarrollo, pruebas, despliegue y mantenimiento documentados en la guía de contribución y pipeline CI/CD.

### IEEE 830 — Especificación de Requisitos de Software

- **Aplicación:** Los documentos de arquitectura y funcionalidad siguen las directrices de IEEE 830 para especificación de requisitos (completos, consistentes, verificables, trazables).

---

## 6. Normas Ambientales y Agrícolas

### NOM-017-STPS — Equipo de Protección Personal

- **Aplicación:** Personal que instala y mantiene sensores y gateway en el invernadero.

### NOM-081-ECOL — Límites de Ruido

- **Aplicación:** Los ventiladores y actuadores controlados por el sistema deben operar dentro de los límites de ruido permitidos.

### Buenas Prácticas Agrícolas (BPA) — SENASICA

- **Aplicación:** El sistema de monitoreo apoya el cumplimiento de BPA al registrar condiciones ambientales, alertar ante desviaciones y generar reportes de trazabilidad.

### Rangos Ambientales Recomendados para Invernaderos

| Variable | Rango Óptimo | Alerta Baja | Alerta Alta | Fuente |
|----------|-------------|-------------|-------------|--------|
| Temperatura | 18°C – 28°C | < 10°C | > 35°C | FAO / SAGARPA |
| Humedad Relativa | 60% – 80% | < 40% | > 90% | FAO |
| Luminosidad | 10,000 – 30,000 lux | < 5,000 lux | > 50,000 lux | FAO |
| CO₂ | 400 – 1,000 ppm | < 300 ppm | > 1,500 ppm | ASHRAE |
| Humedad del Suelo | 50% – 80% | < 30% | > 95% | INIFAP |

---

## 7. Matriz de Cumplimiento

| Norma | Categoría | Estado | Prioridad |
|-------|-----------|--------|-----------|
| ISO/IEC 30141 (IoT) | Arquitectura | ✅ Cumple | Alta |
| ISO/IEC 27001 (Seguridad) | Seguridad | ✅ Cumple | Alta |
| IEC 62443 (Industrial) | Seguridad | 🔶 Parcial | Alta |
| NMX-I-27001-NYCE | Seguridad | ✅ Cumple | Alta |
| MQTT 3.1.1 (OASIS) | Comunicación | ✅ Cumple | Alta |
| ISO/IEC 25010 (Software) | Calidad | ✅ Cumple | Media |
| ISO 22005 (Trazabilidad) | Agricultura | 🔶 Parcial | Media |
| NOM-001-SAGARPA | Agricultura | ✅ Cumple | Media |
| IEC 60529 (IP) | Hardware | 🔶 Parcial | Media |
| NOM-001-SEDE (Eléctrica) | Infraestructura | ⬜ Pendiente | Baja |

**Leyenda:** ✅ Cumple | 🔶 Parcial | ⬜ Pendiente

---

*Última actualización: Marzo 2026 · EchoSmart Dev Team*
