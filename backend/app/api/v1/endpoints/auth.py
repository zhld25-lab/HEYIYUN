from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenData
from app.schemas.common import ResponseModel
from app.schemas.user import UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ResponseModel[TokenData])
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> ResponseModel[TokenData]:
    user = auth_service.authenticate(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    token = auth_service.issue_token(user)
    data = TokenData(access_token=token, user=UserOut.model_validate(user))
    return ResponseModel(data=data)


@router.get("/me", response_model=ResponseModel[UserOut])
def me(current_user: User = Depends(get_current_user)) -> ResponseModel[UserOut]:
    return ResponseModel(data=UserOut.model_validate(current_user))
