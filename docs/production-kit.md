# EchoSmart Kit — Production & Commercial Guide

> **Kit de monitoreo IoT para agricultura de precisión**  
> Raspberry Pi 4 + 5 sensores ambientales + Gateway EchoSmart pre-instalado

---

## Tabla de contenidos

1. [Descripción del producto](#descripción-del-producto)
2. [Bill of Materials (BOM)](#bill-of-materials-bom)
3. [Pricing y márgenes](#pricing-y-márgenes)
4. [Guía de ensamblaje](#guía-de-ensamblaje)
5. [Diagrama de conexiones](#diagrama-de-conexiones)
6. [QA Checklist pre-shipment](#qa-checklist-pre-shipment)
7. [Empaquetado y envío](#empaquetado-y-envío)
8. [Soporte y garantía](#soporte-y-garantía)

---

## Descripción del producto

El **EchoSmart Kit** es un sistema completo de monitoreo ambiental para invernaderos y cultivos de precisión. Incluye:

- **Hardware**: Raspberry Pi 4 + 5 sensores de temperatura, humedad, luz, suelo y CO₂
- **Software**: EchoSmart Gateway pre-instalado y configurado
- **Conectividad**: WiFi 2.4/5 GHz + Ethernet + Bluetooth 5.0
- **Almacenamiento**: MicroSD 32GB con sistema operativo pre-configurado
- **Autonomía offline**: Base de datos local SQLite para operación sin internet

---

## Bill of Materials (BOM)

### Componentes principales

| # | Componente | Modelo | Proveedor | Costo USD | Notas |
|---|-----------|--------|-----------|-----------|-------|
| 1 | Microcomputadora SBC | Raspberry Pi 4 Model B 2GB | RS Components / OKdo | $35.00 | 64-bit ARM Cortex-A72 |
| 2 | Almacenamiento | MicroSD 32GB Class 10 A1 | Samsung EVO+ | $8.00 | Mínimo 32GB, Class 10 recomendado |
| 3 | Sensor temperatura suelo | DS18B20 impermeable 1m | AliExpress / Digi-Key | $5.00 | 1-Wire, rango -55°C a +125°C |
| 4 | Sensor temp+humedad aire | DHT22 (AM2302) módulo | Mouser / Adafruit | $4.00 | ±0.5°C, ±2–5% HR |
| 5 | Sensor luz ambiental | BH1750FVI módulo I2C | AliExpress | $3.00 | 1–65535 lux, I2C 0x23/0x5C |
| 6 | Sensor humedad suelo cap. | Capacitive Soil v2.0 | AliExpress | $5.00 | Capacitivo (no corrosivo) |
| 7 | ADC 16-bit | ADS1115 módulo I2C | Adafruit / AliExpress | $7.00 | Para sensor suelo analógico |
| 8 | Sensor CO₂ | MH-Z19C UART | Winsen / Mouser | $25.00 | 0–5000 ppm, NDIR, UART 9600 |
| 9 | Fuente de alimentación | 5V 3A USB-C oficial RPi | Raspberry Pi Foundation | $12.00 | Oficial: evita under-voltage |
| 10 | Case + disipador | Raspberry Pi 4 Case con ventilador | AliExpress | $10.00 | Ventilación activa recomendada |
| 11 | Cables y componentes | Jumper wires + resistencias 4.7kΩ | Genérico | $5.00 | Resistencia pull-up DS18B20 |
| 12 | Packaging producto | Caja cartón + foam EVA | Imprenta local | $8.00 | Caja 25×20×12 cm |

### Resumen de costos

| Concepto | Costo USD |
|----------|-----------|
| **BOM Total (1 unidad)** | **$127.00** |
| Mano de obra ensamblaje (15 min × $20/hr) | $5.00 |
| Overhead y logística (~8%) | $10.56 |
| **Costo total por unidad** | **~$142.56** |

### Pricing sugerido

| Canal | Precio USD | Margen bruto |
|-------|-----------|--------------|
| **Venta directa** (web, B2C) | **$349.00** | ~59% |
| **Distribuidor** (mayoreo 10+ unidades) | **$249.00** | ~43% |
| **Revendedor** (marketplace) | **$299.00** | ~52% |

> **Nota de mercado**: Kits equivalentes (e.g., AgroSense Pro, FarmBot Express) se venden entre $350–$800 USD. El posicionamiento a $349 es competitivo.

### Proveedores alternativos

| Componente | Proveedor A | Proveedor B | Proveedor C |
|-----------|-------------|-------------|-------------|
| RPi 4 2GB | [RS Components](https://uk.rs-online.com) | [Digi-Key](https://digikey.com) | [Newark](https://newark.com) |
| DHT22 | [Adafruit #385](https://adafruit.com) | [SparkFun](https://sparkfun.com) | AliExpress |
| MH-Z19C | [Winsen oficial](https://winsen-sensor.com) | [Mouser](https://mouser.com) | AliExpress |
| ADS1115 | [Adafruit #1085](https://adafruit.com) | [Digi-Key](https://digikey.com) | AliExpress |
| BH1750 | [Mouser](https://mouser.com) | AliExpress | [JLCPCB](https://jlcpcb.com) |

---

## Guía de ensamblaje

### Herramientas necesarias

- Destornillador Phillips #0 y #1
- Cortacables / pelacables
- Multímetro digital
- Laptop con lector de MicroSD

### Paso 1 — Flash de MicroSD

```bash
# En laptop de producción:
# 1. Insertar MicroSD (32GB) en lector
# 2. Descargar imagen EchoSmart pre-configurada:
wget https://releases.echosmart.io/gateway/echosmart-gateway-v1.0.0-arm64.img.xz

# 3. Flash con Raspberry Pi Imager o dd:
xzcat echosmart-gateway-v1.0.0-arm64.img.xz | \
    sudo dd of=/dev/sdX bs=4M status=progress conv=fsync

# 4. Verificar checksum:
sha256sum echosmart-gateway-v1.0.0-arm64.img.xz
# (comparar con SHA256 en releases.echosmart.io)
```

### Paso 2 — Ensamblaje del case

1. Insertar la RPi 4 en la base del case
2. Conectar el disipador de cobre a la CPU (pasta térmica incluida)
3. Instalar el ventilador (conectar a GPIO pins 4 y 6: 5V y GND)
4. Cerrar la tapa del case

### Paso 3 — Conexión de sensores

#### DS18B20 (temperatura suelo) — 1-Wire

```
DS18B20          RPi 4
VCC (rojo)    → Pin 1 (3.3V)
GND (negro)   → Pin 6 (GND)
DATA (amarillo)→ Pin 7 (GPIO4)
                  + Resistencia 4.7kΩ entre DATA y VCC
```

#### DHT22 (temperatura + humedad aire) — GPIO

```
DHT22            RPi 4
Pin 1 (VCC)   → Pin 2 (5V)
Pin 2 (DATA)  → Pin 11 (GPIO17)
Pin 4 (GND)   → Pin 9 (GND)
```

#### BH1750 (luz ambiental) — I2C

```
BH1750           RPi 4
VCC           → Pin 1 (3.3V)
GND           → Pin 9 (GND)
SCL           → Pin 5 (GPIO3/SCL)
SDA           → Pin 3 (GPIO2/SDA)
ADDR          → GND (I2C address 0x23)
```

#### ADS1115 + Sensor suelo — I2C

```
ADS1115          RPi 4
VDD           → Pin 1 (3.3V)
GND           → Pin 6 (GND)
SCL           → Pin 5 (GPIO3/SCL)  ← mismo bus que BH1750
SDA           → Pin 3 (GPIO2/SDA)  ← mismo bus que BH1750
ADDR          → GND (I2C address 0x48)

Sensor suelo capacitivo:
VCC           → ADS1115 VDD
GND           → ADS1115 GND
AOUT          → ADS1115 A0
```

#### MH-Z19C (CO₂) — UART

```
MH-Z19C          RPi 4
VCC (5V)      → Pin 2 (5V)
GND           → Pin 14 (GND)
TX            → Pin 10 (GPIO15/RXD) ← RPi recibe
RX            → Pin 8  (GPIO14/TXD) ← RPi transmite
```

### Paso 4 — Insertar MicroSD y primer arranque

1. Insertar MicroSD flasheada en la ranura de la RPi
2. Conectar cable Ethernet (recomendado para primer arranque)
3. Conectar fuente USB-C de 5V 3A
4. Esperar 2 minutos al primer arranque

### Paso 5 — Configuración de red (WiFi)

```bash
# Conectar por SSH (usuario: echosmart, password: echosmart)
# Cambiar por IP local de la RPi (visible en router o con scanner)
ssh echosmart@echosmart-gateway.local

# Configurar WiFi
sudo nmtui
# → Activate a connection → WiFi → ingresar SSID y contraseña
```

### Paso 6 — Configuración del gateway

```bash
# Editar configuración
sudo nano /etc/echosmart/gateway.env

# Configurar:
# GATEWAY_ID=gw-<numero-serial>
# CLOUD_API_URL=https://api.echosmart.io
# CLOUD_API_KEY=<api-key-del-cliente>

# Reiniciar servicio
sudo systemctl restart echosmart-gateway

# Verificar funcionamiento
sudo journalctl -u echosmart-gateway -f
```

---

## Diagrama de conexiones

```
                    RASPBERRY PI 4
                  ┌─────────────────┐
  3.3V ──────────►│ Pin 1  │ Pin 2  │◄────── 5V
                  │        │        │
    DS18B20 ─────►│ Pin 7  │ Pin 8  │►────── MH-Z19C TX→RPi RX
  (GPIO4, 1-Wire) │        │        │
                  │ Pin 9  │ Pin 10 │◄────── MH-Z19C RX←RPi TX
     BH1750  ─────►│ Pin 3  │ Pin 5  │◄────── BH1750 SCL
     ADS1115 ─────►│(SDA)   │(SCL)   │◄────── ADS1115 SCL
                  │        │        │
     DHT22  ──────►│ Pin 11 │        │
   (GPIO17)       └─────────────────┘
```

---

## QA Checklist pre-shipment

Completar para **cada unidad** antes del envío. Usar script automatizado:

```bash
# En la RPi del kit (como usuario echosmart):
echosmart-sysinfo --pretty
echosmart-sensor-read --simulate ds18b20
echosmart-sensor-read --simulate dht22
echosmart-sensor-read --simulate bh1750
echosmart-sensor-read --simulate soil
echosmart-sensor-read --simulate mhz19c
sudo systemctl status echosmart-gateway
```

### Checklist manual

#### Hardware

- [ ] RPi 4 arranca correctamente (LED verde parpadeando)
- [ ] MicroSD correctamente insertada y accesible
- [ ] Case montado correctamente, sin piezas sueltas
- [ ] Ventilador girando al encender
- [ ] Todos los cables de sensores correctamente conectados
- [ ] No hay cortocircuitos visibles en la placa

#### Software

- [ ] `echosmart-sysinfo` ejecuta y devuelve JSON válido
- [ ] `echosmart-sensor-read --simulate ds18b20` retorna temperatura JSON
- [ ] `echosmart-sensor-read --simulate dht22` retorna temperatura y humedad JSON
- [ ] `echosmart-sensor-read --simulate bh1750` retorna lux JSON
- [ ] `echosmart-sensor-read --simulate soil` retorna humedad suelo JSON
- [ ] `echosmart-sensor-read --simulate mhz19c` retorna CO₂ ppm JSON
- [ ] `systemctl status echosmart-gateway` muestra `active (running)`
- [ ] Logs del gateway sin errores críticos
- [ ] Gateway envía datos a la nube (verificar en dashboard)

#### Sensores reales (con hardware conectado)

- [ ] DS18B20: temperatura razonable (18–35°C para temp. ambiente)
- [ ] DHT22: temperatura y humedad dentro de rango
- [ ] BH1750: lectura de luz > 0 lux
- [ ] Suelo: lectura de ADC dentro de rango (voltage entre 0.8–2.5V)
- [ ] MH-Z19C: CO₂ entre 400–600 ppm en exterior (planta calentada ≥ 20 min)

#### Red y conectividad

- [ ] WiFi conectado (si configurado)
- [ ] Ethernet funcional
- [ ] Acceso SSH funcional
- [ ] Gateway alcanza `api.echosmart.io` (ping o curl)

---

## Empaquetado y envío

### Contenido de la caja

| Ítem | Cantidad |
|------|----------|
| Raspberry Pi 4 Model B 2GB en case | 1 |
| MicroSD 32GB (pre-flasheada) | 1 |
| Cable USB-C de alimentación (1m) | 1 |
| Fuente de alimentación 5V 3A USB-C | 1 |
| Sensor DS18B20 impermeable (cable 1m) | 1 |
| Módulo DHT22 con pines | 1 |
| Módulo BH1750 | 1 |
| Sensor humedad suelo capacitivo | 1 |
| Módulo ADS1115 | 1 |
| Sensor MH-Z19C con cables | 1 |
| Kit de cables jumper (20 cm, M-F y M-M) | 1 |
| Resistencia 4.7kΩ (para DS18B20) | 3 |
| Guía rápida de inicio (impresa) | 1 |
| Tarjeta de soporte con QR code | 1 |

### Especificaciones de empaquetado

- **Caja exterior**: Cartón corrugado de doble pared, 25×20×12 cm
- **Protección interior**: Foam EVA cortado a medida para cada componente
- **Peso total**: ~680g con caja
- **Frágil**: Sí — marcar con etiquetas "FRÁGIL" y "NO APILAR"

### Envío

| Destino | Carrier | Tiempo | Costo aprox. |
|---------|---------|--------|--------------|
| Nacional (MX) | DHL Express / Estafeta | 1–3 días | $15–25 USD |
| USA/Canadá | FedEx International | 3–5 días | $35–50 USD |
| Europa | DHL International | 5–8 días | $45–65 USD |
| Resto del mundo | UPS Worldwide | 7–14 días | $55–80 USD |

---

## Soporte y garantía

- **Garantía de hardware**: 12 meses contra defectos de fabricación
- **Soporte técnico**: soporte@echosmart.io — respuesta en 24–48h hábiles
- **Documentación**: https://echosmart.io/docs
- **Comunidad**: https://community.echosmart.io
- **Actualizaciones de software**: OTA automáticas vía repositorio APT privado

---

*Documento generado para EchoSmart v1.0.0 — Última actualización: 25 de marzo de 2026*
