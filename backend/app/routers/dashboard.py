from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import AnalysisResult, ImageRecord, MedicalCase, Notification, User
from app.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _scope_case(stmt, user: User):
    return stmt if user.role == "administrator" else stmt.where(MedicalCase.owner_user_id == user.user_id)


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    cases_stmt = select(func.count(MedicalCase.case_id))
    pending_stmt = select(func.count(MedicalCase.case_id)).where(MedicalCase.case_status == "Pending")
    processing_stmt = select(func.count(MedicalCase.case_id)).where(MedicalCase.case_status == "Processing")
    completed_stmt = select(func.count(MedicalCase.case_id)).where(MedicalCase.case_status == "Completed")
    failed_stmt = select(func.count(MedicalCase.case_id)).where(MedicalCase.case_status == "Failed")
    if user.role != "administrator":
        cases_stmt = cases_stmt.where(MedicalCase.owner_user_id == user.user_id)
        pending_stmt = pending_stmt.where(MedicalCase.owner_user_id == user.user_id)
        processing_stmt = processing_stmt.where(MedicalCase.owner_user_id == user.user_id)
        completed_stmt = completed_stmt.where(MedicalCase.owner_user_id == user.user_id)
        failed_stmt = failed_stmt.where(MedicalCase.owner_user_id == user.user_id)
    total_cases = int(db.scalar(cases_stmt) or 0)
    pending = int(db.scalar(pending_stmt) or 0)
    processing = int(db.scalar(processing_stmt) or 0)
    completed = int(db.scalar(completed_stmt) or 0)
    failed = int(db.scalar(failed_stmt) or 0)

    image_stmt = select(func.count(ImageRecord.image_id)).join(MedicalCase, ImageRecord.case_id == MedicalCase.case_id)
    result_stmt = select(func.count(AnalysisResult.result_id)).join(MedicalCase, AnalysisResult.case_id == MedicalCase.case_id)
    if user.role != "administrator":
        image_stmt = image_stmt.where(MedicalCase.owner_user_id == user.user_id)
        result_stmt = result_stmt.where(MedicalCase.owner_user_id == user.user_id)
    images = int(db.scalar(image_stmt) or 0)
    results = int(db.scalar(result_stmt) or 0)

    unread_stmt = select(func.count(Notification.notification_id)).where(Notification.is_read.is_(False))
    if user.role != "administrator":
        unread_stmt = unread_stmt.where(Notification.user_id == user.user_id)
    unread = int(db.scalar(unread_stmt) or 0)

    recent_stmt = select(MedicalCase).order_by(MedicalCase.created_at.desc()).limit(5)
    if user.role != "administrator":
        recent_stmt = recent_stmt.where(MedicalCase.owner_user_id == user.user_id)
    recent_cases = list(db.scalars(recent_stmt).all())
    return DashboardSummary(
        total_cases=total_cases, pending_cases=pending, processing_cases=processing,
        completed_cases=completed, failed_cases=failed, images_uploaded=images,
        stored_result_records=results, unread_notifications=unread, recent_cases=recent_cases,
    )
