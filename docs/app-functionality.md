# EchoSmart — Funcionalidad de la Aplicación

Descripción completa de las capacidades y funciones de la plataforma EchoSmart.

---

## Visión General

EchoSmart es una plataforma IoT de agricultura de precisión que permite el monitoreo ambiental inteligente en invernaderos. El sistema opera en tres capas (Edge, Cloud y Frontend) para ofrecer lecturas en tiempo real, alertas configurables, reportes automatizados y gestión multi-tenant.

---

## 1. Monitoreo en Tiempo Real

### Lectura de Sensores
- Soporte para **5 tipos de sensores**: temperatura (DS18B20), temperatura y humedad (DHT22), luminosidad (BH1750), humedad de suelo (Soil Moisture) y CO₂ (MHZ-19C).
- Intervalo de lectura configurable de **60 segundos a 24 horas**.
- **Hot-plug**: los sensores se auto-descubren al conectarse al gateway mediante SSDP.
- Caché local en SQLite para resiliencia ante pérdida de conectividad.

### Visualización
- Dashboard con gráficas de línea temporal para cada variable ambiental.
- KPIs rápidos: total de sensores, sensores en línea, alertas activas.
- Gráficas de comparación multi-sensor y distribución espacial (heatmap).
- Actualización instantánea vía **WebSocket**.

### Histórico de Datos
- Retención configurable por sensor y por tenant.
- Agregaciones estadísticas: promedio, mínimo, máximo por rango de tiempo.
- Exportación a **CSV** y **PDF**.

---

## 2. Sistema de Alertas

### Reglas de Alerta
- Condiciones flexibles: mayor que, menor que, igual a, fuera de rango.
- Cuatro niveles de severidad: **crítica**, **alta**, **media**, **baja**.
- Mecanismo de **cooldown** para evitar notificaciones repetitivas.
- Evaluación dual: primero en el gateway (edge) y con redundancia en la nube.

### Canales de Notificación
| Canal | Tecnología |
|-------|-----------|
| Email | SMTP / SendGrid |
| SMS | Twilio |
| Push | Firebase Cloud Messaging |
| Webhooks | HTTP POST a URL configurada |

### Gestión de Alertas
- Centro de alertas con filtros por severidad, sensor y estado.
- Historial completo de alertas con marca de tiempo.
- Flujo de **acknowledgment** para confirmar la atención de cada alerta.

---

## 3. Generación de Reportes

- Generación **asincrónica** mediante workers en segundo plano.
- Formatos disponibles: **PDF** y **Excel**.
- Gráficas embebidas con datos agregados del período seleccionado.
- Período de tiempo configurable (últimas 24 h, semana, mes, personalizado).
- Descarga segura con enlaces temporales autenticados.
- Lista de reportes guardados con estado de generación (pendiente, listo, error).

---

## 4. Gestión de Sensores

- Alta, baja y modificación (CRUD) de sensores desde el dashboard.
- Detalle individual con últimas lecturas, estado (online/offline) y metadatos.
- Agrupación por tipo de sensor y por ubicación dentro del invernadero.
- Calibración interactiva mediante scripts Python en el gateway.

---

## 5. Gestión del Gateway

- Registro y administración de múltiples gateways desde la nube.
- Estado en tiempo real de cada gateway: conectado, desconectado, última sincronización.
- **Reinicio remoto** del gateway desde el panel de administración.
- Sincronización de lecturas en lotes (batch) cada 5 minutos con reintentos y backoff exponencial.
- Motor de alertas local que opera incluso sin conexión a la nube.

---

## 6. Multi-Tenancy

- Aislamiento completo de datos entre organizaciones (tenants).
- **Branding personalizado**: logotipo, colores y nombre de empresa por tenant.
- Roles de usuario con control de acceso basado en roles (**RBAC**):
  - **Admin**: acceso total, gestión de usuarios y configuración del tenant.
  - **Operator**: lectura y escritura de sensores, gestión de alertas.
  - **Viewer**: acceso de solo lectura a dashboards y reportes.
- Límites de uso configurables por tier de suscripción.
- Row-level security en PostgreSQL para aislamiento a nivel de base de datos.

---

## 7. Autenticación y Seguridad

- Autenticación con **JWT** (access token de 24 h + refresh token de 30 días).
- Rotación automática de refresh tokens.
- Contraseñas hasheadas con **bcrypt + salt**.
- Comunicaciones cifradas con **HTTPS/TLS 1.3**.
- Rate limiting en todos los endpoints de la API.
- CORS configurado por entorno.

Para más detalle, consultar la [Documentación de Seguridad](security.md).

---

## 8. API REST

La plataforma expone más de **30 endpoints** organizados en los siguientes módulos:

| Módulo | Endpoints Principales |
|--------|----------------------|
| Autenticación | Login, refresh, logout, reset de contraseña |
| Gateways | CRUD, reboot, sincronización de lecturas |
| Sensores | CRUD, historial de lecturas con agregaciones |
| Alertas | Listar, historial, crear reglas, acknowledge |
| Reportes | Generar, listar, descargar |
| WebSocket | Suscripción en tiempo real por sensor |

Para la especificación completa, consultar [API, Testing y DevOps](api-testing-devops.md).

---

## 9. Flujo de Datos End-to-End

```
Sensor → Gateway (lectura) → SQLite (caché local) → MQTT (publicación local)
                ↓
        Motor de alertas local
                ↓
        Cloud Sync (HTTP batch cada 5 min)
                ↓
        Backend → InfluxDB (time-series) + PostgreSQL (metadata)
                ↓
        WebSocket → Dashboard React (actualización en tiempo real)
```

1. El gateway lee todos los sensores conectados según el intervalo configurado.
2. Las lecturas se almacenan localmente en SQLite y se publican en MQTT.
3. El motor de alertas local evalúa las reglas y genera alertas si corresponde.
4. Cada 5 minutos, el Cloud Sync Manager envía un lote de lecturas al backend.
5. El backend almacena los datos en InfluxDB y actualiza métricas agregadas.
6. Los dashboards conectados por WebSocket reciben las actualizaciones al instante.

---

## 10. Aplicaciones Móviles

- App nativa con **React Native** (Expo) para iOS y Android.
- Sincronización offline: el usuario puede consultar los últimos datos sin conexión.
- Notificaciones push para alertas críticas.
- Soporte para temas claro y oscuro.
- Publicación en App Store y Google Play.

---

*Volver al [Índice de Documentación](README.md)*
