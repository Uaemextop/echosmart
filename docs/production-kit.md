# EchoSmart — Kit de Producción Comercial

> Guía completa para fabricar, ensamblar y vender el kit EchoSmart de monitoreo ambiental para invernaderos.

---

## 1. Descripción del Producto

El **EchoSmart Kit** es un sistema IoT listo para usar (plug-and-play) que permite a los productores agrícolas monitorear en tiempo real la temperatura, humedad, luminosidad, CO₂ y humedad de suelo de sus invernaderos.

### 1.1 Componentes del Kit

| # | Componente | Modelo / Descripción | Cantidad |
|---|-----------|---------------------|----------|
| 1 | Raspberry Pi 4B | 4 GB RAM · ARM Cortex-A72 · 64-bit | 1 |
| 2 | Tarjeta microSD | 32 GB · Clase 10 · A2 · con ISO pre-flasheado | 1 |
| 3 | Fuente de alimentación | Oficial RPi 5V 3A USB-C | 1 |
| 4 | Case / carcasa | Aluminio con ventilador pasivo | 1 |
| 5 | Sensor DS18B20 | Temperatura impermeable · 1-Wire | 2 |
| 6 | Sensor DHT22 | Temperatura + Humedad relativa · GPIO | 2 |
| 7 | Sensor BH1750 | Luminosidad (Lux) · I2C | 1 |
| 8 | Sensor MH-Z19C | CO₂ NDIR · UART | 1 |
| 9 | Sensor humedad suelo | Capacitivo v1.2 | 2 |
| 10 | ADC ADS1115 | 16-bit · 4 canales · I2C | 1 |
| 11 | Cable jumper | Macho-hembra · 20 cm · 40 piezas | 1 juego |
| 12 | Resistencias | 4.7 kΩ (×5) + 10 kΩ (×5) | 1 juego |
| 13 | Protoboard | 400 puntos (opcional, para prototipo) | 1 |
| 14 | Caja impermeable | IP65 · montaje pared · 200×150×75 mm | 1 |
| 15 | Cable de red | Cat6 · 2 m (alternativa: adaptador Wi-Fi USB) | 1 |
| 16 | Guía de instalación | Impresa + QR a docs online | 1 |
| 17 | Tarjeta de activación | Código único para registrar el gateway | 1 |

---

## 2. Lista de Materiales (BOM) y Costos

### 2.1 Costo de Manufactura por Unidad (USD)

| Componente | Proveedor sugerido | Costo unitario | Cantidad | Subtotal |
|-----------|-------------------|----------------|----------|----------|
| Raspberry Pi 4B 4GB | RS Components / Mouser | $55.00 | 1 | $55.00 |
| microSD 32 GB (flasheada) | Amazon / Aliexpress + tiempo | $8.00 | 1 | $8.00 |
| Fuente RPi oficial | Raspberry Pi Foundation | $8.00 | 1 | $8.00 |
| Case aluminio + ventilador | Aliexpress | $12.00 | 1 | $12.00 |
| DS18B20 (×2) | Aliexpress / LCSC | $2.50 | 2 | $5.00 |
| DHT22 (×2) | Aliexpress / LCSC | $3.00 | 2 | $6.00 |
| BH1750 módulo | Aliexpress | $1.50 | 1 | $1.50 |
| MH-Z19C | Aliexpress | $22.00 | 1 | $22.00 |
| Sensor humedad suelo (×2) | Aliexpress | $2.00 | 2 | $4.00 |
| ADS1115 módulo | Aliexpress | $2.50 | 1 | $2.50 |
| Cables + resistencias | Aliexpress | $3.00 | 1 | $3.00 |
| Caja impermeable IP65 | Aliexpress | $8.00 | 1 | $8.00 |
| Impresión guía + tarjeta | Impresión local | $2.00 | 1 | $2.00 |
| Embalaje (caja + relleno) | Proveedor local | $3.00 | 1 | $3.00 |
| **Subtotal materiales** | | | | **$140.00** |
| Mano de obra ensamblaje | 1 h a $15/h | $15.00 | 1 | $15.00 |
| Flasheo y QA | 30 min a $15/h | $7.50 | 1 | $7.50 |
| **Costo total de manufactura** | | | | **$162.50** |

### 2.2 Estructura de Precios de Venta

| Canal | Precio de Venta (USD) | Margen bruto |
|-------|----------------------|-------------|
| **Directo al productor** | $350 | 115 % |
| **Distribuidor agrícola** | $280 | 72 % |
| **Reventa B2B (≥10 kits)** | $240 | 48 % |
| **E-commerce (Amazon/MercadoLibre)** | $380 (+comisión) | 92 % neto |

### 2.3 Modelo de Suscripción (Software como Servicio)

| Plan | Gateways | Sensores | Precio/mes | Precio/año |
|------|---------|---------|-----------|-----------|
| **Básico** | 1 | 5 | $9 | $90 |
| **Profesional** | 5 | 30 | $29 | $290 |
| **Empresarial** | Ilimitado | Ilimitado | $99 | $990 |

> El kit de hardware incluye **6 meses de suscripción Profesional gratis** con el código de activación.

---

## 3. Guía de Ensamblaje

### 3.1 Herramientas necesarias

- Destornillador Phillips #0 y #1
- Pelacables / alicates de punta fina
- Multímetro (verificación de continuidad)
- Laptop/PC con lector microSD (para flashear)
- Etiquetadora o marcador permanente

### 3.2 Proceso de Flasheo de la microSD

```bash
# En la máquina de producción (Linux/macOS)
# 1. Descargar la imagen del gateway
wget https://github.com/Uaemextop/echosmart/releases/latest/download/echosmart-gateway-arm64.img.xz

# 2. Verificar la integridad
sha256sum echosmart-gateway-arm64.img.xz

# 3. Flashear (reemplazar /dev/sdX con el dispositivo correcto)
xzcat echosmart-gateway-arm64.img.xz | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync

# 4. Verificar que la imagen arranca (opcional, en QEMU o hardware real)
```

**Alternativa** — Usar Raspberry Pi Imager con imagen personalizada.

### 3.3 Diagrama de Conexión de Sensores

```
Raspberry Pi GPIO (40 pines)
┌─────────────────────────────────────────────────────────┐
│ 3.3V ─────── VCC (DS18B20, BH1750, ADS1115, DHT22)     │
│ 5V ───────── VCC (MH-Z19C)                              │
│ GND ──────── GND (todos los sensores)                   │
│                                                         │
│ GPIO 4  ──── DATA (DS18B20) + R 4.7kΩ pull-up a 3.3V  │
│ GPIO 17 ──── DATA (DHT22) + R 10kΩ pull-up a 3.3V     │
│ GPIO 2  ──── SDA (BH1750, ADS1115) — I2C               │
│ GPIO 3  ──── SCL (BH1750, ADS1115) — I2C               │
│ GPIO 14 ──── TX → RX MH-Z19C — UART                    │
│ GPIO 15 ──── RX ← TX MH-Z19C — UART                    │
│                                                         │
│ ADS1115 A0 ── Sensor humedad suelo 1                    │
│ ADS1115 A1 ── Sensor humedad suelo 2                    │
└─────────────────────────────────────────────────────────┘
```

### 3.4 Pasos de Ensamblaje

1. **Insertar microSD** en la Raspberry Pi.
2. **Instalar RPi en la carcasa** de aluminio. Conectar ventilador a GPIO 5V + GND.
3. **Conectar sensores** según el diagrama anterior. Usar cables jumper etiquetados.
4. **Cerrar la caja impermeable** IP65 pasando cables por prensaestopas.
5. **Conectar fuente de alimentación** (aún sin encender).
6. **Encender y verificar** que los LEDs del RPi parpadeen correctamente.
7. **Test de calidad (QA)**: conectar a red, verificar que el gateway aparece en el dashboard.

### 3.5 Checklist de Control de Calidad (QA)

```
□ LED de actividad del RPi parpadea al arrancar
□ Acceso SSH al gateway (usuario: pi, pass: echosmart)
□ Servicio systemd activo: systemctl status echosmart-gateway
□ Lectura de temperatura DS18B20 OK: echosmart-gateway test-sensors
□ Lectura de humedad DHT22 OK
□ Lectura de luminosidad BH1750 OK
□ Lectura de CO₂ MH-Z19C OK (300–500 ppm en ambiente exterior)
□ Lectura de humedad suelo OK
□ Sincronización con backend cloud OK (aparece en dashboard)
□ Alerta de prueba disparada y recibida por email
□ Etiqueta de número de serie pegada en la carcasa
□ Guía impresa + tarjeta de activación incluidas en la caja
```

---

## 4. Logística y Distribución

### 4.1 Embalaje

- **Caja exterior**: 300×250×150 mm, kraft reciclado, con logo EchoSmart impreso.
- **Interior**: espuma moldeada EPE para Raspberry Pi + sensores.
- **Incluye**: caja impermeable IP65 pre-ensamblada, cables, guía, tarjeta de activación.
- **Peso total**: ~1.2 kg.

### 4.2 Opciones de Envío (México)

| Servicio | Tiempo | Costo aprox. |
|---------|--------|-------------|
| DHL Express | 1–2 días hábiles | $180 MXN |
| FedEx Economy | 3–5 días hábiles | $120 MXN |
| Estafeta | 2–4 días hábiles | $90 MXN |
| Entrega local CDMX/GDL/MTY | Mismo día / siguiente | $60 MXN |

### 4.3 Garantía y Soporte

- **Garantía de hardware**: 12 meses contra defectos de fabricación.
- **Soporte técnico**: helpdesk@echosmart.io, respuesta <24 h hábiles.
- **Actualizaciones de software**: automáticas vía `apt update` incluidas en el servicio.

---

## 5. Escalado a Producción en Masa

### 5.1 Volúmenes y Economías de Escala

| Volumen / mes | Costo unitario | Precio sugerido | Margen |
|--------------|----------------|----------------|--------|
| 10 unidades | $162 | $350 | 116 % |
| 50 unidades | $138 | $330 | 139 % |
| 100 unidades | $120 | $310 | 158 % |
| 500 unidades | $98 | $290 | 196 % |

### 5.2 Proceso de Flasheo Automatizado (Línea de Producción)

```bash
# Script para flashear múltiples microSDs en paralelo
# Requiere un hub USB con puertos suficientes
for dev in /dev/sd{b,c,d,e}; do
  xzcat echosmart-gateway-arm64.img.xz | \
    sudo dd of=${dev} bs=4M status=none conv=fsync &
done
wait
echo "Flasheo completado en todos los dispositivos"
```

### 5.3 Infraestructura del Servidor para Clientes

Cada cliente recibe acceso a una instancia dedicada del backend EchoSmart (cloud o on-premise):

- **SaaS**: hospedado en AWS/GCP, sin gestión por parte del cliente.
- **On-premise**: instalación del servidor ISO en hardware propio del cliente.

Ver [ISO del Servidor](server-iso-setup.md) para más detalles.

---

## 6. Certificaciones y Cumplimiento

| Certificación | Estado | Notas |
|--------------|--------|-------|
| CE (UE) | 🟡 Pendiente | Requerida para venta en Europa |
| FCC (EE.UU.) | 🟡 Pendiente | Requerida para venta en EE.UU. |
| NOM (México) | 🟡 Pendiente | NOM-019-SCFI para equipos electrónicos |
| RoHS | 🟢 Raspberry Pi certificada | Sensores importados a verificar |
| IP65 (carcasa) | 🟢 Verificada por fabricante | Protección polvo + agua a presión |

---

## 7. Canal de Ventas y Marketing

### 7.1 Landing Page del Producto

La demo interactiva está disponible en `demo/` del repositorio. Muestra:
- Dashboard de monitoreo en tiempo real
- Mapa de calor del invernadero
- Reportes con IA integrada

### 7.2 Mensajes Clave de Venta

- **"Sin conocimientos técnicos"** — El kit se instala en 30 minutos con la guía incluida.
- **"Amortización en 1 temporada"** — Reducción de pérdidas por condiciones fuera de rango.
- **"Escala cuando necesites"** — De 1 gateway/5 sensores a ilimitados sin cambiar software.
- **"Datos siempre disponibles"** — Edge computing: sigue funcionando sin internet.

---

*Última actualización: Marzo 2026 — EchoSmart Dev Team*
