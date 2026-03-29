# EchoSmart Gateway — Empaquetado .deb

> Guía para construir, instalar y distribuir el paquete `.deb` del EchoSmart Gateway en Raspberry Pi OS (64-bit).

---

## 1. Contenido del Paquete

El paquete `echosmart-gateway_<version>_arm64.deb` instala:

| Archivo instalado | Descripción |
|-------------------|-------------|
| `/usr/bin/echosmart-gateway` | CLI y wrapper del daemon |
| `/usr/bin/echosmart-gateway-setup` | Asistente interactivo de configuración |
| `/usr/bin/echosmart-sysinfo` | Binario C nativo para diagnóstico del sistema |
| `/opt/echosmart/gateway/` | Código Python + virtualenv |
| `/lib/systemd/system/echosmart-gateway.service` | Servicio systemd |
| `/etc/echosmart/gateway.env.example` | Plantilla de configuración |

---

## 2. Pre-requisitos para Compilar

### 2.1 En la Raspberry Pi (compilación nativa)

```bash
sudo apt update
sudo apt install -y dpkg-dev debhelper devscripts build-essential \
    python3 python3-pip python3-venv gcc git
```

### 2.2 Cross-compilación en x86-64 (Ubuntu 22.04)

```bash
sudo apt update
sudo apt install -y dpkg-dev debhelper devscripts build-essential \
    python3 python3-pip python3-venv gcc-aarch64-linux-gnu git
```

> Para cross-compilar el binario C, cambiar el compilador en `gateway/debian/rules`:
> ```
> CC = aarch64-linux-gnu-gcc
> ```

---

## 3. Construir el Paquete .deb

### 3.1 Desde el repositorio

```bash
# Clonar el repositorio
git clone https://github.com/Uaemextop/echosmart.git
cd echosmart

# Opción A — Con Make (recomendado)
make deb

# Opción B — Manual
cd gateway
dpkg-buildpackage -us -uc -b --build=binary
```

El archivo `.deb` se genera en el directorio padre:
```
echosmart-gateway_1.0.0-1_arm64.deb
```

### 3.2 Con GitHub Actions (CI/CD)

El workflow `.github/workflows/build-deb.yml` se activa automáticamente al:
- Crear un tag `v*` en GitHub (ej: `git tag v1.0.0 && git push --tags`)
- Ejecución manual desde la pestaña "Actions" del repositorio

El artefacto `.deb` se adjunta al Release de GitHub correspondiente.

---

## 4. Instalar el Paquete en la Raspberry Pi

### 4.1 Instalación directa

```bash
# Desde el archivo descargado
sudo dpkg -i echosmart-gateway_1.0.0-1_arm64.deb

# Resolver dependencias si dpkg reporta errores
sudo apt install -f
```

### 4.2 Desde el repositorio de paquetes (futuro)

```bash
# Agregar el repositorio EchoSmart (próximamente)
echo "deb [signed-by=/usr/share/keyrings/echosmart.gpg] \
  https://packages.echosmart.io/apt stable main" | \
  sudo tee /etc/apt/sources.list.d/echosmart.list

sudo apt update
sudo apt install echosmart-gateway
```

---

## 5. Configuración Post-Instalación

### 5.1 Asistente interactivo (recomendado)

```bash
sudo echosmart-gateway-setup
```

El asistente solicita:
1. URL del backend cloud (o IP del servidor on-premise)
2. API Key del gateway (obtenida en el dashboard → Gateways → Nuevo)
3. ID y nombre del gateway
4. Configuración del broker MQTT
5. Intervalos de polling y sincronización

### 5.2 Configuración manual

```bash
# Copiar la plantilla
sudo cp /etc/echosmart/gateway.env.example /etc/echosmart/gateway.env

# Editar la configuración
sudo nano /etc/echosmart/gateway.env

# Recargar y reiniciar el servicio
sudo systemctl daemon-reload
sudo systemctl restart echosmart-gateway
```

**Opciones de configuración** (`/etc/echosmart/gateway.env`):

```bash
GATEWAY_ID=gw-001                          # Identificador único
GATEWAY_NAME=Invernadero Principal         # Nombre descriptivo
CLOUD_API_URL=https://api.echosmart.io     # URL del backend
CLOUD_API_KEY=<tu-api-key>                 # Clave de autenticación
MQTT_BROKER=localhost                      # Broker MQTT
MQTT_PORT=1883                             # Puerto MQTT
POLLING_INTERVAL=60                        # Segundos entre lecturas
SYNC_INTERVAL=300                          # Segundos entre sincronizaciones
SIMULATION_MODE=false                      # true = sin hardware real
LOG_LEVEL=INFO                             # DEBUG|INFO|WARNING|ERROR
```

---

## 6. Comandos CLI

```bash
# Iniciar el gateway manualmente (el servicio systemd lo hace automáticamente)
echosmart-gateway run

# Iniciar en modo simulación (sin hardware real)
echosmart-gateway run --simulate

# Ver estado y configuración actual
echosmart-gateway status

# Probar conectividad de los sensores físicos
echosmart-gateway test-sensors

# Mostrar versión instalada
echosmart-gateway version
```

---

## 7. Gestión del Servicio systemd

```bash
# Ver estado del servicio
sudo systemctl status echosmart-gateway

# Ver logs en tiempo real
journalctl -u echosmart-gateway -f

# Ver últimas 100 líneas de log
journalctl -u echosmart-gateway -n 100

# Reiniciar el servicio
sudo systemctl restart echosmart-gateway

# Habilitar inicio automático
sudo systemctl enable echosmart-gateway

# Deshabilitar inicio automático
sudo systemctl disable echosmart-gateway
```

---

## 8. Diagnóstico con echosmart-sysinfo

El binario nativo `echosmart-sysinfo` (compilado en C) proporciona información del sistema sin necesidad de Python:

```bash
# Información completa del sistema en JSON
echosmart-sysinfo

# Ejemplo de salida:
# {
#   "version": "1.0.0",
#   "hostname": "echosmart-gw-001",
#   "os": "Linux 6.1.0-rpi7-rpi-v8",
#   "arch": "aarch64",
#   "uptime_s": 3600,
#   "cpu_temp_c": 48.5,
#   "ram_total_mb": 3944,
#   "ram_free_mb": 2841,
#   "disk_total_mb": 29318,
#   "disk_free_mb": 22145
# }

# Verificar salud del sistema (código 0=OK, 1=problema)
echosmart-sysinfo --check

# Mostrar versión del binario
echosmart-sysinfo --version
```

---

## 9. Desinstalar

```bash
# Desinstalar (mantiene /etc/echosmart/gateway.env)
sudo dpkg -r echosmart-gateway

# Purgar completamente (elimina también la configuración)
sudo dpkg -P echosmart-gateway
```

---

## 10. Resolución de Problemas

| Síntoma | Causa probable | Solución |
|---------|----------------|---------|
| `systemctl status` muestra `failed` | API Key incorrecta o servidor no accesible | Revisar `CLOUD_API_URL` y `CLOUD_API_KEY` en gateway.env |
| Lecturas de sensores = 0 o null | Sensor no conectado o dirección I2C incorrecta | Ejecutar `echosmart-gateway test-sensors` |
| Error `ModuleNotFoundError` | Dependencias Python no instaladas | `sudo apt install -f` |
| CPU temp > 80°C | Ventilación insuficiente | Verificar ventilador de la carcasa |
| Disco lleno | Logs acumulados | `journalctl --vacuum-size=100M` |

---

*Última actualización: Marzo 2026 — EchoSmart Dev Team*
