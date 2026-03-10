from sqlalchemy.orm import Session

from src.models.report import Report


def get_reports_for_tenant(db: Session, tenant_id: str) -> list[Report]:
    return (
        db.query(Report)
        .filter(Report.tenant_id == tenant_id)
        .order_by(Report.created_at.desc())
        .all()
    )
