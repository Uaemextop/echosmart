from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.middleware.auth import get_current_user
from src.models.alert import Alert, AlertRule
from src.models.sensor import Sensor
from src.models.user import User
from src.schemas.alert import (
    AlertRuleCreate,
    AlertRuleResponse,
    AlertResponse,
    AcknowledgeRequest,
)
from src.services.alert_service import get_alerts_for_tenant, get_alert_rules_for_tenant

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertResponse])
def list_alerts(
    severity: str | None = None,
    acknowledged: bool | None = None,
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_alerts_for_tenant(
        db,
        tenant_id=current_user.tenant_id,
        severity=severity,
        acknowledged=acknowledged,
        limit=limit,
    )


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: str,
    body: AcknowledgeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.tenant_id == current_user.tenant_id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_acknowledged = True
    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert


alert_rules_router = APIRouter(prefix="/alert-rules", tags=["alert-rules"])


@alert_rules_router.get("/", response_model=list[AlertRuleResponse])
def list_alert_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_alert_rules_for_tenant(db, current_user.tenant_id)


@alert_rules_router.post(
    "/", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED
)
def create_alert_rule(
    body: AlertRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    sensor = (
        db.query(Sensor)
        .filter(
            Sensor.id == body.sensor_id, Sensor.tenant_id == current_user.tenant_id
        )
        .first()
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    rule = AlertRule(
        tenant_id=current_user.tenant_id,
        sensor_id=body.sensor_id,
        name=body.name,
        description=body.description,
        condition=body.condition,
        threshold=body.threshold,
        threshold_max=body.threshold_max,
        severity=body.severity,
        cooldown_minutes=body.cooldown_minutes,
        notification_channels=body.notification_channels,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@alert_rules_router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    rule = (
        db.query(AlertRule)
        .filter(AlertRule.id == rule_id, AlertRule.tenant_id == current_user.tenant_id)
        .first()
    )
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    db.delete(rule)
    db.commit()
    return None
