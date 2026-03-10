# EchoSmart — Manual de Usuario

Guía completa para usuarios de la plataforma EchoSmart de monitoreo de invernaderos inteligentes.

---

## Índice

1. [Introducción](#1-introducción)
2. [Acceso al Sistema](#2-acceso-al-sistema)
3. [Dashboard Principal](#3-dashboard-principal)
4. [Gestión de Sensores](#4-gestión-de-sensores)
5. [Centro de Alertas](#5-centro-de-alertas)
6. [Generación de Reportes](#6-generación-de-reportes)
7. [Control de Actuadores](#7-control-de-actuadores)
8. [Panel de Administración](#8-panel-de-administración)
9. [Preguntas Frecuentes](#9-preguntas-frecuentes)

---

## 1. Introducción

### ¿Qué es EchoSmart?

EchoSmart es una plataforma de **monitoreo ambiental para invernaderos** que le permite:

- **Monitorear en tiempo real** la temperatura, humedad, luminosidad, CO₂ y humedad del suelo de su invernadero.
- **Recibir alertas** cuando las condiciones salen de los rangos óptimos.
- **Generar reportes** automatizados con gráficas y datos históricos.
- **Controlar actuadores** (riego, ventilación, iluminación) de forma remota.

### Requisitos del Navegador

| Navegador | Versión Mínima |
|-----------|----------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

El dashboard es **responsive** y funciona en computadoras, tablets y teléfonos móviles.

---

## 2. Acceso al Sistema

### Iniciar Sesión

1. Abra su navegador y navegue a la URL de su instalación EchoSmart.
2. Ingrese su **correo electrónico** y **contraseña**.
3. Haga clic en **"Iniciar Sesión"**.

> 💡 **Consejo:** Active la opción "Recordar sesión" para mantener su sesión activa por 30 días en dispositivos de confianza.

### Recuperar Contraseña

1. En la pantalla de login, haga clic en **"¿Olvidaste tu contraseña?"**.
2. Ingrese su correo electrónico.
3. Revise su bandeja de entrada y siga el enlace de recuperación.
4. Establezca una nueva contraseña (mínimo 12 caracteres).

### Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **Viewer** | Ver dashboard, sensores y reportes (solo lectura) |
| **Operador** | Todo lo anterior + reconocer alertas, controlar actuadores |
| **Administrador** | Todo lo anterior + gestionar usuarios, sensores, reglas |

---

## 3. Dashboard Principal

El dashboard es la vista principal del sistema. Muestra el estado actual del invernadero en tiempo real.

### Tarjetas de Resumen

En la parte superior encontrará 4 tarjetas con los valores principales:

| Tarjeta | Descripción | Ejemplo |
|---------|-------------|---------|
| 🌡️ **Temperatura** | Temperatura promedio actual del invernadero | 25.3°C |
| 💧 **Humedad** | Humedad relativa promedio | 68.5% |
| ☀️ **Luminosidad** | Nivel de luz actual | 12,450 lux |
| 🚨 **Alertas** | Número de alertas activas | 3 |

Cada tarjeta incluye una comparación con el día anterior (▲ aumento / ▼ disminución).

### Gráficas de Tendencia

- **Temperatura y Humedad (24h):** Gráfica de líneas con las últimas 24 horas de datos.
- **CO₂ y Luminosidad:** Gráfica de barras con las lecturas del día actual.

Las gráficas se actualizan automáticamente cada 10 segundos.

### Estado de Sensores

Lista de todos los sensores conectados al gateway con:
- **Indicador de estado** (🟢 online, 🟡 warning, 🔴 offline).
- **Valor actual** de la última lectura.
- **Protocolo** y configuración de polling.

### Alertas Recientes

Lista de las últimas alertas con su severidad:
- 🔴 **Crítica** — Requiere acción inmediata.
- 🟡 **Advertencia** — Condición fuera de rango, monitorear.
- 🔵 **Info** — Notificación informativa.

---

## 4. Gestión de Sensores

### Ver Sensores

Navegue a **Sensores** en el menú lateral para ver todos los sensores del invernadero.

Cada tarjeta de sensor muestra:
- Nombre y tipo del sensor.
- Protocolo de comunicación (1-Wire, I2C, GPIO, UART, ADC).
- Valor actual con mini-gráfica de tendencia.
- Estado de conexión.

### Sensores Soportados

| Sensor | Medición | Rango | Precisión |
|--------|----------|-------|-----------|
| DS18B20 | Temperatura | −55°C a +125°C | ±0.5°C |
| DHT22 | Temp + Humedad | −40°C a +80°C / 0-100% HR | ±0.5°C / ±2% |
| BH1750 | Luminosidad | 1 – 65,535 lux | ±1 lux |
| Soil Moisture | Hum. Suelo | 0 – 100% | ±2% |
| MHZ-19C | CO₂ | 400 – 5,000 ppm | ±50 ppm |

### Rangos Óptimos para Invernadero

| Variable | Rango Óptimo | Zona de Alerta |
|----------|-------------|----------------|
| Temperatura | 18°C – 28°C | < 10°C ó > 35°C |
| Humedad Relativa | 60% – 80% | < 40% ó > 90% |
| Luminosidad | 10,000 – 30,000 lux | < 5,000 ó > 50,000 lux |
| CO₂ | 400 – 1,000 ppm | > 1,500 ppm |
| Humedad del Suelo | 50% – 80% | < 30% ó > 95% |

---

## 5. Centro de Alertas

### Ver Alertas

Navegue a **Alertas** en el menú lateral. Verá un resumen de:
- Alertas **activas** (requieren atención).
- Alertas **reconocidas** (en proceso).
- Alertas **resueltas** (cerradas).
- **Reglas** activas configuradas.

### Reconocer una Alerta

1. Localice la alerta activa en la lista.
2. Haga clic en **"Reconocer"**.
3. Opcionalmente, agregue un comentario describiendo la acción tomada.
4. La alerta pasa a estado "Reconocida".

### Crear una Regla de Alerta

1. Navegue a **Alertas** → **Reglas**.
2. Haga clic en **"+ Nueva Regla"**.
3. Configure los campos:
   - **Sensor:** Seleccione el sensor a monitorear.
   - **Condición:** Mayor que (>), Menor que (<), Igual (=).
   - **Umbral:** Valor numérico del límite.
   - **Duración:** Tiempo que debe mantenerse la condición antes de disparar (e.g., 5 minutos).
   - **Severidad:** Info, Advertencia o Crítica.
   - **Cooldown:** Tiempo mínimo entre alertas repetidas (e.g., 15 minutos).
4. Haga clic en **"Guardar"**.

### Canales de Notificación

| Canal | Configuración |
|-------|---------------|
| 📧 Email | Se configura en el perfil de usuario |
| 📱 Push | Requiere app móvil instalada |
| 💬 In-App | Siempre activo en el dashboard |
| 🔗 Webhook | Se configura en Administración → Integraciones |

---

## 6. Generación de Reportes

### Crear un Reporte

1. Navegue a **Reportes** en el menú lateral.
2. En el formulario "Generar Nuevo Reporte":
   - **Tipo:** Resumen Diario, Análisis Semanal, Reporte de Alertas, Comparativa.
   - **Período:** Seleccione el rango de fechas.
   - **Sensores:** Todos o selección específica.
   - **Formato:** PDF o Excel.
   - **Opciones:** Incluir gráficas, incluir alertas.
3. Haga clic en **"Generar Reporte"**.
4. El reporte se genera de forma asíncrona. Recibirá una notificación cuando esté listo.

### Descargar un Reporte

1. En la lista de "Reportes Recientes", busque el reporte con estado ✅ Completado.
2. Haga clic en **"Descargar"**.

### Tipos de Reporte

| Tipo | Contenido | Frecuencia Sugerida |
|------|-----------|-------------------|
| **Resumen Diario** | Promedios, máximos, mínimos y alertas del día | Diaria |
| **Análisis Semanal** | Tendencias, comparativas entre días | Semanal |
| **Reporte de Alertas** | Historial de alertas con acciones tomadas | Según necesidad |
| **Comparativa** | Comparación entre períodos o zonas | Mensual |
| **Calibración** | Estado y próximas fechas de calibración de sensores | Trimestral |

---

## 7. Control de Actuadores

> ⚙️ *Funcionalidad disponible en el roadmap.*

### Actuadores Soportados

| Actuador | Función | Control |
|----------|---------|---------|
| 💧 **Riego** | Sistema de riego por goteo | On/Off, programación horaria |
| 🌀 **Ventilación** | Ventiladores y extractores | On/Off, velocidad |
| 💡 **Iluminación** | Luces suplementarias | On/Off, intensidad |

### Control Manual

1. Navegue al actuador en el menú lateral (Riego, Ventilación o Iluminación).
2. Utilice el botón de encendido/apagado.
3. Confirme la acción.

### Automatización

Configure reglas de automatización basadas en lecturas de sensores:
- "Si temperatura > 30°C, encender ventilación."
- "Si humedad del suelo < 40%, activar riego por 10 minutos."
- "Si luminosidad < 5,000 lux después de las 8:00, encender iluminación."

---

## 8. Panel de Administración

*(Disponible solo para usuarios con rol Administrador)*

### Gestión de Usuarios

- **Agregar usuario:** Ingrese email, nombre, rol y contraseña temporal.
- **Editar usuario:** Modifique rol o estado (activo/inactivo).
- **Eliminar usuario:** Desactiva la cuenta (los datos se preservan por auditoría).

### Configuración del Gateway

- **Ver estado:** Online/Offline, última comunicación, versión de firmware.
- **Actualizar firmware:** Enviar actualización OTA al gateway.
- **Configurar sensores:** Ajustar intervalos de polling, umbrales, calibración.

### Configuración del Tenant

- **Branding:** Logotipo, colores, nombre de la organización.
- **Notificaciones:** Configuración de canales (email SMTP, webhooks).
- **Auditoría:** Ver historial de accesos y cambios en el sistema.

---

## 9. Preguntas Frecuentes

### ¿Con qué frecuencia se actualizan los datos?

Los datos se actualizan automáticamente cada 1-5 segundos dependiendo del sensor. El dashboard se refresca en tiempo real vía WebSocket.

### ¿Qué pasa si el invernadero pierde conexión a internet?

El gateway sigue operando de forma autónoma:
- Continúa leyendo sensores y almacenando datos localmente.
- Evalúa alertas localmente.
- Sincroniza automáticamente al recuperar conexión (hasta 72 horas de datos).

### ¿Cómo sé si un sensor necesita calibración?

En **Sensores** → **Detalle del Sensor**, revise la fecha de última calibración. El sistema genera alertas automáticas cuando se acerca la fecha de recalibración.

### ¿Puedo exportar mis datos?

Sí. Los datos se pueden exportar en formato CSV, JSON, PDF o Excel desde la sección de **Reportes** o desde el detalle de cada sensor.

### ¿Cuántos invernaderos puedo monitorear?

Cada gateway monitorea un invernadero (o zona). Puede agregar múltiples gateways a su cuenta para monitorear varios invernaderos desde un solo dashboard.

---

*Última actualización: Marzo 2026 · EchoSmart Dev Team*
