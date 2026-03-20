"""Configuración centralizada del backend EchoSmart."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración del backend cargada desde variables de entorno."""

    # Base de datos
    database_url: str = "postgresql://echosmart:echosmart@localhost:5432/echosmart"

    # InfluxDB
    influxdb_url: str = "http://localhost:8086"
    influxdb_token: str = "my-token"
    influxdb_org: str = "echosmart"
    influxdb_bucket: str = "sensor_readings"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT
    jwt_secret_key: str = "cambiar-en-produccion"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440
    jwt_refresh_token_expire_days: int = 30

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
