# EchoSmart — Kit de Producción y Guía Comercial

> Guía completa para ensamblar, empaquetar y vender el kit EchoSmart de monitoreo de invernaderos.

---

## 1. Descripción del Producto

**EchoSmart Kit** es un paquete llave en mano de monitoreo ambiental para invernaderos. El usuario final recibe hardware, software pre-instalado, y documentación impresa — todo listo para conectar y operar en minutos.

### Propuesta de valor

| Diferenciador | Detalle |
|---------------|---------|
| **Plug-and-play** | MicroSD pre-flasheada, software pre-configurado |
| **5 parámetros** | Temperatura, humedad relativa, luminosidad, humedad de suelo, CO₂ |
| **Edge computing** | Funciona offline, almacena datos localmente en SQLite |
| **Cloud ready** | Sincronización automática con el backend EchoSmart |
| **Código abierto** | MIT license, extensible por el usuario |

---

## 2. Bill of Materials (BOM) — Kit Básico

| # | Componente | Modelo / Especificación | Cant. | Costo aprox. (USD) |
|---|-----------|------------------------|-------|---------------------|
| 1 | Raspberry Pi | 4 Model B — 4 GB RAM | 1 | $55.00 |
| 2 | Fuente de alimentación | USB-C 5V 3A oficial RPi | 1 | $8.00 |
| 3 | MicroSD | 32 GB clase 10 — pre-flasheada | 1 | $7.00 |
| 4 | Sensor de temperatura | DS18B20 encapsulado impermeable | 1 | $2.50 |
| 5 | Sensor temp + humedad | DHT22 / AM2302 | 1 | $3.50 |
| 6 | Sensor de luz | BH1750FVI módulo breakout | 1 | $2.00 |
| 7 | Sensor de suelo | Capacitivo v1.2 | 1 | $1.50 |
| 8 | ADC | ADS1115 16-bit 4 canales | 1 | $3.00 |
| 9 | Sensor de CO₂ | MH-Z19C NDIR | 1 | $18.00 |
| 10 | Resistencias | 4.7 kΩ (1-Wire) + 10 kΩ (DHT22) | 2 | $0.20 |
| 11 | Cables jumper | Dupont F-F 20 cm | 20 | $1.50 |
| 12 | Carcasa RPi | Con ventilación, sin ventilador | 1 | $5.00 |
| 13 | Cable Ethernet | Cat5e 1 m (opcional, incluido) | 1 | $1.00 |
| | | | **Total** | **~$108.20** |

### Variantes de kit

| Kit | Incluye | Precio sugerido |
|-----|---------|-----------------|
| **Starter** | RPi + DS18B20 + DHT22 + BH1750 | ~$85 |
| **Standard** | Starter + SoilMoisture + ADS1115 | ~$95 |
| **Pro** | Standard + MH-Z19C (CO₂) | ~$115 |
| **Enterprise** | Pro × 3 nodos + servidor pre-configurado | Cotización |

---

## 3. Diagrama de Conexión de Sensores

```
Raspberry Pi 4 GPIO Header
─────────────────────────────────────────────────
Pin 1  (3.3V) ──────┬─── BH1750 VCC
Pin 2  (5V)   ──────┬─── MH-Z19C Vin
Pin 3  (SDA)  ──────┼─── BH1750 SDA ─── ADS1115 SDA
Pin 4  (5V)   ──────┘
Pin 5  (SCL)  ──────┼─── BH1750 SCL ─── ADS1115 SCL
Pin 6  (GND)  ──────┴─── GND común todos los sensores
Pin 7  (GPIO4)──────┬─── DS18B20 DATA
                    └─── R 4.7kΩ ─── Pin 1 (3.3V)
Pin 11 (GPIO17)─────┬─── DHT22 DATA
                    └─── R 10kΩ ─── Pin 1 (3.3V)
Pin 8  (TX)   ──────────── MH-Z19C RX
Pin 10 (RX)   ──────────── MH-Z19C TX

ADS1115 A0 ─── Sensor de humedad de suelo (señal)
ADS1115 VDD ── 3.3V
ADS1115 GND ── GND
ADS1115 ADDR ─ GND (dirección 0x48)
```

---

## 4. Proceso de Flasheo de MicroSD (Línea de Producción)

### 4.1 Herramienta recomendada

Para producción en masa, usar **Balena Etcher CLI** o `dd`:

```bash
# Descargar la imagen pre-compilada
wget https://github.com/Uaemextop/echosmart/releases/latest/download/echosmart-gateway-v1.0.0-arm64.img.xz

# Flashear (reemplazar /dev/sdX con la SD)
xzcat echosmart-gateway-v1.0.0-arm64.img.xz | sudo dd of=/dev/sdX bs=4M status=progress
sync
```

### 4.2 Imagen pre-configurada

La imagen del gateway incluye:

- Raspberry Pi OS Lite 64-bit (Bookworm)
- Python 3.11 + virtualenv con dependencias pre-instaladas
- Paquete `echosmart-gateway` v1.0.0 pre-instalado
- Interfaces habilitadas: I2C, 1-Wire, UART
- Servicio systemd habilitado
- Script de primer boot (`echosmart-gateway-setup`)

---

## 5. Flujo de Producción

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ 1. Flashear  │────▶│ 2. Ensamblar │────▶│ 3. Test QA  │
│    microSD   │     │    hardware  │     │   rápido    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                    ┌──────────────┐     ┌──────▼──────┐
                    │ 5. Enviar    │◀────│ 4. Empacar  │
                    │    cliente   │     │    kit      │
                    └──────────────┘     └─────────────┘
```

### 5.1 Test QA rápido (3 minutos por unidad)

```bash
# 1. Encender RPi con SD flasheada y sensores conectados
# 2. Esperar boot (~30 s)
# 3. Desde otra máquina en la misma red:

ssh pi@echosmart-gw.local "echosmart-gateway test-sensors"
# Debe mostrar lecturas de todos los sensores en modo simulación

ssh pi@echosmart-gw.local "echosmart-gateway status"
# Debe mostrar ID, versión, y configuración
```

### 5.2 Contenido de la caja

| Ítem | Tipo |
|------|------|
| Raspberry Pi 4 con carcasa | Hardware |
| Fuente 5V 3A USB-C | Hardware |
| MicroSD pre-flasheada | Hardware+Software |
| Bolsa de sensores + cables + resistencias | Hardware |
| Guía rápida de instalación (1 hoja, a color) | Impreso |
| Diagrama de conexiones (1 hoja, a color) | Impreso |
| Tarjeta con QR a documentación online | Impreso |
| Sticker EchoSmart | Branding |

---

## 6. Instalación alternativa via `.deb`

Para usuarios que ya tienen un Raspberry Pi con Raspberry Pi OS:

```bash
# Descargar el paquete .deb más reciente
wget https://github.com/Uaemextop/echosmart/releases/latest/download/echosmart-gateway_1.0.0-1_all.deb

# Instalar
sudo dpkg -i echosmart-gateway_1.0.0-1_all.deb
sudo apt-get install -f   # Resolver dependencias

# Configurar
sudo echosmart-gateway-setup

# Verificar
echosmart-gateway status
systemctl status echosmart-gateway
```

---

## 7. Actualización OTA

Los gateways desplegados pueden actualizarse remotamente:

```bash
# En el gateway (manual)
sudo apt-get update
sudo apt-get install echosmart-gateway

# O desde el servidor (via MQTT)
# El servidor envía comando: echosmart/gw/{id}/update
# El gateway descarga el .deb, instala, y reinicia el servicio
```

---

## 8. Soporte y Garantía

| Aspecto | Detalle |
|---------|---------|
| **Garantía hardware** | 12 meses contra defectos de fábrica |
| **Soporte software** | Actualizaciones gratuitas por 24 meses |
| **Canal de soporte** | support@echosmart.io |
| **Documentación** | https://github.com/Uaemextop/echosmart/docs |
| **Comunidad** | GitHub Issues + Discussions |

---

## 9. Estructura de Precios Sugerida

| Concepto | Costo | Precio venta | Margen |
|----------|-------|-------------|--------|
| Kit Pro (hardware) | $108 | $199 | 84% |
| Suscripción cloud (mes) | — | $9.99/mes | — |
| Soporte premium (año) | — | $99/año | — |
| Kit Enterprise (×3 nodos) | $324 | $549 | 69% |

---

*Última actualización: Marzo 2026*
