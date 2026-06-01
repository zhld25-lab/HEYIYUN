from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.crud.crud_user import crud_user
from app.models.user import User


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = crud_user.get_by_username(db, username)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def issue_token(user: User) -> str:
    return create_access_token(subject=user.id)
