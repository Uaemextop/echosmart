"""EchoSmart Gateway — Command-Line Interface.

Provides sub-commands for running, diagnosing and managing the gateway
on a Raspberry Pi (or any Linux host).

Usage:
    echosmart-gateway run [--simulate]
    echosmart-gateway status
    echosmart-gateway test-sensors
    echosmart-gateway version
"""

import argparse
import json
import logging
import sys

from gateway.src.config import GatewayConfig

__version__ = "1.0.0"

logger = logging.getLogger("echosmart-gateway")


# ── helpers ──────────────────────────────────────────────────────────────

def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _load_config(args: argparse.Namespace) -> GatewayConfig:
    cfg = GatewayConfig()
    if getattr(args, "simulate", False):
        cfg.simulation_mode = True
    return cfg


# ── sub-commands ─────────────────────────────────────────────────────────

def cmd_run(args: argparse.Namespace) -> int:
    """Start the gateway main loop."""
    cfg = _load_config(args)
    _setup_logging(cfg.log_level)

    logger.info("EchoSmart Gateway v%s", __version__)
    logger.info("Gateway ID  : %s", cfg.gateway_id)
    logger.info("Simulation  : %s", cfg.simulation_mode)

    from gateway.src.hal import HAL
    from gateway.src.sensor_manager import SensorManager

    hal = HAL(simulation_mode=cfg.simulation_mode)
    manager = SensorManager(hal, polling_interval=cfg.polling_interval)

    if cfg.simulation_mode:
        from gateway.src.sensor_drivers.ds18b20 import DS18B20Driver
        from gateway.src.sensor_drivers.dht22 import DHT22Driver
        from gateway.src.sensor_drivers.mhz19c import MHZ19CDriver
        from gateway.src.sensor_drivers.bh1750 import BH1750Driver
        from gateway.src.sensor_drivers.soil_moisture import SoilMoistureDriver

        manager.register_sensor(DS18B20Driver(simulation=True))
        manager.register_sensor(DHT22Driver(simulation=True))
        manager.register_sensor(MHZ19CDriver(simulation=True))
        manager.register_sensor(BH1750Driver(simulation=True))
        manager.register_sensor(SoilMoistureDriver(simulation=True))

    readings = manager.read_all()
    for r in readings:
        logger.info("Reading: %s", r)

    logger.info("Gateway started successfully.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Print gateway runtime status."""
    cfg = _load_config(args)
    _setup_logging(cfg.log_level)

    info = {
        "version": __version__,
        "gateway_id": cfg.gateway_id,
        "gateway_name": cfg.gateway_name,
        "simulation_mode": cfg.simulation_mode,
        "cloud_api_url": cfg.cloud_api_url,
        "mqtt_broker": cfg.mqtt_broker,
        "polling_interval": cfg.polling_interval,
    }
    print(json.dumps(info, indent=2))
    return 0


def cmd_test_sensors(args: argparse.Namespace) -> int:
    """Run a quick self-test on every sensor driver (simulation mode)."""
    _setup_logging("INFO")

    from gateway.src.sensor_drivers.ds18b20 import DS18B20Driver
    from gateway.src.sensor_drivers.dht22 import DHT22Driver
    from gateway.src.sensor_drivers.mhz19c import MHZ19CDriver
    from gateway.src.sensor_drivers.bh1750 import BH1750Driver
    from gateway.src.sensor_drivers.soil_moisture import SoilMoistureDriver

    drivers = [
        DS18B20Driver(simulation=True),
        DHT22Driver(simulation=True),
        MHZ19CDriver(simulation=True),
        BH1750Driver(simulation=True),
        SoilMoistureDriver(simulation=True),
    ]

    ok = 0
    fail = 0
    for drv in drivers:
        try:
            reading = drv.read()
            print(f"  ✓ {drv.name:20s}  →  {reading}")
            ok += 1
        except Exception as exc:
            print(f"  ✗ {drv.name:20s}  →  ERROR: {exc}")
            fail += 1

    print(f"\nResults: {ok} passed, {fail} failed")
    return 1 if fail else 0


def cmd_version(args: argparse.Namespace) -> int:
    """Print version string."""
    print(f"echosmart-gateway {__version__}")
    return 0


# ── argument parser ─────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="echosmart-gateway",
        description="EchoSmart IoT Gateway for greenhouse monitoring",
    )
    sub = parser.add_subparsers(dest="command")

    # run
    p_run = sub.add_parser("run", help="Start the gateway")
    p_run.add_argument(
        "--simulate", action="store_true",
        help="Run with simulated sensor data",
    )
    p_run.set_defaults(func=cmd_run)

    # status
    p_status = sub.add_parser("status", help="Show gateway status")
    p_status.set_defaults(func=cmd_status)

    # test-sensors
    p_test = sub.add_parser("test-sensors", help="Self-test all sensor drivers")
    p_test.set_defaults(func=cmd_test_sensors)

    # version
    p_ver = sub.add_parser("version", help="Print version")
    p_ver.set_defaults(func=cmd_version)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
