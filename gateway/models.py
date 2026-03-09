import os
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base

from config import settings

Base = declarative_base()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, unique=True, nullable=False)
    sensor_type = Column(String, nullable=False)
    capabilities = Column(JSON, default=list)
    status = Column(String, default="offline")
    pending_cloud_sync = Column(Boolean, default=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


def get_engine():
    db_path = settings.sqlite_db_path
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return engine
