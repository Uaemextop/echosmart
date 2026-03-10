import logging

from src.config import Config
from src.sensor_manager import SensorManager
from src.alert_engine import AlertEngine
from src.cloud_sync import CloudSyncManager
from src.mqtt_publisher import MQTTPublisher
from src.local_db import LocalDB
from src.discovery import SensorDiscovery


def main():
    config = Config()
    logging.basicConfig(level=getattr(logging, config.log_level))
    logger = logging.getLogger("echosmart-gateway")

    local_db = LocalDB(config.sqlite_path)
    sensor_manager = SensorManager(config)
    alert_engine = AlertEngine()
    mqtt_publisher = MQTTPublisher(
        config.mqtt_broker, config.mqtt_port, config.gateway_id
    )
    cloud_sync = CloudSyncManager(config, local_db)
    discovery = SensorDiscovery()

    discovered = discovery.discover_all()
    for sensor in discovered:
        sensor_manager.register_sensor(sensor["device_id"], sensor["type"])

    logger.info(
        "Gateway %s started with %d sensors",
        config.gateway_id,
        len(sensor_manager.sensors),
    )

    readings = sensor_manager.read_all_sensors()
    for reading in readings:
        local_db.store_reading(
            sensor_id=reading["sensor_id"],
            sensor_type=reading["sensor_type"],
            value=reading["value"],
            unit=reading["unit"],
            timestamp=reading["timestamp"],
            quality=reading["quality"],
        )
        mqtt_publisher.publish_reading(reading["sensor_id"], reading)
        alerts = alert_engine.evaluate(reading["sensor_id"], reading["value"])
        for alert in alerts:
            local_db.store_alert(
                rule_id=alert["rule_id"],
                sensor_id=alert["sensor_id"],
                severity=alert["severity"],
                message=alert["message"],
                current_value=alert["current_value"],
            )
            mqtt_publisher.publish_alert(alert)

    logger.info("Read %d sensor values", len(readings))
    local_db.close()


if __name__ == "__main__":
    main()
