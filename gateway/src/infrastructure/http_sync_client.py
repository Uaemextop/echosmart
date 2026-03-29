"""HTTP sync client — Concrete implementation of ISyncClient.

Sends batched readings and alerts to the cloud backend with retry logic.
"""

from __future__ import annotations

import logging
import time

import requests

from gateway.src.domain.interfaces.sync_client import ISyncClient

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_BACKOFF_BASE_S = 2


class HttpSyncClient(ISyncClient):
    """HTTP client for synchronizing data with the EchoSmart cloud backend.

    Args:
        api_url: Base URL of the backend API.
        api_key: Bearer token for authentication.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_key: str = "",
        timeout: int = 30,
    ) -> None:
        self._api_url = api_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._session = requests.Session()
        if api_key:
            self._session.headers["Authorization"] = f"Bearer {api_key}"
        self._session.headers["Content-Type"] = "application/json"

    def sync_readings(self, readings: list[dict]) -> list[int]:
        url = f"{self._api_url}/api/v1/readings/batch"
        response = self._post_with_retry(url, {"readings": readings})
        if response and response.ok:
            synced_ids = response.json().get("synced_ids", [])
            logger.info("Synced %d/%d readings.", len(synced_ids), len(readings))
            return synced_ids
        return []

    def sync_alerts(self, alerts: list[dict]) -> list[str]:
        url = f"{self._api_url}/api/v1/alerts/batch"
        response = self._post_with_retry(url, {"alerts": alerts})
        if response and response.ok:
            synced_ids = response.json().get("synced_ids", [])
            logger.info("Synced %d/%d alerts.", len(synced_ids), len(alerts))
            return synced_ids
        return []

    def register_gateway(self, info: dict) -> bool:
        url = f"{self._api_url}/api/v1/gateways/register"
        response = self._post_with_retry(url, info)
        if response and response.ok:
            logger.info("Gateway registered successfully.")
            return True
        return False

    def health_check(self) -> bool:
        try:
            resp = self._session.get(
                f"{self._api_url}/api/v1/health",
                timeout=self._timeout,
            )
            return resp.ok
        except requests.RequestException:
            return False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _post_with_retry(
        self,
        url: str,
        payload: dict,
    ) -> requests.Response | None:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = self._session.post(url, json=payload, timeout=self._timeout)
                if resp.ok:
                    return resp
                logger.warning(
                    "Sync attempt %d/%d to %s returned %d.",
                    attempt,
                    _MAX_RETRIES,
                    url,
                    resp.status_code,
                )
            except requests.RequestException as exc:
                logger.warning(
                    "Sync attempt %d/%d to %s failed: %s",
                    attempt,
                    _MAX_RETRIES,
                    url,
                    exc,
                )
            if attempt < _MAX_RETRIES:
                delay = _BACKOFF_BASE_S ** attempt
                time.sleep(delay)
        return None
