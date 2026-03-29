# EchoSmart — Gateway (Raspberry Pi)

Software de edge computing para la Raspberry Pi del invernadero inteligente.
Implementado en **C++17** como binario unificado con Clean Architecture.

## Stack

- **Hardware**: Raspberry Pi 4B (2 GB+ RAM)
- **Lenguaje**: C++17 (estándar, sin dependencias externas)
- **Build**: CMake ≥ 3.16 + g++ ≥ 10
- **Empaquetado**: .deb (dpkg-buildpackage, arm64/amd64)
- **Sensores**: DS18B20, DHT22, BH1750, Soil Moisture, MH-Z19C

## Compilación

```bash
# Configurar y compilar
cmake -S cpp -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel

# Ejecutar tests
ctest --test-dir build --output-on-failure
```

## Uso del Binario Unificado

```bash
echosmart <command> [input] [--options]
```

### Tabla de Comandos

| Comando | Input | Argumentos | Descripción |
|---------|-------|------------|-------------|
| `read` | `<sensor>` | `--simulate=true`, `--format=json` | Leer un sensor |
| `sysinfo` | — | `--format=json\|text` | Diagnósticos del sistema |
| `run` | — | `--config=<path>`, `--sensors=<path>`, `--simulate=true`, `--once=true`, `--interval=<sec>` | Ejecutar daemon de polling |
| `setup` | — | `--config=<path>` | Wizard de configuración |
| `status` | — | `--format=json\|text` | Estado del gateway |
| `calibrate` | `<sensor>` | `--dry=<val>`, `--wet=<val>` | Calibrar sensor |
| `list` | — | `--format=json\|text` | Listar sensores configurados |
| `test` | `<sensor>\|all` | `--simulate=true` | Probar drivers de sensores |
| `version` | — | — | Mostrar versión |
| `help` | `[command]` | — | Mostrar ayuda |

### Ejemplos

```bash
echosmart read ds18b20 --simulate=true    # Lectura simulada de temperatura
echosmart sysinfo                          # Diagnósticos del sistema
echosmart run --simulate=true --once=true  # Un ciclo de polling simulado
echosmart test all --simulate=true         # Probar todos los sensores
echosmart list                             # Listar sensores configurados
echosmart version                          # Mostrar versión
```

## Modo Simulación

Todo binario soporta `--simulate=true` para desarrollo sin hardware:

```bash
echosmart run --simulate=true --interval=10
```

## Arquitectura (Clean Architecture)

```
gateway/cpp/
├── main.cpp                      # Entry point → dispatch de comandos
├── cli.h / cli.cpp               # Parser CLI: echosmart <cmd> [input] [--opts]
│
├── shared/                       # Capa 0: Tipos y utilidades compartidas
│   ├── version.h                 # Constantes de versión
│   ├── sensor_data.h/.cpp        # Struct SensorData + serialización JSON
│   ├── alert_rule.h/.cpp         # Struct AlertRule + evaluación
│   ├── json_formatter.h/.cpp     # Funciones JSON sin dependencias
│   ├── config_loader.h/.cpp      # Parser de .env y sensors.json
│   ├── logger.h/.cpp             # Logging ISO 8601 por niveles
│   └── file_utils.h/.cpp         # I/O de archivos, trim, split, hostname
│
├── drivers/                      # Capa 1: Abstracción de hardware
│   ├── sensor_driver.h/.cpp      # Clase base abstracta SensorDriver
│   ├── driver_factory.h/.cpp     # Factory: string → SensorDriver
│   ├── ds18b20_driver.h/.cpp     # 1-Wire (temperatura)
│   ├── dht22_driver.h/.cpp       # GPIO (temp + humedad)
│   ├── bh1750_driver.h/.cpp      # I2C (luminosidad)
│   ├── soil_driver.h/.cpp        # ADS1115/I2C (humedad suelo)
│   └── mhz19c_driver.h/.cpp      # UART (CO₂)
│
├── core/                         # Capa 2: Lógica de negocio del daemon
│   ├── gateway.h/.cpp            # Orquestador: poll → evaluate → store
│   ├── sensor_poller.h/.cpp      # Polling de sensores via DriverFactory
│   ├── alert_engine.h/.cpp       # Evaluación de reglas + cooldown
│   └── data_store.h/.cpp         # Persistencia JSONL rotativa
│
├── commands/                     # Capa 3: Comandos CLI
│   ├── cmd_read.h/.cpp           # echosmart read <sensor>
│   ├── cmd_sysinfo.h/.cpp        # echosmart sysinfo
│   ├── cmd_run.h/.cpp            # echosmart run (daemon)
│   ├── cmd_setup.h/.cpp          # echosmart setup (wizard)
│   ├── cmd_status.h/.cpp         # echosmart status
│   ├── cmd_calibrate.h/.cpp      # echosmart calibrate
│   ├── cmd_list.h/.cpp           # echosmart list
│   ├── cmd_test.h/.cpp           # echosmart test
│   ├── cmd_version.h/.cpp        # echosmart version
│   └── cmd_help.h/.cpp           # echosmart help
│
└── tests/                        # Tests unitarios (CTest)
    ├── CMakeLists.txt
    ├── test_helpers.h            # Macros ASSERT_*
    ├── test_json_formatter.cpp
    ├── test_sensor_data.cpp
    ├── test_alert_rule.cpp
    ├── test_config_loader.cpp
    ├── test_drivers.cpp
    ├── test_alert_engine.cpp
    ├── test_gateway_cycle.cpp
    └── test_cli.cpp
```

## Tests

```bash
# Compilar con tests
cmake -S cpp -B build -DBUILD_TESTS=ON
cmake --build build --parallel

# Ejecutar
ctest --test-dir build --output-on-failure
```

8 suites de tests: json_formatter, sensor_data, alert_rule, config_loader,
drivers, alert_engine, gateway_cycle, cli (59 tests individuales).

## Empaquetado .deb

```bash
cd gateway
dpkg-buildpackage -b -us -uc           # Build nativo
dpkg-buildpackage -b -us -uc --host-arch=arm64  # Cross-compile ARM64
```

### Contenido del .deb

| Ruta | Descripción |
|------|-------------|
| `/usr/bin/echosmart` | Binario unificado (todos los comandos) |
| `/usr/bin/echosmart-gateway-bin` | Daemon legacy (compatibilidad) |
| `/usr/bin/echosmart-sysinfo` | Diagnósticos legacy |
| `/usr/bin/echosmart-sensor-read` | Lector legacy |
| `/etc/echosmart/gateway.env` | Configuración por defecto |
| `/etc/echosmart/sensors.json` | Definición de sensores |
| `/lib/systemd/system/echosmart-gateway.service` | Unidad systemd |

## Sensores Soportados

| Sensor | Variable | Protocolo | Rango Invernadero | Precio |
|--------|----------|-----------|-------------------|--------|
| DS18B20 | Temperatura | 1-Wire | 18–28°C | ~$2 |
| DHT22 | Temp + Humedad | GPIO | 18–28°C / 60–80% | ~$3 |
| BH1750 | Luminosidad | I2C | 10K–30K lux | ~$1.5 |
| Soil Moisture + ADS1115 | Humedad suelo | I2C | 50–80% | ~$4 |
| MH-Z19C | CO₂ | UART | 400–1000 ppm | ~$18 |
