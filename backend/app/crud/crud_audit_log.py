from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.audit_log import AuditLog


class CRUDAuditLog(CRUDBase[AuditLog]):
    def list_paginated(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        resource_type: str | None = None,
        resource_id: str | None = None,
    ) -> tuple[list[AuditLog], int]:
        stmt = select(AuditLog)
        count_stmt = select(func.count()).select_from(AuditLog)
        if resource_type:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
            count_stmt = count_stmt.where(AuditLog.resource_type == resource_type)
        if resource_id:
            stmt = stmt.where(AuditLog.resource_id == resource_id)
            count_stmt = count_stmt.where(AuditLog.resource_id == resource_id)
        total = db.scalar(count_stmt) or 0
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        items = list(db.scalars(stmt).all())
        return items, total


crud_audit_log = CRUDAuditLog(AuditLog)
