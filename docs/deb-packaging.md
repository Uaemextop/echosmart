# EchoSmart — Empaquetado .deb del Gateway

Guía para construir, instalar y distribuir el paquete Debian del gateway EchoSmart para Raspberry Pi OS.

---

## Requisitos Previos

```bash
# En la máquina de desarrollo (Debian/Ubuntu)
sudo apt-get install dpkg-dev debhelper python3 python3-venv

# Para cross-compilation ARM (opcional)
sudo apt-get install qemu-user-static
```

---

## Estructura del Paquete

```
gateway/debian/
├── changelog                        # Historial de versiones del paquete
├── compat                           # Nivel de compatibilidad debhelper
├── control                          # Metadatos del paquete (nombre, deps, descripción)
├── echosmart-gateway.service        # Servicio systemd para producción
├── postinst                         # Script post-instalación (crea venv, usuario, habilita servicio)
├── prerm                            # Script pre-remoción (detiene servicio)
└── rules                            # Reglas de construcción (dh_make)
```

---

## Construir el Paquete

### Desde el directorio del gateway

```bash
cd gateway
dpkg-buildpackage -us -uc -b
```

El archivo `.deb` se genera en el directorio padre:

```
../echosmart-gateway_1.0.0-1_armhf.deb
```

### Desde la raíz con Make

```bash
make deb
```

### Desde CI/CD (GitHub Actions)

El workflow `.github/workflows/build-deb.yml` construye automáticamente el `.deb` en cada tag `v*` y lo adjunta como release asset.

---

## Instalar el Paquete

### En una Raspberry Pi

```bash
# Copiar el .deb a la Raspberry Pi
scp echosmart-gateway_1.0.0-1_armhf.deb pi@raspberrypi:/tmp/

# Instalar
ssh pi@raspberrypi
sudo dpkg -i /tmp/echosmart-gateway_1.0.0-1_armhf.deb

# Resolver dependencias si hay errores
sudo apt-get install -f
```

### Primer Arranque

```bash
# Ejecutar el wizard de configuración
sudo echosmart-gateway-setup

# O configurar manualmente
sudo nano /etc/echosmart/gateway.env
sudo systemctl start echosmart-gateway
```

---

## Archivos Instalados

| Ruta | Descripción |
|------|-------------|
| `/opt/echosmart/gateway/` | Código fuente del gateway |
| `/opt/echosmart/gateway/venv/` | Entorno virtual Python (creado en postinst) |
| `/usr/bin/echosmart-gateway` | Binario CLI del gateway |
| `/usr/bin/echosmart-gateway-setup` | Wizard de configuración |
| `/etc/echosmart/gateway.env` | Configuración (variables de entorno) |
| `/lib/systemd/system/echosmart-gateway.service` | Servicio systemd |
| `/var/log/echosmart/` | Directorio de logs |

---

## Gestión del Servicio

```bash
# Estado
sudo systemctl status echosmart-gateway

# Iniciar / Detener / Reiniciar
sudo systemctl start echosmart-gateway
sudo systemctl stop echosmart-gateway
sudo systemctl restart echosmart-gateway

# Ver logs en tiempo real
journalctl -u echosmart-gateway -f

# Deshabilitar arranque automático
sudo systemctl disable echosmart-gateway
```

---

## Comandos CLI

```bash
# Ejecutar en modo simulación
echosmart-gateway run --simulate

# Ver estado de configuración
echosmart-gateway status

# Diagnóstico de sensores
echosmart-gateway test-sensors

# Versión
echosmart-gateway version
```

---

## Desinstalar

```bash
# Desinstalar manteniendo configuración
sudo dpkg -r echosmart-gateway

# Desinstalar eliminando todo (incluida configuración)
sudo dpkg --purge echosmart-gateway
```

---

## Actualizar

```bash
# Descargar nueva versión
wget https://github.com/Uaemextop/echosmart/releases/latest/download/echosmart-gateway_1.1.0-1_armhf.deb

# Instalar (actualiza automáticamente)
sudo dpkg -i echosmart-gateway_1.1.0-1_armhf.deb
sudo apt-get install -f
```

---

## Crear un Repositorio APT Propio (Opcional)

Para distribución masiva, se puede crear un repositorio APT:

```bash
# En el servidor de distribución
mkdir -p /var/www/apt/pool/main
cp echosmart-gateway_*.deb /var/www/apt/pool/main/

# Generar índices
cd /var/www/apt
dpkg-scanpackages pool/ /dev/null | gzip -9c > Packages.gz
```

En la Raspberry Pi del cliente:

```bash
echo "deb [trusted=yes] http://tu-servidor.com/apt ./" | \
    sudo tee /etc/apt/sources.list.d/echosmart.list
sudo apt-get update
sudo apt-get install echosmart-gateway
```

---

*Última actualización: Marzo 2026*
