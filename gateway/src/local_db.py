import sqlite3
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LocalDB:
    """SQLite cache for sensor readings and alerts."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                quality TEXT DEFAULT 'good',
                synced INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT NOT NULL,
                sensor_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                current_value REAL NOT NULL,
                synced INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def store_reading(
        self,
        sensor_id: str,
        sensor_type: str,
        value: float,
        unit: str,
        timestamp: str,
        quality: str = "good",
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO readings (sensor_id, sensor_type, value, unit, timestamp, quality)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (sensor_id, sensor_type, value, unit, timestamp, quality),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_unsynced_readings(self, limit: int = 1000) -> List[dict]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM readings WHERE synced = 0 ORDER BY id LIMIT ?", (limit,)
        )
        return [dict(row) for row in cur.fetchall()]

    def mark_readings_synced(self, reading_ids: List[int]) -> int:
        if not reading_ids:
            return 0
        placeholders = ",".join("?" for _ in reading_ids)
        cur = self.conn.cursor()
        cur.execute(
            f"UPDATE readings SET synced = 1 WHERE id IN ({placeholders})",
            reading_ids,
        )
        self.conn.commit()
        return cur.rowcount

    def store_alert(
        self,
        rule_id: str,
        sensor_id: str,
        severity: str,
        message: str,
        current_value: float,
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO alert_history (rule_id, sensor_id, severity, message, current_value)
            VALUES (?, ?, ?, ?, ?)
            """,
            (rule_id, sensor_id, severity, message, current_value),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_unsynced_alerts(self, limit: int = 100) -> List[dict]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM alert_history WHERE synced = 0 ORDER BY id LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()]

    def mark_alerts_synced(self, alert_ids: List[int]) -> int:
        if not alert_ids:
            return 0
        placeholders = ",".join("?" for _ in alert_ids)
        cur = self.conn.cursor()
        cur.execute(
            f"UPDATE alert_history SET synced = 1 WHERE id IN ({placeholders})",
            alert_ids,
        )
        self.conn.commit()
        return cur.rowcount

    def get_readings_count(self) -> dict:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM readings")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM readings WHERE synced = 1")
        synced = cur.fetchone()[0]
        return {"total": total, "synced": synced, "pending": total - synced}

    def close(self):
        if self.conn:
            self.conn.close()
