"""SQLite storage repository — Concrete implementation of IStorageRepository.

Provides local persistence for sensor readings and alerts with sync tracking.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timezone

from gateway.src.domain.constants import DEFAULT_RETENTION_DAYS
from gateway.src.domain.entities.alert import Alert, AlertSeverity
from gateway.src.domain.entities.sensor_reading import SensorReading
from gateway.src.domain.interfaces.storage import IStorageRepository

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = "echosmart_local.db"


class SqliteStorageRepository(IStorageRepository):
    """SQLite-backed storage with WAL mode for concurrent read/write.

    Args:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: str = _DEFAULT_DB_PATH) -> None:
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    # ------------------------------------------------------------------
    # IStorageRepository implementation
    # ------------------------------------------------------------------

    def save_reading(self, reading: SensorReading) -> None:
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO readings
               (sensor_id, sensor_type, value, unit, timestamp, is_valid, synced)
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (
                reading.sensor_id,
                reading.sensor_type,
                reading.value,
                reading.unit,
                reading.timestamp.isoformat(),
                int(reading.is_valid),
            ),
        )
        conn.commit()

    def save_alert(self, alert: Alert) -> None:
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO alerts
               (id, sensor_id, sensor_type, rule_name, severity, message,
                threshold, actual_value, created_at, acknowledged, synced)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                alert.id,
                alert.sensor_id,
                alert.sensor_type,
                alert.rule_name,
                alert.severity.value,
                alert.message,
                alert.threshold,
                alert.actual_value,
                alert.created_at.isoformat(),
                int(alert.acknowledged),
                int(alert.synced),
            ),
        )
        conn.commit()

    def get_readings(
        self,
        sensor_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[SensorReading]:
        conn = self._get_conn()
        query = "SELECT sensor_id, sensor_type, value, unit, timestamp, is_valid FROM readings"
        conditions: list[str] = []
        params: list = []

        if sensor_id is not None:
            conditions.append("sensor_id = ?")
            params.append(sensor_id)
        if since is not None:
            conditions.append("timestamp >= ?")
            params.append(since.isoformat())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        return [
            SensorReading(
                sensor_id=r[0],
                sensor_type=r[1],
                value=r[2],
                unit=r[3],
                timestamp=datetime.fromisoformat(r[4]),
                is_valid=bool(r[5]),
            )
            for r in rows
        ]

    def get_unsynced_readings(self, limit: int = 100) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT id, sensor_id, sensor_type, value, unit, timestamp
               FROM readings WHERE synced = 0
               ORDER BY timestamp ASC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [
            {
                "id": r[0],
                "sensor_id": r[1],
                "sensor_type": r[2],
                "value": r[3],
                "unit": r[4],
                "timestamp": r[5],
            }
            for r in rows
        ]

    def mark_readings_synced(self, reading_ids: list[int]) -> None:
        if not reading_ids:
            return
        conn = self._get_conn()
        placeholders = ",".join("?" * len(reading_ids))
        conn.execute(
            f"UPDATE readings SET synced = 1 WHERE id IN ({placeholders})",
            reading_ids,
        )
        conn.commit()

    def get_unsynced_alerts(self, limit: int = 50) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT id, sensor_id, sensor_type, rule_name, severity, message,
                      threshold, actual_value, created_at
               FROM alerts WHERE synced = 0
               ORDER BY created_at ASC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [
            {
                "id": r[0],
                "sensor_id": r[1],
                "sensor_type": r[2],
                "rule_name": r[3],
                "severity": r[4],
                "message": r[5],
                "threshold": r[6],
                "actual_value": r[7],
                "created_at": r[8],
            }
            for r in rows
        ]

    def mark_alerts_synced(self, alert_ids: list[str]) -> None:
        if not alert_ids:
            return
        conn = self._get_conn()
        placeholders = ",".join("?" * len(alert_ids))
        conn.execute(
            f"UPDATE alerts SET synced = 1 WHERE id IN ({placeholders})",
            alert_ids,
        )
        conn.commit()

    def get_stats(self) -> dict:
        conn = self._get_conn()
        total = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
        unsynced = conn.execute(
            "SELECT COUNT(*) FROM readings WHERE synced = 0"
        ).fetchone()[0]
        alerts_total = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        db_size = os.path.getsize(self._db_path) if os.path.exists(self._db_path) else 0
        return {
            "total_readings": total,
            "unsynced_readings": unsynced,
            "total_alerts": alerts_total,
            "db_size_bytes": db_size,
        }

    def apply_retention(self, max_age_days: int = DEFAULT_RETENTION_DAYS) -> int:
        conn = self._get_conn()
        cutoff = datetime.now(timezone.utc).isoformat()
        # SQLite date math: compare ISO strings
        cursor = conn.execute(
            """DELETE FROM readings
               WHERE timestamp < datetime('now', ?)""",
            (f"-{max_age_days} days",),
        )
        deleted = cursor.rowcount
        conn.commit()
        if deleted > 0:
            conn.execute("PRAGMA incremental_vacuum")
            logger.info("Retention: deleted %d readings older than %d days.", deleted, max_age_days)
        return deleted

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("SQLite connection closed.")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path)
        return self._conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id  TEXT    NOT NULL,
                sensor_type TEXT   NOT NULL,
                value      REAL   NOT NULL,
                unit       TEXT   NOT NULL,
                timestamp  TEXT   NOT NULL,
                is_valid   INTEGER DEFAULT 1,
                synced     INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_readings_sensor
                ON readings(sensor_id);
            CREATE INDEX IF NOT EXISTS idx_readings_timestamp
                ON readings(timestamp);
            CREATE INDEX IF NOT EXISTS idx_readings_synced
                ON readings(synced) WHERE synced = 0;

            CREATE TABLE IF NOT EXISTS alerts (
                id           TEXT    PRIMARY KEY,
                sensor_id    TEXT    NOT NULL,
                sensor_type  TEXT    NOT NULL,
                rule_name    TEXT    NOT NULL,
                severity     TEXT    NOT NULL,
                message      TEXT    NOT NULL,
                threshold    REAL    NOT NULL,
                actual_value REAL    NOT NULL,
                created_at   TEXT    NOT NULL,
                acknowledged INTEGER DEFAULT 0,
                synced       INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_alerts_synced
                ON alerts(synced) WHERE synced = 0;

            CREATE TABLE IF NOT EXISTS sync_log (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id       TEXT    NOT NULL,
                records_sent   INTEGER NOT NULL,
                records_failed INTEGER NOT NULL DEFAULT 0,
                timestamp      TEXT    NOT NULL
            );
            """
        )
        conn.commit()
        logger.info("SQLite storage initialized at %s (WAL mode).", self._db_path)
