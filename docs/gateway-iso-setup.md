# EchoSmart — ISO del Gateway Raspberry Pi: Guía de Instalación

Guía para instalar y configurar un gateway EchoSmart en Raspberry Pi usando la imagen personalizada. El usuario final solo necesita flashear la microSD, conectar los sensores, encender el RPi, y se conecta automáticamente al servidor.

---

## 1. Requisitos

### Hardware

| Componente | Especificación |
|------------|---------------|
| Raspberry Pi | 3B+ / 4B / 5 (2GB+ RAM) |
| microSD | 16GB+ Class 10 (recomendado 32GB) |
| Fuente alimentación | 5V 3A USB-C (oficial) |
| Conectividad | Ethernet (recomendado) o WiFi |
| Sensores | Kit EchoSmart (5 sensores) |

### Software en tu PC

- [Balena Etcher](https://balena.io/etcher) o [Raspberry Pi Imager](https://www.raspberrypi.com/software/)

---

## 2. Instalación

### 2.1 Descargar la Imagen

```bash
# Descargar desde GitHub Releases
wget https://github.com/Uaemextop/echosmart/releases/latest/download/echosmart-gateway-arm64.img.xz

# Verificar integridad
sha256sum echosmart-gateway-arm64.img.xz
```

### 2.2 Flashear la microSD

1. Abrir **Balena Etcher**
2. Seleccionar `echosmart-gateway-arm64.img.xz`
3. Seleccionar la microSD como destino
4. Click en **Flash!**
5. Esperar (~5 minutos)

### 2.3 Primer Arranque

1. Insertar microSD en el Raspberry Pi
2. Conectar cable Ethernet (recomendado) o configurar WiFi
3. Conectar alimentación
4. Esperar ~60 segundos al primer boot
5. El sistema expande el filesystem y configura el hardware automáticamente

---

## 3. Configuración Inicial

### Opción A: Configuración por Web (Recomendada)

1. Desde cualquier PC en la misma red, abrir: `http://echosmart-gw-XXXX.local:8080`
   (donde XXXX son los últimos 4 dígitos de la MAC address)
2. Completar el wizard de configuración:

```
╔══════════════════════════════════════════════╗
║  🌱 EchoSmart Gateway Setup                 ║
╚══════════════════════════════════════════════╝

Paso 1/3: Nombre del Gateway
  (ej: invernadero-norte-01): _

Paso 2/3: Servidor EchoSmart
  URL del servidor: https://api.echosmart.io
  API Key: ES-GW-xxxxxxxxxxxx
  (La API Key se genera en el dashboard web del servidor)

Paso 3/3: Red WiFi (opcional)
  SSID: _
  Contraseña: _
```

### Opción B: Configuración por SSH

```bash
ssh echosmart@echosmart-gw-XXXX.local
# Contraseña por defecto: echosmart (se pide cambiar en primer login)

# Ejecutar wizard
echosmart-gateway-setup
```

### Opción C: Configuración por archivo

Antes de insertar la SD en el RPi, crear un archivo `echosmart-config.txt` en la partición `boot`:

```ini
[gateway]
name=invernadero-norte-01
server_url=https://api.echosmart.io
api_key=ES-GW-xxxxxxxxxxxx

[wifi]
ssid=MiRedWiFi
password=mi_contraseña

[network]
mode=dhcp
# mode=static
# ip=192.168.1.100
# gateway=192.168.1.1
# dns=8.8.8.8
```

---

## 4. Conexión de Sensores

### Diagrama de Conexión

```
Raspberry Pi GPIO Header
═══════════════════════════════════════

         3.3V  [1] [2]  5V ──────── MH-Z19C VCC
  BH1750 SDA ─ [3] [4]  ── GPIO4 ── DS18B20 DATA
  BH1750 SCL ─ [5] [6]  GND ─┬───── DS18B20 GND
              [7] [8]  TX ──┘      ┌ MH-Z19C RX
              [9] [10] RX ─────────┘ MH-Z19C TX
         GND ─[11][12] GPIO17 ───── DHT22 DATA
             [13][14] GND ──────── MH-Z19C GND
             ...
  ADS1115 SDA─[3]  (compartido con BH1750)
  ADS1115 SCL─[5]  (compartido con BH1750)
  
  Sensor Suelo ──── ADS1115 Canal A0
```

### Conexión Paso a Paso

| # | Sensor | Pin RPi | Notas |
|---|--------|---------|-------|
| 1 | **DS18B20** (Temp) | GPIO4 + 3.3V + GND | Agregar resistencia 4.7kΩ entre DATA y 3.3V |
| 2 | **DHT22** (Temp+Hum) | GPIO17 + 3.3V + GND | Resistencia 10kΩ pull-up (si no incluida en módulo) |
| 3 | **BH1750** (Luz) | SDA(GPIO2) + SCL(GPIO3) + 3.3V + GND | Bus I2C, dirección 0x23 |
| 4 | **ADS1115** (ADC) | SDA(GPIO2) + SCL(GPIO3) + 3.3V + GND | Bus I2C compartido, dirección 0x48 |
| 5 | **Soil Moisture** | → Canal A0 del ADS1115 | VCC a 3.3V |
| 6 | **MH-Z19C** (CO₂) | TX→RX(GPIO15), RX→TX(GPIO14) + 5V + GND | ⚠️ Alimentar a 5V (no 3.3V) |

> ⚠️ **IMPORTANTE**: Verificar todas las conexiones ANTES de encender. Un cable incorrecto puede dañar el sensor o el RPi.

---

## 5. Verificación

Una vez configurado y con sensores conectados:

### Verificar desde el Gateway

```bash
ssh echosmart@echosmart-gw-XXXX.local

# Estado del servicio
systemctl status echosmart-gateway

# Ver lecturas en tiempo real
echosmart-gw status

# Resultado esperado:
# ╔═══════════════════════════════════════╗
# ║  Gateway: invernadero-norte-01       ║
# ║  Servidor: ✅ Conectado              ║
# ║  Sensores:                           ║
# ║    🌡️ DS18B20:  24.5°C  ✅          ║
# ║    💧 DHT22:    62% RH   ✅          ║
# ║    ☀️ BH1750:   15200 lux ✅         ║
# ║    🌱 Soil:     65%      ✅          ║
# ║    🏭 MH-Z19C:  485 ppm  ✅         ║
# ╚═══════════════════════════════════════╝
```

### Verificar desde el Dashboard Web

1. Abrir `https://app.echosmart.io` (o el dominio del servidor)
2. Login con cuenta de administrador
3. Ir a Gateways → El gateway debe aparecer como "Online"
4. Ir a Dashboard → Las lecturas deben mostrarse en tiempo real

---

## 6. Gestión del Gateway

### Comandos Locales

```bash
# Estado completo
echosmart-gw status

# Ver logs
echosmart-gw logs

# Reiniciar servicio
echosmart-gw restart

# Actualizar software
echosmart-gw update

# Diagnóstico completo
echosmart-gw diagnostics

# Recalibrar un sensor
echosmart-gw calibrate ds18b20
```

### Gestión Remota (desde el Dashboard)

- **Reiniciar**: Dashboard → Gateways → [gateway] → Reiniciar
- **Actualizar**: Dashboard → Gateways → [gateway] → Actualizar firmware
- **Configurar**: Dashboard → Gateways → [gateway] → Configuración (intervalo polling, sensores)
- **Diagnóstico**: Dashboard → Gateways → [gateway] → Diagnóstico

---

## 7. Operación Offline

Si el gateway pierde conexión al servidor:

1. Las lecturas se almacenan localmente en SQLite (hasta 7 días)
2. El LED parpadea rápido indicando desconexión
3. El gateway intenta reconectar automáticamente (backoff exponencial)
4. Al reconectar, sincroniza TODOS los datos acumulados
5. El servidor registra el período de desconexión

---

## 8. Resolución de Problemas

| Problema | Solución |
|----------|----------|
| No detecta sensores | Verificar conexiones físicas. Ejecutar `i2cdetect -y 1` para I2C |
| No conecta al servidor | Verificar URL y API key. Verificar conectividad: `curl https://api.echosmart.io/health` |
| Lecturas incorrectas | Ejecutar `echosmart-gw calibrate [sensor]` |
| Gateway no arranca | Verificar fuente de alimentación (5V 3A). Ver logs: `journalctl -u echosmart-gateway` |
| WiFi no conecta | Verificar SSID y contraseña. Usar Ethernet como alternativa |

---

*Volver al [Índice de Documentación](README.md)*
