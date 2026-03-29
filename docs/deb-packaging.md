# EchoSmart Gateway — Debian Package (.deb)

> Cómo compilar, instalar y mantener el paquete `.deb` del gateway
> en Raspberry Pi OS (Debian 12 Bookworm arm64).

---

## 1. Requisitos de compilación

```bash
sudo apt-get update
sudo apt-get install -y dpkg-dev debhelper python3 python3-venv python3-pip
```

---

## 2. Compilar el paquete

```bash
# Desde la raíz del repositorio
cd gateway
dpkg-buildpackage -us -uc -b
```

El archivo `.deb` se genera en el directorio padre:

```
../echosmart-gateway_1.0.0-1_all.deb
```

O usando el Makefile de la raíz:

```bash
make deb
```

---

## 3. Instalar en una Raspberry Pi

```bash
sudo dpkg -i echosmart-gateway_1.0.0-1_all.deb
sudo apt-get install -f   # resolver dependencias si falta algo
```

### Qué instala el paquete

| Ruta                                    | Descripción                          |
|-----------------------------------------|--------------------------------------|
| `/opt/echosmart/gateway/`               | Código fuente del gateway (Python)   |
| `/opt/echosmart/gateway/venv/`          | Virtual environment (creado por postinst) |
| `/usr/bin/echosmart-gateway`            | CLI principal (wrapper bash → Python)|
| `/usr/bin/echosmart-gateway-setup`      | Wizard de configuración inicial      |
| `/etc/echosmart/gateway.env`            | Archivo de configuración             |
| `/lib/systemd/system/echosmart-gateway.service` | Unidad systemd           |

---

## 4. Configuración inicial

```bash
sudo echosmart-gateway-setup
```

El wizard interactivo solicita:

- Gateway ID
- Nombre del gateway
- URL de la API cloud
- API key
- Broker MQTT
- Intervalo de polling
- Modo simulación (sí / no)

La configuración se guarda en `/etc/echosmart/gateway.env`.

---

## 5. Gestión del servicio

```bash
# Iniciar
sudo systemctl start echosmart-gateway

# Ver estado
sudo systemctl status echosmart-gateway

# Ver logs en tiempo real
sudo journalctl -u echosmart-gateway -f

# Detener
sudo systemctl stop echosmart-gateway

# Habilitar al arranque
sudo systemctl enable echosmart-gateway
```

---

## 6. CLI — Comandos disponibles

```bash
echosmart-gateway run [--simulate]    # Ejecutar el gateway
echosmart-gateway status              # Mostrar configuración actual
echosmart-gateway test-sensors        # Auto-test de los 5 drivers
echosmart-gateway version             # Mostrar versión
```

---

## 7. Desinstalar

```bash
sudo dpkg -r echosmart-gateway
```

Esto detiene el servicio, desactiva la unidad systemd y elimina el
virtualenv. La configuración en `/etc/echosmart/` se conserva.

---

## 8. CI/CD — Compilación automática

El workflow `.github/workflows/build-deb.yml` compila el `.deb` en cada
tag `v*` y lo adjunta como asset del release en GitHub:

```yaml
on:
  push:
    tags: ['v*']
```

Para crear un release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 9. Estructura del paquete Debian

```
gateway/debian/
├── changelog            # Historial de versiones
├── compat               # Nivel de compatibilidad debhelper
├── control              # Metadatos del paquete
├── echosmart-gateway.service  # Unidad systemd
├── postinst             # Script post-instalación (crea venv)
├── prerm                # Script pre-desinstalación (detiene servicio)
└── rules                # Reglas de compilación
```
