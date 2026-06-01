from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    username: str | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    detail: str | None = None
    ip_address: str | None = None
    created_at: datetime | None = None


class ResponseModel(BaseModel, Generic[T]):
    """Standard API response envelope."""

    code: int = 0
    message: str = "success"
    data: T | None = None


class PageMeta(BaseModel):
    total: int
    page: int
    page_size: int


class PageData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20
