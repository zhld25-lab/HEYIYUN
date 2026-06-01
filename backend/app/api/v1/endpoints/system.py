from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import PERM_AUDIT_VIEW
from app.crud.crud_audit_log import crud_audit_log
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import AuditLogOut, PageData, ResponseModel

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/audit-logs", response_model=ResponseModel[PageData[AuditLogOut]])
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    resource_type: str | None = None,
    resource_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(PERM_AUDIT_VIEW)),
) -> ResponseModel[PageData[AuditLogOut]]:
    items, total = crud_audit_log.list_paginated(
        db,
        skip=(page - 1) * page_size,
        limit=page_size,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    data = PageData(
        items=[AuditLogOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ResponseModel(data=data)
