from typing import Any
from sqlalchemy.orm import Session
from app.models import AuditLog


def record_audit(
    db: Session,
    *,
    user_id,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    outcome: str = "success",
    details: dict[str, Any] | None = None,
    commit: bool = False,
) -> None:
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        details=details,
    ))
    if commit:
        db.commit()
