# EchoSmart — Gateway (Raspberry Pi)

Software de edge computing para la Raspberry Pi del invernadero.

## Stack

- **Hardware**: Raspberry Pi 4B (4 GB RAM)
- **Lenguaje**: Python 3.9+
- **Base de datos local**: SQLite
- **MQTT**: Mosquitto
- **Sensores**: DS18B20, DHT22, BH1750, Soil Moisture, MHZ-19C

## Inicio Rápido

```bash
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## Modo Simulación

Para desarrollo sin hardware real:

```bash
SIMULATION_MODE=true python main.py
```

## Tests

```bash
pytest tests/ -v --cov=src
```

## Estructura

```
gateway/
├── main.py                    # Orquestador principal
├── sensors.json               # Configuración de sensores
├── echosmart-gateway.service  # Servicio systemd
├── src/
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
