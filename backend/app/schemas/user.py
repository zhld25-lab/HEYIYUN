from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    is_active: bool
    role_code: str | None = None
    role_name: str | None = None
    permission_codes: list[str] = []


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role_code: str | None = None
