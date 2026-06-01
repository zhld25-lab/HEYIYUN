from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class ReceiptBase(BaseModel):
    receipt_code: str
    project_id: int
    contract_id: int | None = None
    payer_name: str | None = None
    receipt_amount: float = 0
    receipt_date: date | None = None
    planned_receipt_date: date | None = None
    is_overdue: bool = False
    remarks: str | None = None

    @field_validator("receipt_amount")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v is not None and v < 0:
            raise ValueError("金额不能为负数")
        return v


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    contract_id: int | None = None
    payer_name: str | None = None
    receipt_amount: float | None = None
    receipt_date: date | None = None
    planned_receipt_date: date | None = None
    is_overdue: bool | None = None
    remarks: str | None = None


class ReceiptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    receipt_code: str
    project_id: int
    project_name: str | None = None
    contract_id: int | None = None
    contract_name: str | None = None
    payer_name: str | None = None
    receipt_amount: Any = 0
    receipt_date: date | None = None
    planned_receipt_date: date | None = None
    is_overdue: bool = False
    remarks: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
