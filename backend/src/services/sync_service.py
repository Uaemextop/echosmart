from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.models.gateway import Gateway


def sync_gateway(db: Session, gateway_id: str, tenant_id: str) -> Gateway | None:
    gateway = (
        db.query(Gateway)
        .filter(Gateway.id == gateway_id, Gateway.tenant_id == tenant_id)
        .first()
    )
    if gateway:
        gateway.last_sync_at = datetime.now(timezone.utc)
        gateway.status = "online"
        db.commit()
        db.refresh(gateway)
    return gateway
