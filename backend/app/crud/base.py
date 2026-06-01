from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> ModelType | None:
        return db.get(self.model, id)

    def list(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    def create(self, db: Session, obj: ModelType) -> ModelType:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def remove(self, db: Session, db_obj: ModelType) -> None:
        db.delete(db_obj)
        db.commit()
