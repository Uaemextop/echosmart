import asyncio
import logging
from typing import Any, Dict, Optional

import httpx
from sqlalchemy.orm import Session

from config import settings
from models import Sensor, get_engine

logger = logging.getLogger(__name__)


class CloudSync:
    def __init__(self) -> None:
        self._engine = get_engine()

    async def sync_pending_sensors(self) -> None:
        with Session(self._engine) as session:
            pending = session.query(Sensor).filter_by(pending_cloud_sync=True).all()
            if not pending:
                return
            logger.info("Syncing %d pending sensor(s) to cloud", len(pending))
            async with httpx.AsyncClient(timeout=10.0) as client:
                for sensor in pending:
                    payload: Dict[str, Any] = {
                        "uuid": sensor.uuid,
                        "sensor_type": sensor.sensor_type,
                        "capabilities": sensor.capabilities or [],
                        "gateway_id": settings.gateway_id,
                        "ip_address": sensor.ip_address,
                        "port": sensor.port,
                    }
                    try:
                        resp = await client.post(
                            f"{settings.cloud_backend_url}/api/sensors/register",
                            json=payload,
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        sensor.pending_cloud_sync = False
                        if data.get("tenant_id"):
                            sensor.tenant_id = data["tenant_id"]
                        logger.info("Synced sensor %s to cloud (tenant=%s)", sensor.uuid, sensor.tenant_id)
                    except httpx.HTTPStatusError as exc:
                        logger.error(
                            "HTTP error syncing sensor %s: %s %s",
                            sensor.uuid,
                            exc.response.status_code,
                            exc.response.text,
                        )
                    except httpx.RequestError as exc:
                        logger.error("Request error syncing sensor %s: %s", sensor.uuid, exc)
            session.commit()

    async def run_sync_loop(self) -> None:
        while True:
            try:
                await self.sync_pending_sensors()
            except Exception as exc:
                logger.error("Cloud sync loop error: %s", exc)
            await asyncio.sleep(settings.sync_interval)
