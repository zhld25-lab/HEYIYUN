from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def record(
    db: Session,
    *,
    user: User | None,
    action: str,
    resource_type: str,
    resource_id: str | int | None = None,
    detail: dict[str, Any] | str | None = None,
    ip_address: str | None = None,
    commit: bool = True,
) -> AuditLog:
    """Persist an audit log entry for a create/update/delete operation."""
    if isinstance(detail, dict):
        detail_str = json.dumps(detail, ensure_ascii=False, default=str)
    else:
        detail_str = detail

    log = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        detail=detail_str,
        ip_address=ip_address,
    )
    db.add(log)
    if commit:
        db.commit()
    return log
