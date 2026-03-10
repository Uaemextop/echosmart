from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.middleware.auth import get_current_user
from src.models.report import Report
from src.models.user import User
from src.schemas.report import ReportCreate, ReportResponse, ReportGenerateResponse
from src.services.report_service import get_reports_for_tenant

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/", response_model=list[ReportResponse])
def list_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_reports_for_tenant(db, current_user.tenant_id)


@router.post(
    "/generate",
    response_model=ReportGenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_report(
    body: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    report = Report(
        tenant_id=current_user.tenant_id,
        requested_by=current_user.id,
        title=body.title,
        format=body.format,
        date_from=body.date_from,
        date_to=body.date_to,
        sensors=body.sensors,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return ReportGenerateResponse(report_id=report.id, status=report.status)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = (
        db.query(Report)
        .filter(
            Report.id == report_id, Report.tenant_id == current_user.tenant_id
        )
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
