# EchoSmart Gateway — Guía de Empaquetado .deb

> Referencia técnica para construir, instalar y mantener el paquete
> `echosmart-gateway` en Raspberry Pi OS Bullseye / Bookworm (arm64).

---

## Tabla de contenidos

1. [Descripción del paquete](#descripción-del-paquete)
2. [Prerrequisitos de build](#prerrequisitos-de-build)
3. [Estructura de archivos](#estructura-de-archivos)
4. [Compilar el .deb](#compilar-el-deb)
5. [Instalar en Raspberry Pi](#instalar-en-raspberry-pi)
6. [Configuración post-instalación](#configuración-post-instalación)
7. [Gestión del servicio systemd](#gestión-del-servicio-systemd)
8. [Actualización del paquete](#actualización-del-paquete)
9. [Desinstalación](#desinstalación)
10. [CI/CD — Build automático](#cicd--build-automático)
11. [Troubleshooting](#troubleshooting)

---

## Descripción del paquete

| Campo | Valor |
|-------|-------|
| Nombre | `echosmart-gateway` |
| Versión actual | `1.0.0-1` |
| Arquitectura | `arm64` |
| Estándar Debian | 4.6.0, debhelper compat 13 |
| Instala en | `/opt/echosmart/gateway/` |
| Config en | `/etc/echosmart/` |
| Datos en | `/var/lib/echosmart/` |
| Servicio | `echosmart-gateway.service` |
| Binarios | `/usr/bin/echosmart-sysinfo`, `/usr/bin/echosmart-sensor-read` |

### Dependencias de runtime

```
python3 (>= 3.9)
python3-pip
python3-venv
libgpiod2
python3-libgpiod
i2c-tools
mosquitto
mosquitto-clients
sqlite3
curl
adduser
```

---

## Prerrequisitos de build

### Build nativo (en Raspberry Pi arm64)

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    dpkg-dev \
    devscripts \
    debhelper \
    cmake \
    linux-libc-dev \
    fakeroot
```

### Cross-compilation (Ubuntu x86_64 → arm64)

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    dpkg-dev \
    devscripts \
    debhelper \
    cmake \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    binutils-aarch64-linux-gnu \
    crossbuild-essential-arm64 \
    linux-libc-dev-arm64-cross \
    fakeroot \
    lintian
```

---

## Estructura de archivos

```
gateway/
├── cpp/
│   ├── CMakeLists.txt               ← Build system C++
│   ├── echosmart-sysinfo.cpp        ← Binario: diagnóstico del sistema
│   └── echosmart-sensor-read.cpp    ← Binario: lectura de sensores
├── debian/
│   ├── changelog                    ← Historial de cambios (formato Debian)
│   ├── compat                       ← Nivel debhelper (13)
│   ├── control                      ← Metadata del paquete y dependencias
│   ├── echosmart-gateway.service    ← Servicio systemd
│   ├── gateway.env.example          ← Plantilla de configuración
│   ├── postinst                     ← Script post-instalación
│   ├── prerm                        ← Script pre-desinstalación
│   └── rules                        ← Makefile de build del paquete
├── src/                             ← Python gateway (se instala en /opt/)
├── tests/
├── main.py
├── requirements.txt
└── sensors.json
```

---

## Compilar el .deb

### Método 1 — Makefile raíz (recomendado)

```bash
# Desde la raíz del repositorio:
make deb

# El .deb se genera en la raíz del repo:
ls -lh echosmart-gateway_*.deb
```

### Método 2 — dpkg-buildpackage directo

```bash
cd gateway/

# Cross-compile para arm64 desde Ubuntu x86_64:
dpkg-buildpackage \
    -b \           # solo binario (sin tarball fuente)
    -us \          # no firmar fuente
    -uc \          # no firmar changes
    --host-arch=arm64 \
    --build-profiles=nocheck \
    -rfakeroot

# El .deb se genera en el directorio padre (gateway/../):
ls -lh ../echosmart-gateway_*.deb
```

### Método 3 — CMake directo (solo binarios, sin .deb)

```bash
# Build solo los binarios C++ (útil para testing):
mkdir -p gateway/debian/build-cpp
cd gateway/debian/build-cpp

cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_COMPILER=aarch64-linux-gnu-gcc \
    -DCMAKE_CXX_COMPILER=aarch64-linux-gnu-g++ \
    ../../cpp

make -j$(nproc)

# Verificar:
file echosmart-sysinfo echosmart-sensor-read
# → echosmart-sysinfo: ELF 64-bit LSB executable, ARM aarch64
```

### Verificar el .deb generado

```bash
# Información del paquete:
dpkg-deb --info echosmart-gateway_1.0.0-1_arm64.deb

# Contenido del paquete:
dpkg-deb --contents echosmart-gateway_1.0.0-1_arm64.deb

# Lintian (análisis de calidad):
lintian echosmart-gateway_1.0.0-1_arm64.deb
```

---

## Instalar en Raspberry Pi

### Requisitos de instalación

- Raspberry Pi 4 Model B (arm64)
- Raspberry Pi OS Bullseye 64-bit o Bookworm 64-bit
- Conexión a internet (para descargar dependencias)
- Usuario con `sudo`

### Instalación desde GitHub Releases

```bash
# 1. Descargar el .deb (reemplazar VERSION por la versión actual):
VERSION=1.0.0
wget https://github.com/echosmart/echosmart/releases/download/v${VERSION}/echosmart-gateway_${VERSION}-1_arm64.deb

# 2. Instalar:
sudo dpkg -i echosmart-gateway_${VERSION}-1_arm64.deb

# 3. Resolver dependencias faltantes:
sudo apt-get install -f

# 4. Verificar instalación:
dpkg -l echosmart-gateway
which echosmart-sysinfo
echosmart-sysinfo --version
```

### Instalación desde archivo local (e.g., tarjeta SD de producción)

```bash
# Copiar el .deb a la RPi:
scp echosmart-gateway_1.0.0-1_arm64.deb pi@raspberrypi.local:~/

# En la RPi:
sudo dpkg -i ~/echosmart-gateway_1.0.0-1_arm64.deb
sudo apt-get install -f
```

---

## Configuración post-instalación

### 1. Editar el archivo de entorno

```bash
sudo nano /etc/echosmart/gateway.env
```

Configurar las variables mínimas:

```bash
# Identificador único del gateway (usar serial de la RPi):
GATEWAY_ID=gw-$(cat /proc/cpuinfo | grep Serial | awk '{print $3}' | tail -c 9)

# URL de la API Cloud:
CLOUD_API_URL=https://api.echosmart.io

# API key (generar en dashboard EchoSmart → Gateways → Nuevo):
CLOUD_API_KEY=es_live_xxxxxxxxxxxxxxxxxxxxxxxx

# Modo real (no simulación):
SIMULATION_MODE=false
```

### 2. Verificar interfaces de hardware

```bash
# I2C:
ls /dev/i2c-*
# → /dev/i2c-1  ← debe existir

# I2C devices (requiere i2c-tools):
i2cdetect -y 1
# → BH1750: 0x23 o 0x5C
# → ADS1115: 0x48

# 1-Wire:
ls /sys/bus/w1/devices/
# → 28-XXXXXXXXXXXX  ← DS18B20

# UART:
ls /dev/ttyAMA*
# → /dev/ttyAMA0  ← para MH-Z19C
```

> **NOTA**: Si las interfaces no aparecen, **reiniciar la RPi** (el `postinst` modifica
> `/boot/firmware/config.txt` y los cambios requieren reboot).

```bash
sudo reboot
```

### 3. Iniciar el servicio

```bash
sudo systemctl start echosmart-gateway
sudo systemctl status echosmart-gateway
```

---

## Gestión del servicio systemd

```bash
# Estado del servicio
sudo systemctl status echosmart-gateway

# Iniciar
sudo systemctl start echosmart-gateway

# Detener
sudo systemctl stop echosmart-gateway

# Reiniciar (tras cambios en gateway.env)
sudo systemctl restart echosmart-gateway

# Habilitar inicio automático (ya habilitado por postinst)
sudo systemctl enable echosmart-gateway

# Deshabilitar inicio automático
sudo systemctl disable echosmart-gateway

# Ver logs en tiempo real
sudo journalctl -u echosmart-gateway -f

# Ver últimas 100 líneas de logs
sudo journalctl -u echosmart-gateway -n 100

# Ver logs desde el último arranque
sudo journalctl -u echosmart-gateway -b
```

### Recargar configuración sin reinicio

```bash
# Editar /etc/echosmart/gateway.env
sudo nano /etc/echosmart/gateway.env

# Recargar el servicio (aplica nuevas variables de entorno)
sudo systemctl restart echosmart-gateway
```

---

## Actualización del paquete

```bash
# Si tienes el nuevo .deb:
sudo dpkg -i echosmart-gateway_1.1.0-1_arm64.deb
sudo apt-get install -f

# El postinst de la nueva versión:
# 1. Detiene el servicio (via prerm del paquete viejo)
# 2. Actualiza los archivos
# 3. Actualiza dependencias Python
# 4. Reinicia el servicio
```

### Con repositorio APT privado (futuro)

```bash
# Añadir repositorio EchoSmart:
echo "deb [signed-by=/usr/share/keyrings/echosmart.gpg] \
    https://apt.echosmart.io/stable/ bookworm main" | \
    sudo tee /etc/apt/sources.list.d/echosmart.list

# Actualizar e instalar:
sudo apt-get update
sudo apt-get upgrade echosmart-gateway
```

---

## Desinstalación

```bash
# Desinstalar (mantiene configuración y datos):
sudo dpkg -r echosmart-gateway

# Desinstalar y eliminar archivos de configuración:
sudo dpkg --purge echosmart-gateway

# Eliminar datos manualmente (IRREVERSIBLE):
sudo rm -rf /var/lib/echosmart/
sudo rm -rf /etc/echosmart/
sudo userdel echosmart 2>/dev/null || true
```

---

## CI/CD — Build automático

El workflow `.github/workflows/build-deb.yml` automatiza el build del `.deb`:

### Trigger manual

```bash
# Desde GitHub CLI:
gh workflow run build-deb.yml
```

### Trigger por tag (release)

```bash
# Crear y publicar un tag de versión:
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions:
# 1. Instala cross-compiler aarch64-linux-gnu
# 2. Cross-compila C++ para arm64
# 3. Construye .deb con dpkg-buildpackage
# 4. Crea GitHub Release con el .deb adjunto
```

### Artefactos generados en CI

```
echosmart-gateway_1.0.0-1_arm64.deb
echosmart-gateway_1.0.0-1_arm64.buildinfo
echosmart-gateway_1.0.0-1_arm64.changes
```

---

## Troubleshooting

### El servicio no arranca tras la instalación

```bash
# Ver logs de error:
sudo journalctl -u echosmart-gateway -b --no-pager

# Causas comunes:
# 1. Falta el archivo gateway.env → copiarlo:
sudo cp /etc/echosmart/gateway.env.example /etc/echosmart/gateway.env
sudo chown echosmart:echosmart /etc/echosmart/gateway.env

# 2. El venv no se creó correctamente → recrear:
sudo rm -rf /opt/echosmart/gateway/venv
sudo -u echosmart python3 -m venv /opt/echosmart/gateway/venv
sudo -u echosmart /opt/echosmart/gateway/venv/bin/pip install \
    -r /opt/echosmart/gateway/requirements.txt

# 3. Reiniciar:
sudo systemctl restart echosmart-gateway
```

### I2C no detecta sensores

```bash
# Verificar que I2C está habilitado:
grep "dtparam=i2c_arm=on" /boot/firmware/config.txt
# Si no aparece, agregarlo y reiniciar

# Verificar módulo del kernel:
lsmod | grep i2c_bcm2835
# Si no carga: sudo modprobe i2c_bcm2835

# Escanear bus I2C:
i2cdetect -y 1
# BH1750: debe aparecer en 0x23 o 0x5C
# ADS1115: debe aparecer en 0x48
```

### DS18B20 no aparece en /sys/bus/w1/

```bash
# Verificar overlay en config.txt:
grep "dtoverlay=w1-gpio" /boot/firmware/config.txt

# Verificar módulo:
lsmod | grep w1
sudo modprobe w1-therm w1-gpio

# Listar dispositivos:
ls /sys/bus/w1/devices/
```

### MH-Z19C no responde (timeout)

```bash
# Verificar que UART está habilitado:
grep "enable_uart=1" /boot/firmware/config.txt

# Verificar puerto:
ls /dev/ttyAMA*

# Verificar permisos (el usuario echosmart debe estar en el grupo dialout):
id echosmart | grep dialout
# Si no: sudo usermod -aG dialout echosmart

# Test manual:
echosmart-sensor-read mhz19c /dev/ttyAMA0
```

### Error "dpkg: error: mismatch in expected present files"

```bash
# Limpiar estado dpkg inconsistente:
sudo dpkg --configure -a
sudo apt-get install -f
```

### Verificar archivos instalados

```bash
# Listar todos los archivos del paquete:
dpkg -L echosmart-gateway

# Verificar integridad de archivos instalados:
dpkg -V echosmart-gateway
```

---

*Documentación técnica EchoSmart Gateway v1.0.0 — Última actualización: 25 de marzo de 2026*
