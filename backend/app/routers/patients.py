import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.database import get_db
from app.dependencies import get_current_user
from app.models import PatientRecord, User
from app.schemas import PatientCreate, PatientOut, PatientUpdate


router = APIRouter(
    prefix="/patients",
    tags=["Patient / De-identified Records"],
)


# Roles allowed to create or update patient records.
PATIENT_WRITE_ROLES = {
    "clinician",
    "researcher",
    "administrator",
}

# Roles allowed to delete patient records.
PATIENT_DELETE_ROLES = {
    "clinician",
    "administrator",
}


def require_patient_write_permission(user: User) -> None:
    if user.role not in PATIENT_WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role does not have permission to create or update patient records.",
        )


def require_patient_delete_permission(user: User) -> None:
    if user.role not in PATIENT_DELETE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role does not have permission to delete patient records.",
        )


def get_patient(
    patient_id: uuid.UUID,
    user: User,
    db: Session,
) -> PatientRecord:
    stmt = select(PatientRecord).where(
        PatientRecord.patient_id == patient_id
    )

    # Administrators can access all patient records.
    # Other roles can access only their own records.
    if user.role != "administrator":
        stmt = stmt.where(
            PatientRecord.owner_user_id == user.user_id
        )

    patient = db.scalar(stmt)

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient record not found.",
        )

    return patient


@router.post(
    "",
    response_model=PatientOut,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    data: PatientCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    require_patient_write_permission(user)

    patient = PatientRecord(
        owner_user_id=user.user_id,
        **data.model_dump(),
    )

    db.add(patient)
    db.flush()

    record_audit(
        db,
        user_id=user.user_id,
        action="patient_record_created",
        resource_type="patient",
        resource_id=str(patient.patient_id),
    )

    db.commit()
    db.refresh(patient)

    return patient


@router.get(
    "",
    response_model=list[PatientOut],
)
def list_patients(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    q: str | None = Query(default=None, max_length=80),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    stmt = select(PatientRecord).order_by(
        PatientRecord.created_at.desc()
    )

    # Administrators can list all patient records.
    # Other roles can list only their own records.
    if user.role != "administrator":
        stmt = stmt.where(
            PatientRecord.owner_user_id == user.user_id
        )

    if q:
        stmt = stmt.where(
            PatientRecord.display_code.ilike(
                f"%{q.strip()}%"
            )
        )

    return list(
        db.scalars(
            stmt.offset(offset).limit(limit)
        ).all()
    )


@router.get(
    "/{patient_id}",
    response_model=PatientOut,
)
def read_patient(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return get_patient(patient_id, user, db)


@router.patch(
    "/{patient_id}",
    response_model=PatientOut,
)
def update_patient(
    patient_id: uuid.UUID,
    data: PatientUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    require_patient_write_permission(user)

    patient = get_patient(patient_id, user, db)

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(
            patient,
            field,
            value.strip() if isinstance(value, str) else value,
        )

    record_audit(
        db,
        user_id=user.user_id,
        action="patient_record_updated",
        resource_type="patient",
        resource_id=str(patient.patient_id),
        details={
            "fields": sorted(changes.keys())
        },
    )

    db.commit()
    db.refresh(patient)

    return patient


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    require_patient_delete_permission(user)

    patient = get_patient(patient_id, user, db)

    # Cases retain their data and clear their optional patient link
    # through the database's ON DELETE SET NULL behavior.
    record_audit(
        db,
        user_id=user.user_id,
        action="patient_record_deleted",
        resource_type="patient",
        resource_id=str(patient.patient_id),
    )

    db.delete(patient)
    db.commit()

    return None
