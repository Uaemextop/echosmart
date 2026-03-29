"""CLI del EchoSmart Gateway."""
import argparse
import json
import sys
import logging

GATEWAY_VERSION = "1.0.0"


def cmd_version(args) -> int:
    """Mostrar versión del gateway."""
    print(f"echosmart-gateway {GATEWAY_VERSION}")
    return 0


def cmd_status(args) -> int:
    """Mostrar estado del gateway."""
    try:
        from .config import config

        status = {
            "version": GATEWAY_VERSION,
            "gateway_id": config.gateway_id,
            "gateway_name": config.gateway_name,
            "simulation_mode": config.simulation_mode,
            "cloud_api_url": config.cloud_api_url,
            "polling_interval": config.polling_interval,
        }
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"Error obteniendo estado: {exc}", file=sys.stderr)
        return 1


def cmd_test_sensors(args) -> int:
    """Probar lectura de todos los sensores registrados."""
    from .infrastructure.drivers.ds18b20 import DS18B20Driver
    from .infrastructure.drivers.dht22 import DHT22Driver
    from .infrastructure.drivers.bh1750 import BH1750Driver
    from .infrastructure.drivers.mhz19c import MHZ19CDriver
    from .infrastructure.drivers.soil_moisture import SoilMoistureDriver
    from .application.sensor_manager import SensorManager

    manager = SensorManager(polling_interval=60)
    manager.register(DS18B20Driver("ds18b20-01", simulation=True))
    manager.register(DHT22Driver("dht22-01", simulation=True))
    manager.register(BH1750Driver("bh1750-01", simulation=True))
    manager.register(MHZ19CDriver("mhz19c-01", simulation=True))
    manager.register(SoilMoistureDriver("soil-01", simulation=True))

    readings = manager.read_all()
    for r in readings:
        status = "ERROR" if r.error else "OK"
        value_str = f"{r.value} {r.unit}" if not r.error else r.error
        print(f"  [{status}] {r.sensor_id} ({r.sensor_type}): {value_str}")
    return 0


def cmd_run(args) -> int:
    """Iniciar el gateway."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger("echosmart-gateway")

    from .config import config

    simulate = args.simulate or config.simulation_mode
    logger.info("Iniciando EchoSmart Gateway v%s", GATEWAY_VERSION)
    logger.info("Gateway ID: %s | Simulación: %s", config.gateway_id, simulate)

    from .infrastructure.drivers.ds18b20 import DS18B20Driver
    from .infrastructure.drivers.dht22 import DHT22Driver
    from .infrastructure.drivers.bh1750 import BH1750Driver
    from .infrastructure.drivers.mhz19c import MHZ19CDriver
    from .infrastructure.drivers.soil_moisture import SoilMoistureDriver
    from .application.sensor_manager import SensorManager
    from .application.alert_engine import AlertEngine

    manager = SensorManager(polling_interval=config.polling_interval)
    manager.register(DS18B20Driver("ds18b20-01", simulation=simulate))
    manager.register(DHT22Driver("dht22-01", simulation=simulate))
    manager.register(BH1750Driver("bh1750-01", simulation=simulate))
    manager.register(MHZ19CDriver("mhz19c-01", simulation=simulate))
    manager.register(SoilMoistureDriver("soil-01", simulation=simulate))

    alert_engine = AlertEngine()
    alert_engine.add_rule(
        {"name": "Temp Alta", "condition": "gt", "threshold": 35.0, "severity": "high"}
    )
    alert_engine.add_rule(
        {"name": "CO2 Alto", "condition": "gt", "threshold": 1500.0, "severity": "medium"}
    )

    logger.info("Gateway inicializado con %d sensores", manager.sensor_count)
    readings = manager.read_all()
    for r in readings:
        logger.info("Lectura: %s = %.1f %s", r.sensor_id, r.value, r.unit)
    logger.info("Gateway corriendo. Ctrl+C para detener.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construir el parser CLI."""
    parser = argparse.ArgumentParser(
        prog="echosmart-gateway",
        description="EchoSmart Gateway — Control CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("version", help="Mostrar versión del gateway")
    subparsers.add_parser("status", help="Mostrar estado y configuración del gateway")
    subparsers.add_parser("test-sensors", help="Probar lectura de todos los sensores")

    run_parser = subparsers.add_parser("run", help="Iniciar el gateway")
    run_parser.add_argument("--simulate", action="store_true", help="Forzar modo simulación")

    return parser


def main() -> int:
    """Punto de entrada del CLI."""
    parser = build_parser()
    args = parser.parse_args()

    commands = {
        "version": cmd_version,
        "status": cmd_status,
        "test-sensors": cmd_test_sensors,
        "run": cmd_run,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
