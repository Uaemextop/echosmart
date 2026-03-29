# EchoSmart — Kit de Producción

Guía para la fabricación, ensamblaje y comercialización del kit EchoSmart.

---

## 1. BOM (Bill of Materials)

| # | Componente | Especificación | Proveedor | Costo (USD) |
|---|-----------|----------------|-----------|-------------|
| 1 | Raspberry Pi 4B | 4 GB RAM, arm64 | Distribuidor oficial | $55 |
| 2 | Fuente de alimentación | USB-C 5V 3A | Amazon / AliExpress | $8 |
| 3 | microSD pre-grabada | 32 GB Class 10, imagen EchoSmart | Kingston / SanDisk | $7 |
| 4 | DS18B20 | Encapsulado impermeable, cable 1 m | AliExpress | $2 |
| 5 | DHT22 (AM2302) | Módulo con resistencia integrada | AliExpress | $3 |
| 6 | BH1750FVI | Módulo breakout I2C | AliExpress | $2 |
| 7 | Sensor suelo capacitivo | v1.2, salida analógica | AliExpress | $2 |
| 8 | ADS1115 | ADC 16-bit, 4 canales, I2C | AliExpress | $3 |
| 9 | MH-Z19C | CO₂ NDIR, 0-5000 ppm, UART | AliExpress | $18 |
| 10 | Carcasa Raspberry Pi | Ventilada, compatible 4B | AliExpress | $5 |
| 11 | Kit de cableado | Protoboard + jumpers + resistencias 4.7kΩ y 10kΩ | Local / Amazon | $5 |
| 12 | Empaque del kit | Caja + manual impreso + sticker GPIO | Imprenta local | $8 |
| | **COGS Total** | | | **~$118** |

---

## 2. Precios de Venta

| Plan | Contenido | Precio |
|------|----------|--------|
| **Kit Básico** | Hardware completo + microSD con imagen + manual impreso | $299 USD |
| **Kit Pro** | Kit Básico + 1 año soporte técnico + acceso dashboard cloud | $449 USD |
| **Enterprise** | 10× Kit Pro + instalación on-site + SLA 24/7 | Cotización |

**Margen bruto Kit Básico**: ($299 − $118) / $299 = **60.5 %**

---

## 3. Contenido del Kit

```
┌──────────────────────────────────────────────┐
│  Caja EchoSmart Kit                          │
│                                              │
│  ┌────────────┐  ┌─────────────────────────┐ │
│  │ Raspberry   │  │ Bolsa de sensores:      │ │
│  │ Pi 4B       │  │  • DS18B20              │ │
│  │ + carcasa   │  │  • DHT22                │ │
│  │ + fuente    │  │  • BH1750               │ │
│  │ + microSD   │  │  • Soil sensor + ADS1115│ │
│  │             │  │  • MH-Z19C              │ │
│  └────────────┘  └─────────────────────────┘ │
│                                              │
│  ┌────────────┐  ┌─────────────────────────┐ │
│  │ Protoboard  │  │ Manual de inicio rápido │ │
│  │ + cables    │  │ + sticker GPIO          │ │
│  │ + resist.   │  │ + tarjeta de registro   │ │
│  └────────────┘  └─────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## 4. Proceso de Ensamblaje

### 4.1 Preparación de microSD (batch)

```bash
# Descargar la imagen ISO del gateway
wget https://releases.echosmart.io/echosmart-gateway-v1.0.0-arm64.img.xz

# Flashear con dd (o Balena Etcher para lotes pequeños)
xzcat echosmart-gateway-v1.0.0-arm64.img.xz | \
  sudo dd of=/dev/sdX bs=4M status=progress
```

Para lotes grandes (>50 unidades), usar un duplicador de tarjetas SD.

### 4.2 Ensamblaje Físico (por unidad)

1. Insertar Raspberry Pi en carcasa
2. Conectar fuente de alimentación (no encender aún)
3. Insertar microSD pre-grabada
4. Empaquetar sensores en bolsa antiestática
5. Incluir protoboard, cables y resistencias
6. Incluir manual impreso y sticker GPIO
7. Colocar todo en la caja del kit
8. Etiquetar con número de serie (formato: `ES-YYYYMM-XXXX`)

### 4.3 Control de Calidad (QA)

**Cada unidad se prueba antes de empaquetar:**

```bash
# 1. Encender la Raspberry Pi (boot < 60 s)
# 2. Verificar binarios
echosmart-sysinfo              # → JSON con CPU temp, memoria, disco
echosmart-sensor-read ds18b20 --simulate   # → JSON con temperatura
echosmart-gateway --simulate --once        # → ciclo completo OK

# 3. Verificar servicio systemd
systemctl status echosmart-gateway         # → loaded + inactive (waiting for setup)

# 4. Verificar wizard de configuración
echosmart-gateway-setup                    # → genera /etc/echosmart/gateway.env
```

**Criterios de PASS:**
- Boot completo en < 60 segundos
- Los 3 binarios retornan JSON válido
- El servicio systemd se carga correctamente
- El wizard escribe la configuración

---

## 5. Logística

### 5.1 Envío

| Zona | Método | Tiempo | Costo estimado |
|------|--------|--------|----------------|
| Nacional (México) | Fedex / Estafeta | 3-5 días | $10-15 USD |
| EE.UU. / Canadá | DHL Express | 5-7 días | $25-35 USD |
| Internacional | DHL / UPS | 7-14 días | $35-50 USD |

### 5.2 Garantía

- **Hardware**: 1 año contra defectos de fabricación
- **Software**: actualizaciones gratuitas de seguridad vía `apt upgrade`
- **Soporte**: email + chat (Kit Pro y Enterprise)

---

## 6. Actualización del Software en Campo

El cliente actualiza el software ejecutando:

```bash
# Descargar la última versión del .deb
wget https://releases.echosmart.io/echosmart-gateway_1.1.0-1_arm64.deb

# Instalar (automáticamente reinicia el servicio)
sudo dpkg -i echosmart-gateway_1.1.0-1_arm64.deb
```

O, si se configura el repositorio APT:

```bash
sudo apt update && sudo apt upgrade echosmart-gateway
```

---

*Volver al [Índice de Documentación](README.md)*
