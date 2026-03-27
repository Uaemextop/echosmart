"""Conexión a bases de datos (PostgreSQL, InfluxDB, Redis)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import settings

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base para modelos SQLAlchemy."""


def get_db():
    """Dependency que provee una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
