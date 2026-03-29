# EchoSmart — Production Kit

Guía para ensamblar, producir y vender el kit de monitoreo ambiental EchoSmart para invernaderos.

---

## Bill of Materials (BOM)

### Kit Básico — 1 Zona

| # | Componente | Modelo | Cantidad | Precio Est. (USD) |
|---|-----------|--------|----------|--------------------|
| 1 | Computadora de borde | Raspberry Pi 4B (4 GB) | 1 | $55.00 |
| 2 | Fuente de alimentación | USB-C 5V 3A oficial | 1 | $8.00 |
| 3 | Tarjeta microSD | 32 GB Clase 10 A1 | 1 | $7.00 |
| 4 | Sensor de temperatura | DS18B20 (impermeable) | 1 | $3.50 |
| 5 | Sensor de temp. + humedad | DHT22 / AM2302 | 1 | $4.00 |
| 6 | Sensor de luz | BH1750 (módulo GY-302) | 1 | $2.50 |
| 7 | Sensor de humedad de suelo | Capacitivo v1.2 | 1 | $2.00 |
| 8 | Convertidor ADC | ADS1115 (16-bit I2C) | 1 | $3.50 |
| 9 | Sensor de CO₂ | MH-Z19C (NDIR) | 1 | $18.00 |
| 10 | Resistencia pull-up | 4.7 kΩ (para DS18B20) | 1 | $0.10 |
| 11 | Cables jumper | Macho-hembra, 20 cm | 20 | $2.00 |
| 12 | Carcasa protectora | Caja IP65 para exterior | 1 | $6.00 |
| 13 | Cable Ethernet | Cat 5e, 1 m | 1 | $1.50 |
| — | **Subtotal componentes** | | | **$113.10** |

### Kit Profesional — 3 Zonas

Incluye todo lo del Kit Básico más sensores adicionales para cubrir 3 zonas de un invernadero.

| # | Componente | Cantidad adicional | Precio Est. (USD) |
|---|-----------|--------------------|--------------------|
| 1 | DS18B20 adicionales | 2 | $7.00 |
| 2 | DHT22 adicionales | 2 | $8.00 |
| 3 | BH1750 adicionales | 2 | $5.00 |
| 4 | Sensores de suelo adicionales | 2 | $4.00 |
| 5 | Multiplexor I2C | TCA9548A | 1 | $3.00 |
| 6 | Cables jumper adicionales | 40 unidades | $3.00 |
| — | **Subtotal adicional** | | **$30.00** |
| — | **Total Kit Profesional** | | **$143.10** |

---

## Precios Sugeridos de Venta

| Kit | Costo | Margen | Precio de Venta |
|-----|-------|--------|-----------------|
| Kit Básico (1 zona) | $113.10 | 60% | **$180.00 USD** |
| Kit Profesional (3 zonas) | $143.10 | 55% | **$220.00 USD** |
| Software + Soporte (anual) | — | — | **$120.00 USD/año** |
| Instalación + Capacitación | — | — | **$150.00 USD** |

---

## Contenido del Kit

### Hardware

1. Raspberry Pi 4B con tarjeta microSD pre-grabada (EchoSmart OS)
2. Sensores con cables etiquetados por color
3. Carcasa protectora IP65
4. Fuente de alimentación USB-C

### Software Pre-instalado

- Raspberry Pi OS Lite (64-bit)
- Paquete `echosmart-gateway` (.deb) pre-instalado
- Servicio systemd habilitado al arranque
- Wizard de configuración: `sudo echosmart-gateway-setup`

### Documentación Incluida

- Guía de inicio rápido (impresa, 1 hoja)
- Diagrama de conexiones por sensor (impreso)
- QR code a documentación completa en línea

---

## Guía de Ensamblaje

### Paso 1 — Preparar la microSD

```bash
# Descargar la imagen pre-configurada desde GitHub Releases
wget https://github.com/Uaemextop/echosmart/releases/latest/download/echosmart-gateway.img.xz

# Grabar en la microSD (Linux/macOS)
xzcat echosmart-gateway.img.xz | sudo dd of=/dev/sdX bs=4M status=progress
```

O usar **Raspberry Pi Imager** con la imagen personalizada.

### Paso 2 — Conectar Sensores

#### Diagrama de conexión GPIO

```
Raspberry Pi 4B GPIO Header
─────────────────────────────
Pin  1 (3.3V) ─── DS18B20 VCC, BH1750 VCC, ADS1115 VCC
Pin  3 (SDA)  ─── BH1750 SDA, ADS1115 SDA
Pin  5 (SCL)  ─── BH1750 SCL, ADS1115 SCL
Pin  6 (GND)  ─── Todos los GND
Pin  7 (GPIO4)─── DS18B20 DATA (+ 4.7kΩ pull-up a 3.3V)
Pin  7 (GPIO4)─── DHT22 DATA
Pin  8 (TXD)  ─── MH-Z19C RXD
Pin 10 (RXD)  ─── MH-Z19C TXD
Pin 14 (GND)  ─── MH-Z19C GND
Pin  4 (5V)   ─── MH-Z19C VIN, DHT22 VCC
```

> **Nota**: El DS18B20 y DHT22 pueden compartir GPIO4 o usar pines separados configurables en `sensors.json`.

### Paso 3 — Primer Arranque

1. Insertar la microSD en la Raspberry Pi
2. Conectar cable Ethernet (o configurar WiFi previamente)
3. Conectar la fuente de alimentación
4. Esperar ~60 segundos al primer arranque
5. Ejecutar el wizard: `sudo echosmart-gateway-setup`

### Paso 4 — Verificar Funcionamiento

```bash
# Verificar el servicio
systemctl status echosmart-gateway

# Ver lecturas en tiempo real
journalctl -u echosmart-gateway -f

# Probar sensores
echosmart-gateway test-sensors

# Ver configuración
echosmart-gateway status
```

---

## Control de Calidad

### Checklist de QA por Unidad

- [ ] Raspberry Pi enciende correctamente
- [ ] microSD con imagen correcta
- [ ] Cada sensor responde en modo test
- [ ] Conexión a red exitosa
- [ ] Servicio systemd activo
- [ ] Sincronización con cloud exitosa (si aplica)
- [ ] Carcasa sellada y cables organizados

### Prueba de Estrés

```bash
# Ejecutar 100 lecturas consecutivas en modo simulación
echosmart-gateway run --simulate
```

---

## Proveedores Sugeridos

| Componente | Proveedor | Región |
|-----------|-----------|--------|
| Raspberry Pi 4B | Farnell / Newark | Global |
| Sensores (DS18B20, DHT22, BH1750) | AliExpress / Amazon | Global |
| MH-Z19C | Winsen Electronics | China |
| ADS1115 | Adafruit / SparkFun | US |
| Carcasas IP65 | AliExpress / local | Global |
| microSD | SanDisk / Kingston | Global |

---

## Logística de Producción en Masa

### Para 100 unidades

| Concepto | Costo Unitario | Total |
|----------|---------------|-------|
| Componentes (Kit Básico) | $95.00* | $9,500 |
| Ensamblaje y QA | $15.00 | $1,500 |
| Empaque y documentación | $5.00 | $500 |
| Grabado microSD | $2.00 | $200 |
| **Total por unidad** | **$117.00** | **$11,700** |

*\*Precio con descuento por volumen (~16% de ahorro).*

### Margen Proyectado (100 unidades)

| | Valor |
|---|-------|
| Costo total | $11,700 |
| Ingresos (100 × $180) | $18,000 |
| **Margen bruto** | **$6,300 (35%)** |

---

*Última actualización: Marzo 2026*
