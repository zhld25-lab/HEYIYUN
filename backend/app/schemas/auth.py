from __future__ import annotations

from pydantic import BaseModel

from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
