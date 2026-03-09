from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cloud_backend_url: str = "http://backend:3000"
    gateway_id: str = "gateway-001"
    mqtt_broker_host: str = "mosquitto"
    mqtt_broker_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    ssdp_port: int = 1900
    ssdp_multicast_group: str = "239.255.255.250"
    sqlite_db_path: str = "/app/data/gateway.db"
    heartbeat_interval: int = 30
    heartbeat_max_missed: int = 3
    sync_interval: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
