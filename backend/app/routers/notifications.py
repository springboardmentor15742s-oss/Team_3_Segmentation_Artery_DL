
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Notification, User
from app.schemas import NotificationOut


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationOut],
)
def list_notifications(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    unread_only: bool = False,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):
    """
    List notifications belonging only to the authenticated user.
    """

    stmt = (
        select(Notification)
        .where(
            Notification.user_id == user.user_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .limit(limit)
    )

    if unread_only:
        stmt = stmt.where(
            Notification.is_read.is_(False)
        )

    return list(
        db.scalars(stmt).all()
    )


@router.post(
    "/{notification_id}/read",
    response_model=NotificationOut,
)
def mark_notification_read(
    notification_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """
    Mark one of the authenticated user's notifications as read.
    """

    stmt = select(Notification).where(
        Notification.notification_id == notification_id,
        Notification.user_id == user.user_id,
    )

    record = db.scalar(stmt)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    record.is_read = True

    record_audit(
        db,
        user_id=user.user_id,
        action="notification_marked_read",
        resource_type="notification",
        resource_id=str(record.notification_id),
    )

    db.commit()
    db.refresh(record)

    return record


@router.post(
    "/read-all",
    status_code=status.HTTP_200_OK,
)
def mark_all_read(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    """
    Mark all unread notifications belonging to the
    authenticated user as read.
    """

    stmt = select(Notification).where(
        Notification.user_id == user.user_id,
        Notification.is_read.is_(False),
    )

    records = list(
        db.scalars(stmt).all()
    )

    for record in records:
        record.is_read = True

    record_audit(
        db,
        user_id=user.user_id,
        action="notifications_marked_read",
        resource_type="notification",
        details={
            "count": len(records),
        },
    )

    db.commit()

    return {
        "updated": len(records),
    }
