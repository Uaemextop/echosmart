# EchoSmart — Funcionalidades y Roadmap de Features

Catálogo completo de funcionalidades actuales y futuras de la plataforma, organizadas por módulo y prioridad.

---

## 1. Funcionalidades del MVP (Fase 1–3)

### 1.1 Monitoreo de Sensores

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Lectura periódica de sensores | Polling configurable (60 s – 24 h) para todos los sensores conectados | Alta |
| Hot-plug de sensores | Auto-descubrimiento al conectar/desconectar sensores vía SSDP | Alta |
| Caché local (SQLite) | Almacenamiento local de lecturas para resiliencia offline | Alta |
| Sincronización batch | Envío de lecturas al backend cada 5 min con reintentos exponenciales | Alta |
| Dashboard en tiempo real | Gráficas de línea temporal con actualización vía WebSocket | Alta |
| KPIs rápidos | Total de sensores, sensores online, alertas activas | Alta |
| Historial de datos | Consulta de lecturas con filtros por rango de tiempo | Alta |
| Agregaciones | Promedio, mínimo y máximo por hora/día/semana | Media |
| Exportación CSV | Descargar lecturas históricas en formato CSV | Media |

### 1.2 Sistema de Alertas

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Reglas de alerta configurables | Condiciones: mayor, menor, igual, fuera de rango | Alta |
| Niveles de severidad | Crítica, alta, media, baja | Alta |
| Evaluación local (edge) | El gateway evalúa reglas sin depender de la nube | Alta |
| Evaluación cloud (redundante) | El backend re-evalúa reglas como respaldo | Alta |
| Cooldown por regla | Evita notificaciones repetitivas (configurable por minutos) | Alta |
| Notificación por email | Envío vía SMTP / SendGrid | Alta |
| Centro de alertas | Panel con alertas activas, filtros y búsqueda | Alta |
| Historial de alertas | Registro completo con timestamps | Media |
| Acknowledgment de alertas | Flujo para confirmar la atención de una alerta | Media |

### 1.3 Gestión de Sensores y Gateways

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| CRUD de sensores | Alta, baja, modificación y consulta de sensores | Alta |
| CRUD de gateways | Registro y administración de gateways | Alta |
| Estado en tiempo real | Online/offline con última hora de contacto | Alta |
| Reinicio remoto del gateway | Comando de reboot desde el panel de administración | Media |
| Detalle individual de sensor | Últimas lecturas, estado, metadatos y ubicación | Media |

### 1.4 Autenticación y Multi-tenancy

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Login con email/contraseña | JWT access + refresh tokens | Alta |
| RBAC | Roles admin, operator, viewer con permisos diferenciados | Alta |
| Aislamiento por tenant | Row-level security en PostgreSQL | Alta |
| Gestión de usuarios | CRUD de usuarios por tenant | Alta |
| Branding por tenant | Logo, colores y nombre de empresa personalizables | Media |
| Forgot password | Flujo de recuperación de contraseña por email | Media |

---

## 2. Funcionalidades Avanzadas (Fase 4–5)

### 2.1 Reportes

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Generación de reportes PDF | Asincrónica con gráficas embebidas | Alta |
| Generación de reportes Excel | Datos tabulados con múltiples hojas | Alta |
| Configuración de período | Últimas 24 h, semana, mes, personalizado | Alta |
| Selección de sensores | Elegir qué sensores incluir en el reporte | Media |
| Descarga segura | Links temporales autenticados | Media |
| Reportes programados | Generación automática (diario, semanal, mensual) | Baja |
| Plantillas de reporte | Definir formatos reutilizables | Baja |

### 2.2 Aplicación Móvil

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Dashboard móvil | Resumen de sensores y alertas en pantalla principal | Alta |
| Push notifications | Alertas críticas vía Firebase Cloud Messaging | Alta |
| Modo offline | Consultar últimos datos sin conexión | Media |
| Dark/light mode | Temas claro y oscuro | Media |
| Biometric login | Autenticación con huella dactilar o Face ID | Baja |

### 2.3 Notificaciones Avanzadas

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| SMS (Twilio) | Alertas por mensaje de texto | Media |
| Push notifications (Firebase) | Alertas en app móvil | Media |
| Webhooks | HTTP POST a URL configurada por el usuario | Media |
| WhatsApp Business | Alertas vía WhatsApp | Baja |
| Slack / Microsoft Teams | Integración con canales de equipo | Baja |
| Telegram Bot | Notificaciones por Telegram | Baja |

---

## 3. Funcionalidades Futuras (Post-MVP)

### 3.1 Control de Actuadores

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Control de relés | Encender/apagar dispositivos desde el dashboard (riego, ventilación, iluminación) | Alta |
| Programación horaria | Programar activación de actuadores por horario | Media |
| Automatización por reglas | Si temperatura > 35°C → activar ventilación | Media |
| Control manual remoto | Botón on/off desde el dashboard o app móvil | Media |
| Historial de actuaciones | Registro de cuándo se activó cada actuador | Baja |

### 3.2 Analítica Predictiva (Machine Learning)

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Predicción de temperatura | Modelo que predice la temperatura en las próximas horas | Media |
| Detección de anomalías | Identificar lecturas fuera de lo normal sin reglas manuales | Media |
| Recomendaciones de riego | Sugerir cuándo y cuánto regar basado en humedad de suelo y clima | Baja |
| Análisis de tendencias | Identificar patrones estacionales y correlaciones | Baja |
| Modelo de crecimiento | Estimar el crecimiento del cultivo con base en datos ambientales | Baja |

### 3.3 Geolocalización e Invernaderos

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Mapa de invernaderos | Vista geográfica con ubicación de cada invernadero | Media |
| Mapa de zonas internas | Plano del invernadero con ubicación de sensores | Media |
| Heatmap ambiental | Mapa de calor con temperatura/humedad por zona | Baja |
| Comparación entre invernaderos | Dashboard comparativo entre múltiples ubicaciones | Baja |

### 3.4 Integración con Servicios Externos

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| API meteorológica | Datos del clima exterior (OpenWeatherMap, Weather API) | Media |
| Google Sheets export | Sincronización automática de datos a hojas de cálculo | Baja |
| ERP integration | Conexión con sistemas de gestión empresarial | Baja |
| IFTTT / Zapier | Automatización con servicios de terceros | Baja |
| API pública | Endpoints abiertos (con API key) para integraciones de terceros | Baja |

### 3.5 Administración Avanzada

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Audit log completo | Registro de todas las acciones de usuario con timestamps | Media |
| Gestión de suscripciones | Planes (free, pro, enterprise) con límites diferenciados | Media |
| Facturación integrada | Integración con Stripe para cobros automáticos | Baja |
| SSO (Single Sign-On) | Login con Google, Microsoft o SAML | Baja |
| 2FA (Autenticación de dos factores) | TOTP con app de autenticación | Media |
| White-label | Personalización completa para reventa | Baja |

### 3.6 Soporte para Más Sensores

| Sensor | Medición | Protocolo | Prioridad |
|--------|----------|-----------|-----------|
| BME280 | Presión + temp + humedad | I2C / SPI | Media |
| TSL2591 | Luminosidad de alta precisión | I2C | Baja |
| SCD30 / SCD40 | CO₂ + temp + humedad | I2C | Media |
| pH Sensor | pH del agua/suelo | Analógico | Media |
| EC Sensor | Conductividad eléctrica | Analógico | Media |
| Flow Meter | Caudal de agua | GPIO (pulsos) | Baja |
| Rain Gauge | Precipitación | GPIO (pulsos) | Baja |
| Anemómetro | Velocidad del viento | GPIO / Analógico | Baja |
| Cámara (RPi Camera) | Imagen del cultivo | CSI | Baja |

### 3.7 Escalabilidad e Infraestructura

| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Kubernetes auto-scaling | Escalar réplicas del backend automáticamente | Media |
| Base de datos read replicas | Réplicas de lectura para escalar consultas | Baja |
| CDN global | Distribución del frontend en múltiples regiones | Baja |
| Gateway mesh | Comunicación entre gateways locales (sin cloud) | Baja |
| Edge AI | Modelos de ML directamente en la Raspberry Pi | Baja |
| OTA updates | Actualización remota del firmware del gateway | Media |

---

## 4. Matriz de Prioridad por Fase

| Fase | Features Principales | Tiempo Estimado |
|------|---------------------|-----------------|
| **MVP** | Sensores, alertas básicas, dashboard, auth, multi-tenant | 10 semanas |
| **V1.1** | Reportes PDF/Excel, CRUD avanzado, email notifications | 3 semanas |
| **V1.2** | App móvil, push notifications, SMS | 6 semanas |
| **V2.0** | Actuadores, automatización por reglas, webhooks | 4 semanas |
| **V2.1** | WhatsApp, Slack, Telegram, reportes programados | 3 semanas |
| **V3.0** | ML predictivo, detección de anomalías, mapas | 6 semanas |
| **V3.1** | SSO, 2FA, facturación, white-label | 4 semanas |

---

*Volver al [Índice de Documentación](README.md)*
