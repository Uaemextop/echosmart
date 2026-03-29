"""EchoSmart Gateway — Main entry point.

Wires together all components following Clean Architecture:
  Config → Factory → Drivers → SensorManager → AlertEngine → Storage → Sync
"""

from __future__ import annotations

import logging
import signal
import sys
import time

from gateway.src.config import load_config
from gateway.src.application.sensor_manager import SensorManager
from gateway.src.application.alert_engine import (
    AlertEngine,
    RangeRule,
    ThresholdRule,
)
from gateway.src.application.cloud_sync_service import CloudSyncService
from gateway.src.domain.constants import GREENHOUSE_OPTIMAL
from gateway.src.domain.entities.alert import AlertSeverity
from gateway.src.infrastructure.driver_factory import SensorDriverFactory
from gateway.src.infrastructure.sqlite_storage import SqliteStorageRepository
from gateway.src.infrastructure.mqtt_publisher import MqttMessagePublisher
from gateway.src.infrastructure.http_sync_client import HttpSyncClient


def _build_default_rules() -> list:
    """Create alert rules from greenhouse optimal ranges."""
    rules = []
    for sensor_type, bounds in GREENHOUSE_OPTIMAL.items():
        rules.append(
            RangeRule(
                name=f"{sensor_type}_optimal_range",
                sensor_type=sensor_type,
                min_value=bounds["min"],
                max_value=bounds["max"],
                severity=AlertSeverity.WARNING,
            )
        )
    return rules


def main() -> None:
    """Initialise all components and run the polling loop."""
    cfg = load_config()

    logging.basicConfig(
        level=getattr(logging, cfg.log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger("echosmart-gateway")

    logger.info("Starting EchoSmart Gateway v1.0.0")
    logger.info("Gateway ID: %s", cfg.gateway_id)
    logger.info("Simulation mode: %s", cfg.simulation_mode)

    # --- Storage ---
    storage = SqliteStorageRepository()

    # --- Alert engine ---
    alert_engine = AlertEngine(storage=storage)
    for rule in _build_default_rules():
        alert_engine.add_rule(rule)

    # --- MQTT publisher ---
    mqtt = MqttMessagePublisher(
        broker=cfg.mqtt_broker,
        port=cfg.mqtt_port,
        gateway_id=cfg.gateway_id,
    )

    # --- Sensor manager ---
    def on_reading(reading):
        # Evaluate alerts
        alert_engine.evaluate(reading)
        # Publish via MQTT
        mqtt.publish(f"sensors/{reading.sensor_type}/reading", reading.to_dict())

    sensor_manager = SensorManager(
        storage=storage,
        polling_interval=cfg.polling_interval,
        on_reading=on_reading,
    )

    # --- Register sensors from config ---
    factory = SensorDriverFactory()
    for sc in cfg.sensors:
        params = dict(sc.params)
        params["sensor_id"] = sc.sensor_id
        params["simulation"] = cfg.simulation_mode
        try:
            driver = factory.create(sc.sensor_type, params)
            sensor_manager.register(driver)
        except (ValueError, TypeError) as exc:
            logger.error("Failed to create sensor '%s': %s", sc.name, exc)

    sensor_manager.initialize_all()

    # --- Cloud sync ---
    sync_client = HttpSyncClient(api_url=cfg.cloud_api_url, api_key=cfg.cloud_api_key)
    cloud_sync = CloudSyncService(storage=storage, sync_client=sync_client)

    # --- Graceful shutdown ---
    shutdown_requested = False

    def handle_signal(signum, frame):
        nonlocal shutdown_requested
        shutdown_requested = True
        logger.info("Shutdown signal received.")

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # --- Main loop ---
    logger.info("Gateway started — polling %d sensor(s) every %ds.",
                sensor_manager.sensor_count, cfg.polling_interval)

    last_sync = time.monotonic()

    try:
        while not shutdown_requested:
            readings = sensor_manager.read_all()
            logger.info("Cycle complete: %d reading(s).", len(readings))

            # Periodic cloud sync
            if (time.monotonic() - last_sync) >= cfg.sync_interval:
                result = cloud_sync.sync()
                logger.info("Cloud sync: %s", result)
                last_sync = time.monotonic()

            time.sleep(cfg.polling_interval)
    finally:
        sensor_manager.shutdown_all()
        mqtt.disconnect()
        storage.close()
        logger.info("Gateway stopped.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Gateway detenido por el usuario.")
        sys.exit(0)
