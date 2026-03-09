import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from cloud_sync import CloudSync
from config import settings
from heartbeat import HeartbeatMonitor
from models import Sensor, get_engine
from mqtt_handler import MQTTHandler
from ssdp_discovery import SSDPDiscovery

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

engine = get_engine()
mqtt_handler = MQTTHandler()
heartbeat_monitor = HeartbeatMonitor()
cloud_sync = CloudSync()
ssdp_discovery = SSDPDiscovery(mqtt_handler)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Gateway starting up (id=%s)", settings.gateway_id)
    try:
        mqtt_handler.connect()
    except Exception as exc:
        logger.warning("MQTT connect failed at startup: %s", exc)

    tasks = [
        asyncio.create_task(ssdp_discovery.run_continuous_discovery(), name="ssdp"),
        asyncio.create_task(heartbeat_monitor.start_monitoring(), name="heartbeat"),
        asyncio.create_task(cloud_sync.run_sync_loop(), name="cloud_sync"),
    ]
    yield
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    mqtt_handler.disconnect()
    logger.info("Gateway shut down")


app = FastAPI(title="EchoSmart Gateway", version="1.0.0", lifespan=lifespan)


class SensorDataPayload(BaseModel):
    data: Dict[str, Any]


class HeartbeatPayload(BaseModel):
    timestamp: Optional[str] = None


def _sensor_to_dict(sensor: Sensor) -> Dict[str, Any]:
    return {
        "id": sensor.id,
        "uuid": sensor.uuid,
        "sensor_type": sensor.sensor_type,
        "capabilities": sensor.capabilities,
        "status": sensor.status,
        "pending_cloud_sync": sensor.pending_cloud_sync,
        "last_seen": sensor.last_seen.isoformat() if sensor.last_seen else None,
        "tenant_id": sensor.tenant_id,
        "ip_address": sensor.ip_address,
        "port": sensor.port,
        "created_at": sensor.created_at.isoformat() if sensor.created_at else None,
        "updated_at": sensor.updated_at.isoformat() if sensor.updated_at else None,
    }


@app.get("/health")
async def health() -> Dict[str, Any]:
    with Session(engine) as session:
        count = session.query(Sensor).count()
    return {"status": "ok", "gateway_id": settings.gateway_id, "sensors_count": count}


@app.get("/sensors")
async def list_sensors() -> List[Dict[str, Any]]:
    with Session(engine) as session:
        sensors = session.query(Sensor).all()
        return [_sensor_to_dict(s) for s in sensors]


@app.get("/sensors/{uuid}")
async def get_sensor(uuid: str) -> Dict[str, Any]:
    with Session(engine) as session:
        sensor = session.query(Sensor).filter_by(uuid=uuid).first()
        if sensor is None:
            raise HTTPException(status_code=404, detail="Sensor not found")
        return _sensor_to_dict(sensor)


@app.post("/sensors/{uuid}/data")
async def receive_sensor_data(uuid: str, payload: SensorDataPayload) -> Dict[str, str]:
    with Session(engine) as session:
        sensor = session.query(Sensor).filter_by(uuid=uuid).first()
        if sensor is None:
            raise HTTPException(status_code=404, detail="Sensor not found")
        sensor.last_seen = datetime.now(timezone.utc)
        sensor.status = "online"
        session.commit()

    mqtt_handler.publish_sensor_data(uuid, payload.data)
    heartbeat_monitor.record_ping(uuid)
    return {"status": "published"}


@app.post("/heartbeat/{uuid}")
async def record_heartbeat(uuid: str, payload: Optional[HeartbeatPayload] = None) -> Dict[str, str]:
    heartbeat_monitor.record_ping(uuid)
    with Session(engine) as session:
        sensor = session.query(Sensor).filter_by(uuid=uuid).first()
        if sensor is not None:
            sensor.last_seen = datetime.now(timezone.utc)
            if sensor.status == "offline":
                sensor.status = "online"
            session.commit()
    return {"status": "ok", "uuid": uuid}
