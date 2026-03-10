# EchoSmart — Configuración del Sistema Operativo en Raspberry Pi

Guía paso a paso para preparar una Raspberry Pi como gateway de EchoSmart, desde la instalación del sistema operativo hasta la verificación de todas las interfaces de hardware.

---

## 1. Requisitos Previos

### Hardware

| Componente | Especificación |
|------------|---------------|
| Raspberry Pi | 4B con 4 GB de RAM (recomendado 8 GB) |
| Fuente de alimentación | 5 V / 3 A USB-C oficial |
| Tarjeta microSD | 32 GB Class 10 (recomendado 64 GB) |
| Lector de tarjetas SD | Para flashear el sistema operativo |
| Cable Ethernet o acceso WiFi | Para conectividad de red |
| Teclado + monitor (opcional) | Solo para la configuración inicial si no se usa SSH |

### Software en el Equipo de Trabajo

- [Raspberry Pi Imager](https://www.raspberrypi.com/software/) instalado en tu computadora.

---

## 2. Instalación de Raspberry Pi OS

### 2.1 Flashear la Imagen

1. Abrir **Raspberry Pi Imager**.
2. Seleccionar **Raspberry Pi OS (64-bit)** como sistema operativo.
3. Seleccionar la tarjeta microSD como destino.
4. Hacer clic en el ícono de engranaje (⚙) para configurar opciones avanzadas:
   - **Hostname**: `echosmart-gw-01`
   - **Habilitar SSH**: Sí, con autenticación por contraseña o clave pública.
   - **Configurar WiFi**: Ingresar SSID y contraseña de la red.
   - **Establecer usuario**: Nombre de usuario y contraseña para el sistema.
   - **Zona horaria y teclado**: Seleccionar la configuración local.
5. Hacer clic en **Escribir** y esperar a que finalice.

### 2.2 Primer Arranque

1. Insertar la tarjeta microSD en la Raspberry Pi.
2. Conectar la alimentación.
3. Esperar 1–2 minutos a que el sistema arranque por primera vez.
4. Conectarse por SSH:

```bash
ssh usuario@echosmart-gw-01.local
# O por IP directa:
ssh usuario@192.168.x.x
```

---

## 3. Actualización del Sistema

```bash
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

Después del reinicio, verificar la versión:

```bash
cat /etc/os-release
uname -a
# Debe mostrar aarch64 (64-bit)
```

---

## 4. Configuración de Red

### 4.1 IP Estática (Recomendado para el Gateway)

Editar la configuración de `dhcpcd`:

```bash
sudo nano /etc/dhcpcd.conf
```

Agregar al final del archivo:

```
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4

# Para WiFi, usar wlan0 en lugar de eth0
```

Reiniciar el servicio:

```bash
sudo systemctl restart dhcpcd
```

### 4.2 Configurar Hostname

```bash
sudo hostnamectl set-hostname echosmart-gw-01
```

Editar `/etc/hosts` para reflejar el nuevo nombre:

```bash
sudo nano /etc/hosts
# Cambiar la línea con 127.0.1.1 al nuevo hostname
```

---

## 5. Habilitar Interfaces de Hardware

### 5.1 Usar `raspi-config`

```bash
sudo raspi-config
```

Navegar a **Interface Options** y habilitar:

| Interfaz | Menú | Uso en EchoSmart |
|----------|------|-------------------|
| **I2C** | Interface Options → I2C → Enable | Sensor BH1750 (luminosidad) |
| **1-Wire** | Interface Options → 1-Wire → Enable | Sensor DS18B20 (temperatura) |
| **Serial Port** | Interface Options → Serial Port → No (login shell) → Yes (hardware) | Sensor MHZ-19C (CO₂) |
| **SPI** | Interface Options → SPI → Enable | ADC ADS1115 (si se conecta por SPI) |

Reiniciar tras los cambios:

```bash
sudo reboot
```

### 5.2 Configuración Manual del Device Tree

Editar `/boot/firmware/config.txt`:

```bash
sudo nano /boot/firmware/config.txt
```

Agregar o verificar las siguientes líneas:

```ini
# Habilitar I2C
dtparam=i2c_arm=on

# Habilitar 1-Wire en GPIO4
dtoverlay=w1-gpio,gpiopin=4

# Habilitar UART para sensor de CO2
enable_uart=1

# Deshabilitar Bluetooth si no se usa (libera UART principal)
dtoverlay=disable-bt

# Asignar memoria mínima a GPU (el gateway no usa interfaz gráfica)
gpu_mem=16
```

Reiniciar:

```bash
sudo reboot
```

### 5.3 Verificar Interfaces

**I2C:**

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
# Debe mostrar una tabla; los dispositivos conectados aparecen con su dirección (ej. 0x23 para BH1750)
```

**1-Wire:**

```bash
ls /sys/bus/w1/devices/
# Debe listar dispositivos como 28-0516a42651ff (DS18B20)
```

**UART:**

```bash
ls -l /dev/serial*
# Debe mostrar /dev/serial0 → /dev/ttyS0 o /dev/ttyAMA0
```

---

## 6. Instalación de Herramientas del Sistema

```bash
# Herramientas esenciales de desarrollo
sudo apt install -y \
  python3-dev \
  python3-pip \
  python3-venv \
  build-essential \
  git \
  i2c-tools \
  mosquitto \
  mosquitto-clients

# Verificar versiones
python3 --version    # Debe ser 3.9+
git --version
mosquitto -v         # Verificar instalación del broker MQTT
```

---

## 7. Configuración de Mosquitto (MQTT Broker Local)

### 7.1 Configurar el Broker

```bash
sudo nano /etc/mosquitto/conf.d/echosmart.conf
```

Contenido:

```
# Escuchar en el puerto estándar
listener 1883

# Permitir conexiones anónimas en red local (solo desarrollo)
allow_anonymous true

# Para producción, habilitar autenticación:
# allow_anonymous false
# password_file /etc/mosquitto/passwd
```

### 7.2 Crear Usuarios (Producción)

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd echosmart
# Ingresar contraseña cuando se solicite
```

### 7.3 Habilitar y Verificar

```bash
sudo systemctl enable mosquitto
sudo systemctl restart mosquitto
sudo systemctl status mosquitto

# Prueba rápida (en dos terminales):
# Terminal 1 (suscriptor):
mosquitto_sub -t "echosmart/test"
# Terminal 2 (publicador):
mosquitto_pub -t "echosmart/test" -m "Hola EchoSmart"
```

---

## 8. Entorno Python para el Gateway

### 8.1 Crear Entorno Virtual

```bash
mkdir -p /opt/echosmart
cd /opt/echosmart
git clone https://github.com/Uaemextop/echosmart.git
cd echosmart/gateway

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 8.2 Dependencias Principales

```
RPi.GPIO>=0.7.1
adafruit-circuitpython-dht>=3.7
adafruit-circuitpython-bh1750>=1.1
adafruit-circuitpython-ads1x15>=2.2
paho-mqtt>=1.6
requests>=2.28
```

### 8.3 Permisos de Hardware

Para acceder a GPIO, I2C y 1-Wire sin `sudo`:

```bash
sudo usermod -aG gpio,i2c,dialout $USER
# Cerrar sesión y volver a entrar para que los cambios tengan efecto
```

---

## 9. Servicio Systemd para Auto-Inicio

Crear el archivo de servicio:

```bash
sudo nano /etc/systemd/system/echosmart-gateway.service
```

Contenido:

```ini
[Unit]
Description=EchoSmart Gateway Service
After=network.target mosquitto.service
Wants=mosquitto.service

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/echosmart/echosmart/gateway
ExecStart=/opt/echosmart/echosmart/gateway/venv/bin/python main.py
Restart=on-failure
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Habilitar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable echosmart-gateway
sudo systemctl start echosmart-gateway

# Verificar estado
sudo systemctl status echosmart-gateway

# Ver logs en tiempo real
journalctl -u echosmart-gateway -f
```

---

## 10. Optimizaciones para Producción

### 10.1 Deshabilitar Servicios Innecesarios

```bash
# El gateway no necesita interfaz gráfica
sudo systemctl disable lightdm
sudo apt remove -y xserver-xorg* desktop-base

# Deshabilitar Bluetooth si no se utiliza
sudo systemctl disable bluetooth
```

### 10.2 Configurar Log Rotation

```bash
sudo nano /etc/logrotate.d/echosmart
```

```
/var/log/echosmart/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 10.3 Watchdog de Hardware

Editar `/boot/firmware/config.txt`:

```ini
# Habilitar watchdog de hardware
dtparam=watchdog=on
```

Instalar y configurar:

```bash
sudo apt install -y watchdog
sudo nano /etc/watchdog.conf
# Descomentar: watchdog-device = /dev/watchdog
# Descomentar: max-load-1 = 24
sudo systemctl enable watchdog
sudo systemctl start watchdog
```

---

## 11. Checklist de Verificación

Ejecutar cada comando y confirmar el resultado esperado:

| # | Verificación | Comando | Resultado Esperado |
|---|-------------|---------|-------------------|
| 1 | OS 64-bit | `uname -m` | `aarch64` |
| 2 | Python 3.9+ | `python3 --version` | `Python 3.9.x` o superior |
| 3 | I2C habilitado | `i2cdetect -y 1` | Tabla de direcciones sin errores |
| 4 | 1-Wire habilitado | `ls /sys/bus/w1/devices/` | Lista de dispositivos |
| 5 | UART habilitado | `ls /dev/serial0` | Enlace simbólico presente |
| 6 | Mosquitto activo | `systemctl status mosquitto` | `active (running)` |
| 7 | GPIO accesible | `groups` | Incluye `gpio`, `i2c`, `dialout` |
| 8 | Red configurada | `ip addr show` | IP estática asignada |
| 9 | Servicio gateway | `systemctl status echosmart-gateway` | `active (running)` |

---

## 12. Resolución de Problemas

### "Permission denied" al acceder a GPIO o I2C

```bash
# Verificar grupos del usuario
groups
# Si falta gpio o i2c:
sudo usermod -aG gpio,i2c,dialout $USER
# Cerrar sesión y reconectar
```

### No se detectan dispositivos 1-Wire

```bash
# Verificar que el módulo esté cargado
lsmod | grep w1_
# Si no aparece, revisar /boot/firmware/config.txt y reiniciar
```

### UART no responde

```bash
# Verificar que la consola serial esté deshabilitada
sudo raspi-config
# Interface Options → Serial Port → No (login shell) → Yes (hardware)
# Reiniciar
```

### Mosquitto no inicia

```bash
# Revisar logs
journalctl -u mosquitto -n 50
# Verificar que el puerto 1883 no esté ocupado
sudo ss -tlnp | grep 1883
```

---

## Siguientes Pasos

- Conectar los sensores siguiendo la guía de [Sensores y Hardware](sensors-hardware.md).
- Configurar los drivers del gateway con [Gateway y Edge Computing](gateway-edge-computing.md).
- Verificar la conectividad con el backend en [Primeros Pasos](getting-started.md).

---

*Volver al [Índice de Documentación](README.md)*
