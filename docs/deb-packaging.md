# EchoSmart Gateway — Empaquetado .deb

> Guía para construir, instalar y distribuir el paquete Debian del gateway EchoSmart.

---

## 1. Visión General

El gateway EchoSmart se distribuye como un paquete `.deb` estándar de Debian/Ubuntu compatible con Raspberry Pi OS (Bookworm, arm64). Esto permite:

- Instalación con un solo comando (`dpkg -i` / `apt install`)
- Gestión de dependencias automática
- Actualización vía `apt-get upgrade`
- Desinstalación limpia (`apt-get remove`)
- Integración con systemd (inicio automático)

### Archivos instalados

```
/opt/echosmart/gateway/        ← Código fuente y virtualenv
/usr/bin/echosmart-gateway     ← CLI principal
/usr/bin/echosmart-gateway-setup ← Wizard de configuración
/etc/echosmart/gateway.env     ← Archivo de configuración
/lib/systemd/system/echosmart-gateway.service ← Servicio systemd
```

---

## 2. Requisitos para construir el .deb

### En la máquina de build (Ubuntu/Debian x86_64 o arm64):

```bash
sudo apt-get install dpkg-dev debhelper dh-python python3-all
```

### En CI (GitHub Actions):

El workflow `.github/workflows/build-deb.yml` se ejecuta automáticamente al crear un tag `v*` o al modificar archivos en `gateway/`.

---

## 3. Construir el paquete localmente

```bash
# Desde la raíz del repositorio
cd gateway
dpkg-buildpackage -us -uc -b

# El .deb se genera en el directorio padre
ls ../echosmart-gateway_*.deb
```

O usando el Makefile raíz:

```bash
make deb
```

---

## 4. Estructura del empaquetado Debian

```
gateway/debian/
├── changelog        ← Historial de versiones (formato Debian)
├── compat           ← Nivel de compatibilidad debhelper
├── control          ← Metadatos del paquete (nombre, deps, descripción)
├── copyright        ← Información de licencia
├── echosmart-gateway.service ← Servicio systemd (producción)
├── gateway.env.default       ← Configuración por defecto
├── postinst         ← Script post-instalación (crea user, venv, deps)
├── prerm            ← Script pre-remoción (detiene servicio)
└── rules            ← Reglas de construcción (Makefile de Debian)
```

---

## 5. Instalar en Raspberry Pi

### Desde un release de GitHub:

```bash
# Descargar
wget https://github.com/Uaemextop/echosmart/releases/latest/download/echosmart-gateway_1.0.0-1_all.deb

# Instalar
sudo dpkg -i echosmart-gateway_1.0.0-1_all.deb
sudo apt-get install -f
```

### Desde el paquete local:

```bash
sudo dpkg -i echosmart-gateway_1.0.0-1_all.deb
sudo apt-get install -f
```

### Post-instalación:

```bash
# 1. Configurar
sudo echosmart-gateway-setup

# 2. Verificar
echosmart-gateway status
echosmart-gateway test-sensors

# 3. Iniciar
sudo systemctl start echosmart-gateway
sudo systemctl status echosmart-gateway

# 4. Ver logs
journalctl -u echosmart-gateway -f
```

---

## 6. Desinstalar

```bash
# Remover paquete (conserva configuración)
sudo apt-get remove echosmart-gateway

# Remover paquete y configuración
sudo apt-get purge echosmart-gateway
```

---

## 7. CLI del Gateway

El paquete instala el comando `echosmart-gateway` en `/usr/bin/`:

```bash
echosmart-gateway --help
echosmart-gateway --version

# Comandos disponibles:
echosmart-gateway run              # Iniciar gateway (primer plano)
echosmart-gateway run --simulate   # Forzar modo simulación
echosmart-gateway status           # Mostrar configuración actual
echosmart-gateway test-sensors     # Leer cada sensor una vez
echosmart-gateway version          # Versión del software
```

---

## 8. Configuración

El archivo de configuración es `/etc/echosmart/gateway.env`:

```env
GATEWAY_ID=gw-001
GATEWAY_NAME=Invernadero Principal
CLOUD_API_URL=http://localhost:8000
CLOUD_API_KEY=your-api-key-here
MQTT_BROKER=localhost
MQTT_PORT=1883
POLLING_INTERVAL=60
SYNC_INTERVAL=300
SIMULATION_MODE=true
LOG_LEVEL=INFO
```

Cada variable puede ser sobreescrita por variables de entorno del sistema.

---

## 9. Versionar y publicar una nueva versión

1. Actualizar la versión en `gateway/pyproject.toml`
2. Actualizar `gateway/debian/changelog` (formato `dch`)
3. Crear un tag: `git tag v1.1.0 && git push --tags`
4. El CI construye el `.deb` y lo adjunta al GitHub Release

---

*Última actualización: Marzo 2026*
