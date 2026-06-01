from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User


class CRUDUser(CRUDBase[User]):
    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.scalar(select(User).where(User.username == username))


crud_user = CRUDUser(User)
