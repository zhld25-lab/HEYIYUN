from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import PERM_USER_VIEW
from app.crud.crud_user import crud_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=ResponseModel[list[UserOut]])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission(PERM_USER_VIEW)),
) -> ResponseModel[list[UserOut]]:
    users = crud_user.list(db, limit=500)
    return ResponseModel(data=[UserOut.model_validate(u) for u in users])
