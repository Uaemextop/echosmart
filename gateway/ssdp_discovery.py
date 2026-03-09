import asyncio
import json
import logging
import socket
import struct
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from config import settings
from models import Sensor, get_engine
from mqtt_handler import MQTTHandler

logger = logging.getLogger(__name__)

SSDP_MULTICAST = "239.255.255.250"
SSDP_PORT = 1900

MSEARCH_MSG = (
    "M-SEARCH * HTTP/1.1\r\n"
    f"HOST: {SSDP_MULTICAST}:{SSDP_PORT}\r\n"
    "MAN: \"ssdp:discover\"\r\n"
    "MX: 3\r\n"
    "ST: urn:echosmart:device:sensor:1\r\n"
    "\r\n"
)


def _parse_ssdp_response(raw: str) -> dict:
    headers: dict = {}
    for line in raw.splitlines()[1:]:
        if ":" in line:
            key, _, value = line.partition(":")
            headers[key.strip().upper()] = value.strip()
    return headers


class SSDPDiscovery:
    def __init__(self, mqtt_handler: MQTTHandler) -> None:
        self._mqtt = mqtt_handler
        self._engine = get_engine()

    async def start_discovery(self) -> None:
        loop = asyncio.get_event_loop()
        # Collect raw responses in a thread (blocking I/O), then process them on the event loop
        responses = await loop.run_in_executor(None, self._run_ssdp_discovery)
        for response, addr in responses:
            try:
                self._handle_discovery_response(response, addr)
            except Exception as exc:
                logger.error("Error processing SSDP response from %s: %s", addr, exc)

    def _run_ssdp_discovery(self) -> list:
        """Blocking UDP socket operations — runs in a thread pool executor."""
        collected: list = []
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            try:
                # Binding to "" (all interfaces) is intentional for SSDP multicast reception
                sock.bind(("", SSDP_PORT))  # nosec B104 - required for multicast
            except OSError:
                sock.bind(("", 0))  # nosec B104 - fallback ephemeral port

            group = socket.inet_aton(SSDP_MULTICAST)
            mreq = struct.pack("4sL", group, socket.INADDR_ANY)
            try:
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            except OSError as exc:
                logger.debug("Multicast join skipped: %s", exc)

            sock.sendto(MSEARCH_MSG.encode(), (SSDP_MULTICAST, SSDP_PORT))
            logger.info("Sent M-SEARCH broadcast")

            sock.settimeout(3.0)
            while True:
                try:
                    data, addr = sock.recvfrom(4096)
                    response = data.decode("utf-8", errors="replace")
                    collected.append((response, addr))
                except socket.timeout:
                    break
        except Exception as exc:
            logger.error("SSDP discovery error: %s", exc)
        finally:
            sock.close()
        return collected

    def _handle_discovery_response(self, response: str, addr: tuple) -> None:
        headers = _parse_ssdp_response(response)
        uuid: Optional[str] = headers.get("USN") or headers.get("UUID")
        sensor_type: Optional[str] = headers.get("SENSOR-TYPE")
        capabilities_raw: str = headers.get("CAPABILITIES", "[]")
        ip_str, port_str = addr[0], headers.get("PORT", "8080")

        if not uuid or not sensor_type:
            logger.debug("Ignored SSDP response missing UUID/SENSOR-TYPE from %s", addr)
            return

        try:
            capabilities = json.loads(capabilities_raw)
        except json.JSONDecodeError:
            capabilities = []

        try:
            port = int(port_str)
        except (ValueError, TypeError):
            port = 8080

        with Session(self._engine) as session:
            existing: Optional[Sensor] = session.query(Sensor).filter_by(uuid=uuid).first()
            if existing is None:
                sensor = Sensor(
                    uuid=uuid,
                    sensor_type=sensor_type,
                    capabilities=capabilities,
                    status="online",
                    pending_cloud_sync=True,
                    last_seen=datetime.now(timezone.utc),
                    ip_address=ip_str,
                    port=port,
                )
                session.add(sensor)
                logger.info("Discovered new sensor %s (%s)", uuid, sensor_type)
            else:
                existing.sensor_type = sensor_type
                existing.capabilities = capabilities
                existing.ip_address = ip_str
                existing.port = port
                existing.status = "online"
                existing.last_seen = datetime.now(timezone.utc)
                # preserve pending flag; only clear after confirmed cloud sync
                logger.info("Updated existing sensor %s", uuid)
            session.commit()

        self._mqtt.create_topics(uuid)
        self._mqtt.subscribe_to_sensor(uuid)

    async def run_continuous_discovery(self) -> None:
        while True:
            try:
                await self.start_discovery()
            except Exception as exc:
                logger.error("Continuous SSDP error: %s", exc)
            await asyncio.sleep(60)
