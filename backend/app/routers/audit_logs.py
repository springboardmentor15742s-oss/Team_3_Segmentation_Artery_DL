from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import AuditLog, User
from app.schemas import AuditLogOut


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[
        User,
        Depends(require_roles("administrator")),
    ],
    limit: int = Query(default=100, ge=1, le=500),
):
    query = (
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )

    return list(db.scalars(query).all())
