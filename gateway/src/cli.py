"""CLI del EchoSmart Gateway."""

import argparse
import json
import logging
import os
import sys

VERSION = "1.0.0"

logger = logging.getLogger("echosmart-gateway")


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------


def cmd_run(args: argparse.Namespace) -> int:
    """Iniciar el gateway (modo normal o simulación)."""
    _setup_logging(args.log_level)

    if args.simulate:
        os.environ["SIMULATION_MODE"] = "true"
        logger.info("Modo simulación activado.")

    from gateway.src.config import config  # noqa: PLC0415
    from gateway.src.hal import HAL  # noqa: PLC0415
    from gateway.src.sensor_manager import SensorManager  # noqa: PLC0415
    from gateway.src.alert_engine import AlertEngine  # noqa: PLC0415
    from gateway.src.cloud_sync import CloudSync  # noqa: PLC0415

    logger.info(f"Iniciando EchoSmart Gateway v{VERSION}")
    logger.info(f"Gateway ID : {config.gateway_id}")
    logger.info(f"Cloud URL  : {config.cloud_api_url}")
    logger.info(f"Simulación : {config.simulation_mode}")

    hal = HAL(simulation_mode=config.simulation_mode)
    manager = SensorManager(hal, polling_interval=config.polling_interval)
    engine = AlertEngine()
    sync = CloudSync(
        api_url=config.cloud_api_url,
        api_key=config.cloud_api_key,
        sync_interval=config.sync_interval,
    )

    logger.info(
        f"Gateway iniciado — SensorManager, AlertEngine y CloudSync listos."
    )
    logger.info("Presiona Ctrl+C para detener.")

    try:
        import time  # noqa: PLC0415

        while True:
            readings = manager.read_all()
            for reading in readings:
                alerts = engine.evaluate(reading)
                if alerts:
                    logger.warning(f"Alertas generadas: {alerts}")
                sync.queue_reading(reading)
            sync.sync()
            time.sleep(config.polling_interval)
    except KeyboardInterrupt:
        logger.info("Gateway detenido por el usuario.")

    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Mostrar estado del gateway."""
    _setup_logging(args.log_level)

    from gateway.src.config import config  # noqa: PLC0415

    status = {
        "version": VERSION,
        "gateway_id": config.gateway_id,
        "gateway_name": config.gateway_name,
        "cloud_api_url": config.cloud_api_url,
        "mqtt_broker": config.mqtt_broker,
        "simulation_mode": config.simulation_mode,
        "polling_interval_s": config.polling_interval,
    }
    print(json.dumps(status, indent=2))
    return 0


def cmd_test_sensors(args: argparse.Namespace) -> int:
    """Probar conectividad de todos los sensores configurados."""
    _setup_logging(args.log_level)

    from gateway.src.hal import HAL  # noqa: PLC0415
    from gateway.src.sensor_manager import SensorManager  # noqa: PLC0415

    simulation = args.simulate or os.environ.get("SIMULATION_MODE", "false").lower() == "true"
    hal = HAL(simulation_mode=simulation)
    manager = SensorManager(hal, polling_interval=1)

    print(f"Probando {len(manager.sensors)} sensores registrados...")

    if not manager.sensors:
        print("No hay sensores registrados. Use sensors.json para configurarlos.")
        return 0

    readings = manager.read_all()
    ok = True
    for r in readings:
        status = "✓" if r else "✗"
        print(f"  {status} {r}")
        if not r:
            ok = False

    return 0 if ok else 1


def cmd_version(_args: argparse.Namespace) -> int:
    """Mostrar la versión del gateway."""
    print(f"echosmart-gateway {VERSION}")
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="echosmart-gateway",
        description="EchoSmart Gateway — Software de edge computing para Raspberry Pi",
    )
    parser.add_argument(
        "--log-level",
        default=os.environ.get("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nivel de logging (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # run
    run_parser = subparsers.add_parser("run", help="Iniciar el gateway")
    run_parser.add_argument(
        "--simulate",
        action="store_true",
        default=False,
        help="Ejecutar en modo simulación (sin hardware real)",
    )
    run_parser.set_defaults(func=cmd_run)

    # status
    status_parser = subparsers.add_parser("status", help="Mostrar estado del gateway")
    status_parser.set_defaults(func=cmd_status)

    # test-sensors
    test_parser = subparsers.add_parser(
        "test-sensors", help="Probar conectividad de sensores"
    )
    test_parser.add_argument(
        "--simulate",
        action="store_true",
        default=False,
        help="Usar modo simulación para el test",
    )
    test_parser.set_defaults(func=cmd_test_sensors)

    # version
    version_parser = subparsers.add_parser("version", help="Mostrar versión")
    version_parser.set_defaults(func=cmd_version)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada principal de la CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
