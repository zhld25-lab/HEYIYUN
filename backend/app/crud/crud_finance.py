from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDFinance(Generic[ModelType]):
    """Generic CRUD for soft-deletable finance entities (Contract/Cost/...)."""

    def __init__(self, model: type[ModelType], code_field: str):
        self.model = model
        self.code_field = code_field

    def get(self, db: Session, id: int) -> ModelType | None:
        obj = db.get(self.model, id)
        if obj is None or obj.deleted_at is not None:
            return None
        return obj

    def get_by_code(self, db: Session, code: str) -> ModelType | None:
        col = getattr(self.model, self.code_field)
        return db.scalar(select(self.model).where(col == code, self.model.deleted_at.is_(None)))

    def create(self, db: Session, obj: ModelType) -> ModelType:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def soft_delete(self, db: Session, obj: ModelType) -> None:
        obj.deleted_at = datetime.now(timezone.utc)
        obj.status = "deleted"
        db.add(obj)
        db.commit()

    def list_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        conditions: list[Any] | None = None,
    ) -> tuple[list[ModelType], int]:
        conditions = conditions or []
        base = [self.model.deleted_at.is_(None), *conditions]
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)
        for cond in base:
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)
        total = db.scalar(count_stmt) or 0
        stmt = stmt.order_by(self.model.id.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all()), total
