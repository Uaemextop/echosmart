from sqlalchemy.orm import Session

from src.models.alert import Alert, AlertRule


def get_alerts_for_tenant(
    db: Session,
    tenant_id: str,
    severity: str | None = None,
    acknowledged: bool | None = None,
    limit: int = 100,
) -> list[Alert]:
    query = db.query(Alert).filter(Alert.tenant_id == tenant_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    if acknowledged is not None:
        query = query.filter(Alert.is_acknowledged == acknowledged)
    return query.order_by(Alert.created_at.desc()).limit(limit).all()


def get_alert_rules_for_tenant(db: Session, tenant_id: str) -> list[AlertRule]:
    return db.query(AlertRule).filter(AlertRule.tenant_id == tenant_id).all()
