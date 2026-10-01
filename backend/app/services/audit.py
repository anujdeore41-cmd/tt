"""Audit log service: record important actions with user, previous/new values."""
from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditLog


def _ip(request: Request | None) -> str:
    if request is None:
        return ""
    return request.client.host if request.client else ""


def record_audit(
    db: Session,
    action: str,
    entity_type: str = "",
    entity_id: str | int = "",
    previous_value: dict | None = None,
    new_value: dict | None = None,
    reason: str = "",
    user=None,
    request: Request | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user.id if user is not None else None,
        user_label=(user.username if user is not None else "system"),
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        previous_value=previous_value or {},
        new_value=new_value or {},
        reason=reason,
        ip_address=_ip(request),
    )
    db.add(log)
    db.flush()
    return log
