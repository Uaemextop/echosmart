# EchoSmart Kit de Producción — BOM, Precios y Ensamblaje

> Guía completa para la fabricación en masa del kit EchoSmart para invernaderos.

## 1. Descripción del Producto

**EchoSmart Kit** es un sistema de monitoreo ambiental inteligente para invernaderos que incluye:
- **Hardware**: Raspberry Pi 4 + sensores ambientales seleccionados
- **Software**: Gateway pre-instalado en microSD lista para usar
- **Conectividad**: Wi-Fi 802.11ac + Ethernet integrados
- **Sensores**: Temperatura, humedad, CO₂, luminosidad y humedad de suelo

---

## 2. Bill of Materials (BOM) — Por Kit

| # | Componente | Modelo | Cantidad | Precio Unit. (USD) | Subtotal |
|---|-----------|--------|----------|---------------------|----------|
| 1 | Raspberry Pi 4 Model B | 4GB RAM | 1 | $55.00 | $55.00 |
| 2 | Fuente de alimentación | 5V 3A USB-C oficial | 1 | $8.00 | $8.00 |
| 3 | MicroSD card | SanDisk 32GB Class A1 | 1 | $6.00 | $6.00 |
| 4 | Sensor temperatura | DS18B20 (impermeable) | 3 | $3.50 | $10.50 |
| 5 | Sensor temp+humedad | DHT22 / AM2302 | 3 | $4.50 | $13.50 |
| 6 | Sensor luminosidad | BH1750FVI módulo | 1 | $2.50 | $2.50 |
| 7 | Sensor humedad suelo | Capacitivo v1.2 | 3 | $3.00 | $9.00 |
| 8 | ADC | ADS1115 módulo 16-bit | 1 | $3.50 | $3.50 |
| 9 | Sensor CO₂ | MH-Z19C NDIR | 1 | $25.00 | $25.00 |
| 10 | Carcasa RPi | Caja ABS con ventilación | 1 | $8.00 | $8.00 |
| 11 | Cables jumper | 40-pin M-F, 20cm | 1 paquete | $3.00 | $3.00 |
| 12 | Resistencias | 4.7kΩ + 10kΩ surtido | 10 | $0.10 | $1.00 |
| 13 | Guía rápida | Impresa A5, color | 1 | $0.50 | $0.50 |
| 14 | Caja de empaque | Caja cartón personalizada | 1 | $2.00 | $2.00 |
| **Total BOM** | | | | | **$147.00** |

### Costos adicionales por kit

| Concepto | Costo |
|---------|-------|
| Mano de obra (ensamblaje + flash SD) | $5.00 |
| Licencia software (perpetua, 1 gateway) | $0 (open source) |
| Gastos de envío (promedio) | $8.00 |
| **Costo Total por Kit** | **$160.00** |

---

## 3. Estructura de Precios de Venta

| SKU | Plan | Precio | Incluye |
|-----|------|--------|---------|
| ES-KIT-BASIC | Basic | **$299 USD** | 1 RPi + 3 sensores temp + 1 sensor humedad |
| ES-KIT-STANDARD | Standard | **$449 USD** | Kit completo (BOM arriba) |
| ES-KIT-PRO | Pro | **$649 USD** | Kit Standard + 3 gateways + soporte 1 año |
| ES-SUB-CLOUD | Cloud SaaS | **$29/mes** | Dashboard cloud, alertas, reportes (por invernadero) |

**Margen bruto estimado** (Kit Standard): ~65%

---

## 4. Proceso de Ensamblaje (Masa)

### Paso 1 — Flash de MicroSD (producción masiva)

```bash
# Usar balena CLI para flash en línea de producción
balena local flash echosmart-gateway-v1.0.0-arm64.img --drive /dev/sdX
# O con rpi-imager CLI:
rpi-imager --cli echosmart-gateway-v1.0.0-arm64.img /dev/sdX
```

### Paso 2 — Instalación del .deb en SD

Alternativa al flash de imagen completa, instalar el .deb sobre Raspberry Pi OS Lite:

```bash
# En una RPi fresca con RPi OS Lite:
sudo apt update
sudo apt install -y ./echosmart-gateway_1.0.0_all.deb
```

### Paso 3 — Test de Calidad (QC)

```bash
# Ejecutar test de sensores antes de empacar
echosmart-gateway test-sensors
# Verificar salida: todos los sensores deben mostrar [OK]
```

### Paso 4 — Empaque

1. Insertar microSD en Raspberry Pi
2. Colocar en carcasa (tornillos M2.5)
3. Colocar en caja de empaque con:
   - Guía rápida impresa
   - Cable USB-C de alimentación
   - Cables jumper etiquetados
   - Tarjeta de garantía

---

## 5. Diagrama de Conexión de Sensores

```
Raspberry Pi 4 — Pinout de Conexión
=====================================

3.3V (Pin 1) ─────┬─── DS18B20 VCC (× 3)
                   └─── BH1750 VCC
5V (Pin 2) ────────┬─── DHT22 VCC (× 3)
                   ├─── ADS1115 VCC
                   └─── MH-Z19C VCC (5V!)
GND (Pin 6) ───────┬─── DS18B20 GND
                   ├─── DHT22 GND
                   ├─── BH1750 GND
                   ├─── ADS1115 GND
                   ├─── Sensor suelo GND (× 3)
                   └─── MH-Z19C GND

GPIO 4 (Pin 7) ─── DS18B20 DATA (con resistencia 4.7kΩ a 3.3V)
GPIO 17 (Pin 11) ─ DHT22 DATA (con resistencia 10kΩ a 3.3V)
GPIO 2/SDA (Pin 3) ─── BH1750 SDA + ADS1115 SDA
GPIO 3/SCL (Pin 5) ─── BH1750 SCL + ADS1115 SCL
GPIO 14/TX (Pin 8) ─── MH-Z19C RX
GPIO 15/RX (Pin 10) ── MH-Z19C TX

ADS1115 A0 ─── Sensor suelo 1
ADS1115 A1 ─── Sensor suelo 2
ADS1115 A2 ─── Sensor suelo 3
```

---

## 6. Garantía y Soporte

- **Garantía hardware**: 12 meses contra defectos de fabricación
- **Actualizaciones software**: OTA automáticas incluidas
- **Soporte técnico**: Email support@echosmart.io (respuesta < 24h)
- **Documentación**: https://docs.echosmart.io

---

*Última actualización: Marzo 2026 — EchoSmart Team*
