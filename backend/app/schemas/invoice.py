from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

INVOICE_TYPES = ["增值税专用发票", "增值税普通发票", "电子发票"]
INVOICE_DIRECTIONS = ["进项", "销项"]
CERTIFICATION_STATUSES = ["未认证", "已认证", "无需认证"]


class InvoiceBase(BaseModel):
    invoice_code: str
    invoice_type: str = "增值税专用发票"
    invoice_direction: str = "销项"
    project_id: int
    contract_id: int | None = None
    amount: float = 0
    tax_rate: float = 0
    invoice_date: date | None = None
    certification_status: str = "未认证"
    remarks: str | None = None

    @field_validator("invoice_direction")
    @classmethod
    def valid_direction(cls, v: str) -> str:
        if v not in INVOICE_DIRECTIONS:
            raise ValueError(f"无效的发票方向: {v}")
        return v

    @field_validator("amount")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v is not None and v < 0:
            raise ValueError("金额不能为负数")
        return v


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    invoice_type: str | None = None
    invoice_direction: str | None = None
    contract_id: int | None = None
    amount: float | None = None
    tax_rate: float | None = None
    invoice_date: date | None = None
    certification_status: str | None = None
    remarks: str | None = None


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_code: str
    invoice_type: str
    invoice_direction: str
    project_id: int
    project_name: str | None = None
    contract_id: int | None = None
    contract_name: str | None = None
    amount: Any = 0
    tax_rate: Any = 0
    invoice_date: date | None = None
    certification_status: str
    remarks: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
