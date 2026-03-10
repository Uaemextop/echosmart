from sqlalchemy.orm import Session

from src.models.sensor import Sensor


def get_sensors_for_tenant(
    db: Session,
    tenant_id: str,
    gateway_id: str | None = None,
    sensor_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Sensor]:
    query = db.query(Sensor).filter(Sensor.tenant_id == tenant_id)
    if gateway_id:
        query = query.filter(Sensor.gateway_id == gateway_id)
    if sensor_type:
        query = query.filter(Sensor.type == sensor_type)
    return query.offset(offset).limit(limit).all()
