
import uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, selectinload

from app.audit import record_audit
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    AnalysisHistory,
    MedicalCase,
    PatientRecord,
    User,
    Notification,
    ReportRecord,
)
from app.schemas import CaseCreate, CaseOut, CaseUpdate, HistoryOut


router = APIRouter(prefix="/cases", tags=["Case Management"])


# Roles allowed to create and update clinical cases.
CASE_WRITE_ROLES = {
    "clinician",
    "researcher",
    "administrator",
}

# Roles allowed to delete clinical cases.
CASE_DELETE_ROLES = {
    "clinician",
    "administrator",
}


def require_case_write_permission(user: User) -> None:
    """Ensure the current user can create or update clinical cases."""
    if user.role not in CASE_WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role does not have permission to create or update cases.",
        )


def require_case_delete_permission(user: User) -> None:
    """Ensure the current user can delete clinical cases."""
    if user.role not in CASE_DELETE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role does not have permission to delete cases.",
        )


def get_authorized_case(
    case_id: uuid.UUID,
    user: User,
    db: Session,
    include_images: bool = False,
) -> MedicalCase:
    statement = select(MedicalCase).where(
        MedicalCase.case_id == case_id
    )

    # Administrators can access all cases.
    # Other roles can access only their own cases.
    if user.role != "administrator":
        statement = statement.where(
            MedicalCase.owner_user_id == user.user_id
        )

    if include_images:
        statement = statement.options(
            selectinload(MedicalCase.images)
        )

    case = db.scalar(statement)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    return case


def validate_patient_link(
    patient_id,
    user: User,
    db: Session,
) -> None:
    """Ensure a case is linked only to an accessible patient record."""
    if patient_id is None:
        return

    statement = select(PatientRecord).where(
        PatientRecord.patient_id == patient_id
    )

    if user.role != "administrator":
        statement = statement.where(
            PatientRecord.owner_user_id == user.user_id
        )

    if db.scalar(statement) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient record not found.",
        )


@router.post(
    "",
    response_model=CaseOut,
    status_code=status.HTTP_201_CREATED,
)
def create_case(
    data: CaseCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    require_case_write_permission(user)

    validate_patient_link(
        data.patient_id,
        user,
        db,
    )

    case = MedicalCase(
        owner_user_id=user.user_id,
        patient_id=data.patient_id,
        case_name=data.case_name.strip(),
        imaging_modality=data.imaging_modality.strip(),
        anatomical_region=data.anatomical_region.strip(),
        scan_date=data.scan_date,
        notes=data.notes.strip() if data.notes else None,
        case_status="Pending",
    )

    db.add(case)
    db.flush()

    db.add(
        AnalysisHistory(
            case_id=case.case_id,
            action="Case created",
            status="Pending",
            message="Case was created.",
        )
    )

    db.add(
        Notification(
            user_id=user.user_id,
            case_id=case.case_id,
            alert_type="case_created",
            message=f"Case '{case.case_name}' was created.",
            severity="info",
        )
    )

    record_audit(
        db,
        user_id=user.user_id,
        action="case_created",
        resource_type="case",
        resource_id=str(case.case_id),
    )

    db.commit()
    db.refresh(case)

    return case


@router.get("", response_model=list[CaseOut])
def list_cases(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    case_status: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None, max_length=150),
    modality: str | None = Query(default=None, max_length=50),
    date_from: date | None = None,
    date_to: date | None = None,
):
    statement = select(MedicalCase).order_by(
        MedicalCase.created_at.desc()
    )

    if user.role != "administrator":
        statement = statement.where(
            MedicalCase.owner_user_id == user.user_id
        )

    if case_status:
        statement = statement.where(
            MedicalCase.case_status == case_status
        )

    if modality:
        statement = statement.where(
            MedicalCase.imaging_modality == modality
        )

    if date_from:
        statement = statement.where(
            MedicalCase.created_at >= date_from
        )

    if date_to:
        statement = statement.where(
            MedicalCase.created_at < date_to + timedelta(days=1)
        )

    if q and q.strip():
        pattern = f"%{q.strip()}%"

        statement = statement.where(
            or_(
                MedicalCase.case_name.ilike(pattern),
                MedicalCase.anatomical_region.ilike(pattern),
                MedicalCase.imaging_modality.ilike(pattern),
                MedicalCase.notes.ilike(pattern),
            )
        )

    statement = statement.offset(offset).limit(limit)

    return list(db.scalars(statement).all())


@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return get_authorized_case(
        case_id,
        user,
        db,
    )


@router.patch("/{case_id}", response_model=CaseOut)
def update_case(
    case_id: uuid.UUID,
    data: CaseUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    require_case_write_permission(user)

    case = get_authorized_case(
        case_id,
        user,
        db,
    )

    changes = data.model_dump(exclude_unset=True)

    if "patient_id" in changes:
        validate_patient_link(
            changes["patient_id"],
            user,
            db,
        )

    for field, value in changes.items():
        setattr(
            case,
            field,
            value.strip() if isinstance(value, str) else value,
        )

    db.add(
        AnalysisHistory(
            case_id=case.case_id,
            action="Case updated",
            status=case.case_status,
            message="Case details were updated.",
        )
    )

    record_audit(
        db,
        user_id=user.user_id,
        action="case_updated",
        resource_type="case",
        resource_id=str(case.case_id),
        details={"fields": sorted(changes.keys())},
    )

    db.commit()
    db.refresh(case)

    return case


@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_case(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    require_case_delete_permission(user)

    case = get_authorized_case(
        case_id,
        user,
        db,
        include_images=True,
    )

    file_paths: list[Path] = []

    upload_root = settings.upload_path.resolve()
    report_root = settings.report_path.resolve()

    case_id_str = str(case.case_id)

    for image in case.images:
        candidate = (
            upload_root / image.file_reference
        ).resolve()

        if candidate.is_relative_to(upload_root):
            file_paths.append(candidate)

        if image.preprocessed_reference:
            processed = (
                upload_root / image.preprocessed_reference
            ).resolve()

            if processed.is_relative_to(upload_root):
                file_paths.append(processed)

    report_records = list(
        db.scalars(
            select(ReportRecord).where(
                ReportRecord.case_id == case.case_id
            )
        ).all()
    )

    for report in report_records:
        candidate = (
            report_root / report.file_reference
        ).resolve()

        if candidate.is_relative_to(report_root):
            file_paths.append(candidate)

    record_audit(
        db,
        user_id=user.user_id,
        action="case_deleted",
        resource_type="case",
        resource_id=case_id_str,
    )

    db.delete(case)
    db.commit()

    for path in file_paths:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass

    return None


@router.get(
    "/{case_id}/history",
    response_model=list[HistoryOut],
)
def get_case_history(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    get_authorized_case(
        case_id,
        user,
        db,
    )

    statement = (
        select(AnalysisHistory)
        .where(AnalysisHistory.case_id == case_id)
        .order_by(AnalysisHistory.created_at.desc())
    )

    return list(db.scalars(statement).all())
