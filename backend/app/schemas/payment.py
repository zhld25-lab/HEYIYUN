from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

PAYMENT_STATUSES = ["未付款", "部分付款", "已付款"]
APPROVAL_STATUSES = ["未提交", "审批中", "已通过", "已驳回"]


class PaymentBase(BaseModel):
    payment_code: str
    project_id: int
    contract_id: int | None = None
    payee_name: str | None = None
    requested_amount: float = 0
    paid_amount: float = 0
    payment_date: date | None = None
    payment_status: str = "未付款"
    approval_status: str = "未提交"
    remarks: str | None = None

    @field_validator("requested_amount", "paid_amount")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v is not None and v < 0:
            raise ValueError("金额不能为负数")
        return v


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    contract_id: int | None = None
    payee_name: str | None = None
    requested_amount: float | None = None
    paid_amount: float | None = None
    payment_date: date | None = None
    payment_status: str | None = None
    approval_status: str | None = None
    remarks: str | None = None


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_code: str
    project_id: int
    project_name: str | None = None
    contract_id: int | None = None
    contract_name: str | None = None
    payee_name: str | None = None
    requested_amount: Any = 0
    paid_amount: Any = 0
    payment_date: date | None = None
    payment_status: str
    approval_status: str
    remarks: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
