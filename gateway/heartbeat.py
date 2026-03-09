import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy.orm import Session

from config import settings
from models import Sensor, get_engine

logger = logging.getLogger(__name__)


class HeartbeatMonitor:
    def __init__(self) -> None:
        self._last_ping: Dict[str, datetime] = {}
        self._engine = get_engine()

    def record_ping(self, uuid: str) -> None:
        self._last_ping[uuid] = datetime.now(timezone.utc)
        logger.debug("Heartbeat recorded for sensor %s", uuid)

    async def check_heartbeats(self) -> None:
        now = datetime.now(timezone.utc)
        timeout_seconds = settings.heartbeat_interval * settings.heartbeat_max_missed

        with Session(self._engine) as session:
            sensors = session.query(Sensor).all()
            for sensor in sensors:
                last: Optional[datetime] = self._last_ping.get(sensor.uuid)
                if last is None:
                    if sensor.last_seen is not None:
                        last_seen = sensor.last_seen
                        if last_seen.tzinfo is None:
                            last_seen = last_seen.replace(tzinfo=timezone.utc)
                        elapsed = (now - last_seen).total_seconds()
                    else:
                        elapsed = timeout_seconds + 1
                else:
                    elapsed = (now - last).total_seconds()

                if elapsed > timeout_seconds and sensor.status == "online":
                    sensor.status = "offline"
                    logger.warning("Sensor %s marked offline (no heartbeat for %.0fs)", sensor.uuid, elapsed)

            session.commit()

    async def start_monitoring(self) -> None:
        while True:
            try:
                await self.check_heartbeats()
            except Exception as exc:
                logger.error("Heartbeat check error: %s", exc)
            await asyncio.sleep(settings.heartbeat_interval)

    def get_status(self) -> Dict[str, str]:
        now = datetime.now(timezone.utc)
        result: Dict[str, str] = {}
        with Session(self._engine) as session:
            sensors = session.query(Sensor).all()
            for sensor in sensors:
                result[sensor.uuid] = sensor.status
        return result
