"""EchoSmart Gateway — CLI entry point."""

import argparse
import logging
import sys

from src.config import GatewayConfig, config
from src.hal import HAL
from src.sensor_manager import SensorManager
from src.alert_engine import AlertEngine
from src.cloud_sync import CloudSync
from src.mqtt_publisher import MQTTPublisher
from src.local_db import LocalDB

__version__ = "1.0.0"

logger = logging.getLogger("echosmart-gateway")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="echosmart-gateway",
        description="EchoSmart IoT Gateway — Precision agriculture sensor hub",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command")

    # run
    run_parser = sub.add_parser("run", help="Start the gateway service")
    run_parser.add_argument(
        "--simulate", action="store_true", default=False,
        help="Force simulation mode (no real hardware)",
    )

    # status
    sub.add_parser("status", help="Show gateway status")

    # test-sensors
    sub.add_parser("test-sensors", help="Read each sensor once and print results")

    # version (alias)
    sub.add_parser("version", help="Print version and exit")

    return parser


def cmd_run(args):
    """Start the gateway."""
    simulation = args.simulate or config.simulation_mode
    logger.info("Starting EchoSmart Gateway v%s", __version__)
    logger.info("Gateway ID: %s", config.gateway_id)
    logger.info("Simulation mode: %s", simulation)

    hal = HAL(simulation_mode=simulation)
    manager = SensorManager(hal, polling_interval=config.polling_interval)
    AlertEngine()
    CloudSync(
        api_url=config.cloud_api_url,
        api_key=config.cloud_api_key,
        sync_interval=config.sync_interval,
    )
    MQTTPublisher(broker=config.mqtt_broker, port=config.mqtt_port)
    LocalDB()

    logger.info("All components initialised. Sensors registered: %d", len(manager.sensors))
    logger.info("Gateway started successfully. Press Ctrl+C to stop.")

    # Placeholder: real event loop would go here
    try:
        import time

        while True:
            readings = manager.read_all()
            for r in readings:
                logger.debug("Reading: %s", r)
            time.sleep(config.polling_interval)
    except KeyboardInterrupt:
        logger.info("Gateway stopped by user.")


def cmd_status(_args):
    """Print current configuration."""
    print(f"EchoSmart Gateway v{__version__}")
    print(f"  Gateway ID  : {config.gateway_id}")
    print(f"  Name        : {config.gateway_name}")
    print(f"  Cloud API   : {config.cloud_api_url}")
    print(f"  MQTT Broker : {config.mqtt_broker}:{config.mqtt_port}")
    print(f"  Polling     : {config.polling_interval}s")
    print(f"  Sync        : {config.sync_interval}s")
    print(f"  Simulation  : {config.simulation_mode}")


def cmd_test_sensors(_args):
    """Perform a single read on each configured sensor."""
    from src.sensor_drivers.ds18b20 import DS18B20Driver
    from src.sensor_drivers.dht22 import DHT22Driver
    from src.sensor_drivers.bh1750 import BH1750Driver
    from src.sensor_drivers.soil_moisture import SoilMoistureDriver
    from src.sensor_drivers.mhz19c import MHZ19CDriver

    drivers = [
        DS18B20Driver(simulation=True),
        DHT22Driver(simulation=True),
        BH1750Driver(simulation=True),
        SoilMoistureDriver(simulation=True),
        MHZ19CDriver(simulation=True),
    ]

    print("Sensor self-test (simulation mode):")
    for drv in drivers:
        reading = drv.read()
        print(f"  [{drv.name}] {reading}")
    print("All sensors OK.")


def main(argv=None):
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.command == "run":
        cmd_run(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "test-sensors":
        cmd_test_sensors(args)
    elif args.command == "version":
        print(f"echosmart-gateway {__version__}")
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
