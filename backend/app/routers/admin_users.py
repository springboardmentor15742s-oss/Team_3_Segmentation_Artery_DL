"""Administrator-only user listing and role management endpoints."""
from datetime import datetime, timezone
from typing import Annotated, Literal
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.database import get_db
from app.dependencies import require_roles
from app.models import User, UserSession
from app.schemas import UserOut

router = APIRouter(prefix="/admin/users", tags=["Administrator - User Management"])

RoleName = Literal["clinician", "researcher", "ml_engineer", "administrator"]


class UserRoleUpdate(BaseModel):
    role: RoleName


@router.get("", response_model=list[UserOut])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    _administrator: Annotated[User, Depends(require_roles("administrator"))],
):
    """Return registered users without password or session secrets."""
    return db.scalars(select(User).order_by(User.created_at.desc(), User.email.asc())).all()


@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: uuid.UUID,
    data: UserRoleUpdate,
    db: Annotated[Session, Depends(get_db)],
    administrator: Annotated[User, Depends(require_roles("administrator"))],
):
    """Update another user's role; only administrators may perform this action."""
    if user_id == administrator.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role.",
        )

    target = db.scalar(select(User).where(User.user_id == user_id).with_for_update())
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    previous_role = target.role
    if previous_role == data.role:
        return target

    if previous_role == "administrator" and data.role != "administrator":
        administrator_count = db.scalar(
            select(func.count()).select_from(User).where(User.role == "administrator", User.is_active.is_(True))
        ) or 0
        if administrator_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You cannot remove the last active administrator. Assign another administrator first.",
            )

    target.role = data.role
    # Force the affected user to sign in again so their frontend permissions refresh.
    now = datetime.now(timezone.utc)
    sessions = db.scalars(
        select(UserSession).where(UserSession.user_id == target.user_id, UserSession.revoked_at.is_(None))
    ).all()
    for session in sessions:
        session.revoked_at = now

    record_audit(
        db,
        user_id=administrator.user_id,
        action="user_role_updated",
        resource_type="user",
        resource_id=str(target.user_id),
        details={"target_email": target.email, "previous_role": previous_role, "new_role": data.role},
    )

    db.commit()
    db.refresh(target)
    return target
