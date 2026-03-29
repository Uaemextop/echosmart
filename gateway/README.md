# EchoSmart — Gateway (Raspberry Pi)

Software de edge computing para la Raspberry Pi del invernadero.

## Stack

- **Hardware**: Raspberry Pi 4B (4 GB RAM)
- **Lenguaje**: Python 3.9+
- **Base de datos local**: SQLite
- **MQTT**: Mosquitto
- **Sensores**: DS18B20, DHT22, BH1750, Soil Moisture, MHZ-19C
- **Packaging**: `.deb` para Raspberry Pi OS

## Inicio Rápido (Desarrollo)

```bash
pip install -r requirements.txt
cp .env.example .env
python src/cli.py run --simulate
```

## CLI

```bash
echosmart-gateway run [--simulate]   # Iniciar el gateway
echosmart-gateway status             # Ver configuración actual
echosmart-gateway test-sensors       # Diagnóstico de sensores
echosmart-gateway version            # Versión del gateway
```

## Instalación con .deb (Producción)

```bash
sudo dpkg -i echosmart-gateway_1.0.0-1_armhf.deb
sudo echosmart-gateway-setup
```

Más detalles: [docs/deb-packaging.md](../docs/deb-packaging.md)

## Tests

```bash
pytest tests/ -v --cov=src
```

## Construir .deb

```bash
dpkg-buildpackage -us -uc -b
# O desde la raíz del proyecto:
make deb
```

## Estructura

```
gateway/
├── main.py                    # Orquestador principal
├── sensors.json               # Configuración de sensores
├── echosmart-gateway.service  # Servicio systemd (producción)
├── bin/
│   ├── echosmart-gateway      # Wrapper bash → CLI Python
│   └── echosmart-gateway-setup # Wizard de configuración
├── debian/
│   ├── control                # Metadatos del paquete .deb
│   ├── rules                  # Reglas de construcción
│   ├── postinst               # Post-instalación
│   ├── prerm                  # Pre-remoción
│   ├── changelog              # Historial de versiones
│   └── echosmart-gateway.service # Servicio systemd
├── src/
│   ├── cli.py                 # CLI entry point
│   ├── config.py              # Configuración
│   ├── hal.py                 # Hardware Abstraction Layer
│   ├── sensor_manager.py      # Gestión de sensores
│   ├── alert_engine.py        # Motor de alertas local
│   ├── cloud_sync.py          # Sincronización con cloud
│   ├── mqtt_publisher.py      # Publicador MQTT
│   ├── discovery.py           # Auto-descubrimiento SSDP
│   ├── local_db.py            # Caché SQLite
│   └── sensor_drivers/        # Drivers por sensor
│       ├── ds18b20.py
│       ├── dht22.py
│       ├── bh1750.py
│       ├── soil_moisture.py
│       └── mhz19c.py
└── tests/
```
