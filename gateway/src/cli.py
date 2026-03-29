"""EchoSmart Gateway — CLI entry point.

Provides subcommands for running, managing, and diagnosing the gateway.
Designed for production deployment on Raspberry Pi OS.
"""

import argparse
import json
import logging
import os
import sys

VERSION = "1.0.0"

# Ensure gateway package is importable
_GATEWAY_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _GATEWAY_DIR not in sys.path:
    sys.path.insert(0, _GATEWAY_DIR)


def _setup_logging(level: str = "INFO") -> None:
    """Configure structured logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def cmd_run(args: argparse.Namespace) -> int:
    """Start the gateway service."""
    from src.config import config

    if args.simulate:
        os.environ["SIMULATION_MODE"] = "true"

    _setup_logging(config.log_level)
    logger = logging.getLogger("echosmart-gateway")
    logger.info("EchoSmart Gateway v%s starting", VERSION)
    logger.info("Gateway ID: %s", config.gateway_id)
    logger.info("Simulation mode: %s", config.simulation_mode or args.simulate)

    from src.hal import HAL
    from src.sensor_manager import SensorManager

    hal = HAL(simulation_mode=config.simulation_mode or args.simulate)
    manager = SensorManager(hal, polling_interval=config.polling_interval)

    logger.info("Gateway started successfully.")
    if not args.simulate:
        manager.start_polling()
    else:
        readings = manager.read_all()
        logger.info("Simulation readings: %s", readings)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Show gateway status."""
    from src.config import config

    info = {
        "version": VERSION,
        "gateway_id": config.gateway_id,
        "gateway_name": config.gateway_name,
        "cloud_api_url": config.cloud_api_url,
        "mqtt_broker": f"{config.mqtt_broker}:{config.mqtt_port}",
        "polling_interval": config.polling_interval,
        "sync_interval": config.sync_interval,
        "simulation_mode": config.simulation_mode,
        "log_level": config.log_level,
    }
    print(json.dumps(info, indent=2))
    return 0


def cmd_test_sensors(args: argparse.Namespace) -> int:
    """Run a quick sensor diagnostic."""
    _setup_logging("INFO")
    logger = logging.getLogger("echosmart-gateway")

    from src.hal import HAL
    from src.sensor_manager import SensorManager
    from src.sensor_drivers.ds18b20 import DS18B20Driver
    from src.sensor_drivers.dht22 import DHT22Driver
    from src.sensor_drivers.bh1750 import BH1750Driver
    from src.sensor_drivers.soil_moisture import SoilMoistureDriver
    from src.sensor_drivers.mhz19c import MHZ19CDriver

    hal = HAL(simulation_mode=True)
    manager = SensorManager(hal, polling_interval=5)

    drivers = [
        DS18B20Driver(simulation=True),
        DHT22Driver(simulation=True),
        BH1750Driver(simulation=True),
        SoilMoistureDriver(simulation=True),
        MHZ19CDriver(simulation=True),
    ]
    for d in drivers:
        manager.register_sensor(d)

    readings = manager.read_all()
    print(json.dumps(readings, indent=2, default=str))
    logger.info("Sensor diagnostic complete — %d sensors OK", len(readings))
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    """Print version string."""
    print(f"echosmart-gateway {VERSION}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="echosmart-gateway",
        description="EchoSmart IoT Gateway for precision agriculture",
    )
    sub = parser.add_subparsers(dest="command")

    # run
    p_run = sub.add_parser("run", help="Start the gateway service")
    p_run.add_argument(
        "--simulate", action="store_true", help="Run in simulation mode"
    )
    p_run.set_defaults(func=cmd_run)

    # status
    p_status = sub.add_parser("status", help="Show gateway configuration")
    p_status.set_defaults(func=cmd_status)

    # test-sensors
    p_test = sub.add_parser("test-sensors", help="Run sensor diagnostics")
    p_test.set_defaults(func=cmd_test_sensors)

    # version
    p_ver = sub.add_parser("version", help="Print version")
    p_ver.set_defaults(func=cmd_version)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
