# EchoSmart Gateway — Empaquetado .deb

> Guía para construir, distribuir e instalar el paquete .deb del gateway.

## Estructura del Paquete

```
echosmart-gateway_1.0.0_all.deb
├── /opt/echosmart/gateway/          ← Código Python del gateway
│   ├── src/                         ← Clean Architecture (domain/app/infra)
│   ├── requirements.txt
│   └── sensors.json
├── /usr/bin/
│   ├── echosmart-gateway            ← CLI wrapper
│   └── echosmart-gateway-setup      ← Setup wizard
├── /lib/systemd/system/
│   └── echosmart-gateway.service    ← Servicio systemd
└── /etc/echosmart/
    └── gateway.env.example          ← Plantilla de configuración
```

## Construir el Paquete (Desarrolladores)

### Prerequisitos

```bash
sudo apt install debhelper devscripts dpkg-dev build-essential
```

### Build con Makefile (recomendado)

```bash
make deb
```

### Build manual

```bash
cd gateway
dpkg-buildpackage -us -uc -b
ls ../echosmart-gateway_*.deb
```

El .deb se genera en el directorio padre (`../`).

---

## Instalar el Paquete (Raspberry Pi)

### Opción 1: Instalación directa desde archivo

```bash
sudo dpkg -i echosmart-gateway_1.0.0_all.deb
sudo echosmart-gateway-setup
```

### Opción 2: Instalación desde repositorio APT (futuro)

```bash
# Agregar repositorio EchoSmart
curl -fsSL https://apt.echosmart.io/gpg.key | sudo apt-key add -
echo "deb https://apt.echosmart.io stable main" | sudo tee /etc/apt/sources.list.d/echosmart.list
sudo apt update
sudo apt install echosmart-gateway
sudo echosmart-gateway-setup
```

---

## Gestión del Servicio

```bash
# Estado del servicio
sudo systemctl status echosmart-gateway

# Ver logs en tiempo real
journalctl -u echosmart-gateway -f

# Reiniciar gateway
sudo systemctl restart echosmart-gateway

# Detener gateway
sudo systemctl stop echosmart-gateway
```

---

## CLI de Administración

```bash
# Ver versión
echosmart-gateway version

# Ver estado y configuración actual
echosmart-gateway status

# Probar todos los sensores
echosmart-gateway test-sensors

# Iniciar gateway en modo simulación
echosmart-gateway run --simulate
```

---

## Actualización

```bash
# Descargar nueva versión
wget https://github.com/Uaemextop/echosmart/releases/latest/download/echosmart-gateway_latest_all.deb

# Instalar (conserva configuración en /etc/echosmart/gateway.env)
sudo dpkg -i echosmart-gateway_latest_all.deb
sudo systemctl restart echosmart-gateway
```

---

## Desinstalar

```bash
# Desinstalar conservando configuración
sudo dpkg -r echosmart-gateway

# Desinstalar limpiando TODO (incluyendo /etc/echosmart/)
sudo dpkg --purge echosmart-gateway
```

---

## Repositorio APT Propio (Producción en Masa)

Para distribución comercial, crear un repositorio APT propio con `reprepro`:

```bash
# En servidor de distribución
sudo apt install reprepro gnupg

# Crear estructura del repositorio
mkdir -p /srv/apt-repo/{conf,pool}
cat > /srv/apt-repo/conf/distributions <<EOF
Origin: EchoSmart
Label: EchoSmart
Codename: stable
Architectures: armhf arm64 amd64 all
Components: main
Description: EchoSmart IoT Package Repository
SignWith: YOUR_GPG_KEY_ID
EOF

# Agregar paquete al repositorio
reprepro -b /srv/apt-repo includedeb stable echosmart-gateway_1.0.0_all.deb

# Servir con nginx
sudo ln -s /srv/apt-repo /var/www/html/apt
```

---

*Última actualización: Marzo 2026 — EchoSmart Team*
