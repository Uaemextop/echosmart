"""Caché local de lecturas en SQLite."""
import logging
import sqlite3

logger = logging.getLogger(__name__)

DB_PATH = "echosmart_local.db"


class LocalDB:
    """Almacenamiento local de lecturas para resiliencia offline."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Crear tablas si no existen."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp TEXT NOT NULL,
                synced INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
        logger.info(f"LocalDB inicializada en {self.db_path}")

    def store_reading(self, sensor_id: str, value: float, timestamp: str):
        """Almacenar una lectura."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO readings (sensor_id, value, timestamp) VALUES (?, ?, ?)",
            (sensor_id, value, timestamp),
        )
        conn.commit()
        conn.close()

    def get_unsynced(self, limit: int = 100) -> list:
        """Obtener lecturas no sincronizadas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT id, sensor_id, value, timestamp FROM readings WHERE synced = 0 LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "sensor_id": r[1], "value": r[2], "timestamp": r[3]} for r in rows]

    def mark_synced(self, ids: list):
        """Marcar lecturas como sincronizadas."""
        if not ids:
            return
        conn = sqlite3.connect(self.db_path)
        placeholders = ",".join(["?"] * len(ids))
        conn.execute(f"UPDATE readings SET synced = 1 WHERE id IN ({placeholders})", ids)
        conn.commit()
        conn.close()
