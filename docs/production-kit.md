# EchoSmart Production Kit — BOM, Pricing & Assembly

> Guía para producción en masa del kit EchoSmart: Raspberry Pi + sensores
> listos para venta comercial.

---

## 1. Bill of Materials (BOM) — Kit Básico

| #  | Componente                | Modelo / Ref.         | Cant. | Costo unit. (USD) | Subtotal |
|----|---------------------------|-----------------------|------:|-------------------:|---------:|
| 1  | Single-board computer     | Raspberry Pi 4B 4 GB  |     1 |             55.00  |    55.00 |
| 2  | MicroSD (pre-flasheada)   | SanDisk 32 GB A1      |     1 |              8.00  |     8.00 |
| 3  | Fuente de alimentación    | USB-C 5 V / 3 A       |     1 |              9.00  |     9.00 |
| 4  | Sensor de temperatura     | DS18B20 waterproof     |     3 |              3.50  |    10.50 |
| 5  | Sensor temp + humedad     | DHT22 / AM2302         |     3 |              4.00  |    12.00 |
| 6  | Sensor de CO₂             | MH-Z19C (NDIR)         |     1 |             22.00  |    22.00 |
| 7  | Sensor de luz             | BH1750 (I2C)           |     1 |              2.50  |     2.50 |
| 8  | Sensor de suelo           | Capacitivo + ADS1115   |     2 |              5.00  |    10.00 |
| 9  | Carcasa IP65              | Caja ABS sellada       |     1 |              7.00  |     7.00 |
| 10 | Cables y conectores       | Dupont + prensatermin. |     1 |              5.00  |     5.00 |
| 11 | Protoboard / PCB custom   | Adaptador HAT          |     1 |              4.00  |     4.00 |
|    | **Total componentes**     |                        |       |                    | **145.00** |

### Variantes de kit

| Kit           | Contenido                          | Costo comp. | PVP sugerido |
|---------------|------------------------------------|------------:|-------------:|
| **Básico**    | RPi + 2 sensores + software        |      80 USD |     149 USD  |
| **Estándar**  | RPi + 5 sensores + CO₂ + software  |     145 USD |     249 USD  |
| **Pro**       | Estándar + PoE HAT + carcasa IP67  |     195 USD |     349 USD  |

---

## 2. Pre-flashing de la MicroSD

Cada MicroSD se entrega con el SO y el gateway pre-instalado:

```bash
# 1. Flash Raspberry Pi OS Lite (64-bit)
sudo rpi-imager --cli --os raspios_lite_arm64 --storage /dev/sdX

# 2. Montar e instalar el .deb
sudo mount /dev/sdX2 /mnt
sudo cp echosmart-gateway_1.0.0-1_all.deb /mnt/tmp/
sudo chroot /mnt dpkg -i /tmp/echosmart-gateway_1.0.0-1_all.deb
sudo umount /mnt
```

Alternativa automatizada: usar **pi-gen** con un stage personalizado
(ver `docs/gateway-iso-setup.md`).

---

## 3. Guía de Ensamblaje

### 3.1 Conexiones de sensores

```
Raspberry Pi GPIO Header
────────────────────────
Pin  1 (3.3 V)  ──►  VCC de BH1750, DS18B20
Pin  2 (5 V)    ──►  VCC de DHT22, MH-Z19C
Pin  6 (GND)    ──►  GND de todos los sensores
Pin  7 (GPIO 4) ──►  DATA de DS18B20 (+ resistencia 4.7 kΩ a 3.3 V)
Pin  3 (SDA)    ──►  SDA de BH1750, ADS1115
Pin  5 (SCL)    ──►  SCL de BH1750, ADS1115
Pin 11 (GPIO 17)──►  DATA de DHT22
Pin  8 (TX)     ──►  RX de MH-Z19C
Pin 10 (RX)     ──►  TX de MH-Z19C
```

### 3.2 Pasos de ensamblaje

1. Insertar la MicroSD pre-flasheada en la Raspberry Pi.
2. Conectar los sensores según el diagrama de la sección 3.1.
3. Colocar la Raspberry Pi y los sensores dentro de la carcasa IP65.
4. Conectar la fuente de alimentación.
5. Encender — el servicio `echosmart-gateway` inicia automáticamente.
6. Ejecutar `sudo echosmart-gateway-setup` para configurar la conexión
   al servidor cloud.

---

## 4. Control de Calidad (QC)

Cada kit debe pasar estas pruebas antes del envío:

| Test                     | Comando / Verificación                        | Criterio    |
|--------------------------|-----------------------------------------------|-------------|
| Boot exitoso             | LED verde parpadea                            | PASS        |
| Conectividad WiFi/Eth    | `ping -c 3 8.8.8.8`                          | 0% loss     |
| Lecturas de sensores     | `echosmart-gateway test-sensors`              | 5/5 passed  |
| Servicio systemd         | `systemctl status echosmart-gateway`          | active       |
| Sincronización cloud     | `echosmart-gateway status` → `cloud_api_url`  | URL correcta |

---

## 5. Etiquetado y Empaque

- Etiqueta exterior: logo EchoSmart, modelo de kit, número de serie.
- Contenido de la caja:
  - Raspberry Pi con MicroSD insertada.
  - Sensores en bolsas antiestáticas individuales.
  - Fuente de alimentación.
  - Guía rápida de inicio (tarjeta impresa A5).
  - Pegatinas con códigos QR a documentación online.

---

## 6. Licencias y Cumplimiento

| Aspecto           | Estado                                           |
|-------------------|--------------------------------------------------|
| Software          | MIT License (ver `LICENSE`)                      |
| Hardware          | Diseño abierto (esquemáticos publicados)         |
| CE / FCC          | Raspberry Pi ya cuenta con certificación         |
| Garantía sugerida | 12 meses contra defectos de fabricación          |
