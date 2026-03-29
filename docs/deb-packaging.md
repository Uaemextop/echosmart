# EchoSmart — Empaquetado .deb

Guía completa para construir, instalar y mantener el paquete
`echosmart-gateway` para Raspberry Pi OS (arm64).

---

## 1. Estructura del Paquete

```
gateway/
├── cpp/                            # Código fuente C++
│   ├── CMakeLists.txt              # Build system
│   ├── echosmart-gateway.cpp       # Daemon principal
│   ├── echosmart-sysinfo.cpp       # Diagnósticos del sistema
│   └── echosmart-sensor-read.cpp   # Lectura de sensores
├── bin/                            # Scripts wrapper
│   ├── echosmart-gateway           # Wrapper del daemon
│   └── echosmart-gateway-setup     # Wizard de primer arranque
├── debian/                         # Metadatos Debian
│   ├── control                     # Nombre, dependencias, descripción
│   ├── rules                       # Instrucciones de build (cmake)
│   ├── changelog                   # Historial de versiones
│   ├── compat                      # Nivel de compatibilidad (13)
│   ├── postinst                    # Script post-instalación
│   ├── prerm                       # Script pre-remoción
│   └── echosmart-gateway.service   # Unidad systemd
├── sensors.json                    # Config de sensores por defecto
└── .env.example                    # Variables de entorno por defecto
```

---

## 2. Construir el .deb

### 2.1 Requisitos

```bash
sudo apt install build-essential cmake debhelper devscripts fakeroot
# Para cross-compilación arm64 desde x86_64:
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
```

### 2.2 Build Nativo (en Raspberry Pi)

```bash
cd gateway
dpkg-buildpackage -b -us -uc
# Resultado: ../echosmart-gateway_1.0.0-1_arm64.deb
```

### 2.3 Build en CI (cross-compilación)

```bash
cd gateway
dpkg-buildpackage -b -us -uc --host-arch=arm64
# Resultado: ../echosmart-gateway_1.0.0-1_arm64.deb
```

### 2.4 Build con Make

```bash
make deb    # Equivalente a cd gateway && dpkg-buildpackage
```

---

## 3. Instalar el .deb

```bash
sudo dpkg -i echosmart-gateway_1.0.0-1_arm64.deb
# O con resolución automática de dependencias:
sudo apt install ./echosmart-gateway_1.0.0-1_arm64.deb
```

### Archivos Instalados

| Ruta | Descripción |
|------|-------------|
| `/usr/bin/echosmart-gateway` | Wrapper shell del daemon |
| `/usr/bin/echosmart-gateway-bin` | Binario C++ del daemon |
| `/usr/bin/echosmart-sysinfo` | Diagnósticos del sistema |
| `/usr/bin/echosmart-sensor-read` | Lectura de sensores |
| `/usr/bin/echosmart-gateway-setup` | Wizard de configuración |
| `/etc/echosmart/gateway.env` | Configuración del gateway |
| `/etc/echosmart/sensors.json` | Definición de sensores |
| `/lib/systemd/system/echosmart-gateway.service` | Unidad systemd |

---

## 4. Primer Arranque

```bash
# 1. Ejecutar el wizard de configuración
sudo echosmart-gateway-setup

# 2. Activar el servicio
sudo systemctl enable --now echosmart-gateway

# 3. Verificar estado
sudo systemctl status echosmart-gateway
journalctl -u echosmart-gateway -f
```

---

## 5. Comandos Útiles

```bash
# Diagnósticos del sistema
echosmart-sysinfo

# Leer un sensor específico (simulado)
echosmart-sensor-read ds18b20 --simulate

# Leer todos los sensores con un solo ciclo (simulado)
echosmart-gateway --simulate --once

# Ver logs del servicio
journalctl -u echosmart-gateway --since today

# Reiniciar el servicio
sudo systemctl restart echosmart-gateway

# Desinstalar
sudo apt remove echosmart-gateway
```

---

## 6. Actualización

```bash
# Descargar nueva versión
wget https://releases.echosmart.io/echosmart-gateway_1.1.0-1_arm64.deb

# Instalar sobre la versión anterior
sudo dpkg -i echosmart-gateway_1.1.0-1_arm64.deb

# El servicio se reinicia automáticamente
sudo systemctl status echosmart-gateway
```

---

## 7. Troubleshooting

| Síntoma | Causa probable | Solución |
|---------|---------------|----------|
| `echosmart-gateway-bin: not found` | .deb no instalado | `sudo dpkg -i echosmart-gateway*.deb` |
| Servicio `inactive (dead)` | Setup no ejecutado | `sudo echosmart-gateway-setup` |
| `No DS18B20 device found` | 1-Wire no habilitado | `echo "dtoverlay=w1-gpio" >> /boot/config.txt && reboot` |
| `cannot open /dev/i2c-1` | I2C no habilitado | `sudo raspi-config` → Interfaces → I2C → Enable |
| `cannot open /dev/serial0` | UART no habilitado | `sudo raspi-config` → Interfaces → Serial → Enable |
| Lecturas siempre 0.0 | Sensor desconectado | Verificar cableado con diagrama GPIO |

---

*Volver al [Índice de Documentación](README.md)*
