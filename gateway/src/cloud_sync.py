import json
import logging
import time
from typing import Optional, List

import requests

logger = logging.getLogger(__name__)


class CloudSyncManager:
    """Synchronises local sensor data and alerts with the cloud API."""

    def __init__(self, config, local_db):
        self.api_url = config.cloud_api_url
        self.api_key = config.cloud_api_key
        self.gateway_id = config.gateway_id
        self.local_db = local_db
        self.max_retries = 5
        self.retry_delays = [5, 15, 45, 120, 120]

    def sync_readings(self) -> dict:
        unsynced = self.local_db.get_unsynced_readings(limit=1000)
        if not unsynced:
            return {"synced_count": 0, "failed_count": 0, "next_sync_interval": 300}

        payload = {
            "gateway_id": self.gateway_id,
            "readings": unsynced,
        }

        success = self._post_with_retry(f"{self.api_url}/api/v1/readings/batch", payload)

        if success:
            ids = [r["id"] for r in unsynced]
            self.local_db.mark_readings_synced(ids)
            return {
                "synced_count": len(unsynced),
                "failed_count": 0,
                "next_sync_interval": 300,
            }

        return {
            "synced_count": 0,
            "failed_count": len(unsynced),
            "next_sync_interval": 60,
        }

    def sync_alerts(self) -> dict:
        unsynced = self.local_db.get_unsynced_alerts(limit=100)
        if not unsynced:
            return {"synced_count": 0, "failed_count": 0}

        payload = {
            "gateway_id": self.gateway_id,
            "alerts": unsynced,
        }

        success = self._post_with_retry(f"{self.api_url}/api/v1/alerts/batch", payload)

        if success:
            ids = [a["id"] for a in unsynced]
            self.local_db.mark_alerts_synced(ids)
            return {"synced_count": len(unsynced), "failed_count": 0}

        return {"synced_count": 0, "failed_count": len(unsynced)}

    def fetch_config(self) -> Optional[dict]:
        url = f"{self.api_url}/api/v1/gateways/{self.gateway_id}/config"
        headers = self._auth_headers()
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error("Failed to fetch gateway config: %s", e)
            return None

    def _post_with_retry(self, url: str, payload: dict) -> bool:
        headers = self._auth_headers()
        headers["Content-Type"] = "application/json"

        for attempt in range(self.max_retries):
            try:
                resp = requests.post(
                    url, json=payload, headers=headers, timeout=30
                )
                resp.raise_for_status()
                return True
            except requests.RequestException as e:
                delay = self.retry_delays[attempt] if attempt < len(self.retry_delays) else 120
                logger.warning(
                    "Cloud sync attempt %d/%d failed: %s — retrying in %ds",
                    attempt + 1, self.max_retries, e, delay,
                )
                time.sleep(delay)

        logger.error("Cloud sync failed after %d retries", self.max_retries)
        return False

    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}
