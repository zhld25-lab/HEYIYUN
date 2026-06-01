from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

COST_TYPES = [
    "分包成本",
    "材料成本",
    "人工成本",
    "机械设备成本",
    "周材租赁成本",
    "运输成本",
    "费用报销",
    "间接成本",
    "税费",
    "其他成本",
]
PAYMENT_STATUSES = ["未付款", "部分付款", "已付款"]
INVOICE_STATUSES = ["未收票", "部分收票", "已收票"]


class CostBase(BaseModel):
    cost_code: str
    cost_type: str
    project_id: int
    contract_id: int | None = None
    supplier_name: str | None = None
    amount: float = 0
    occurred_date: date | None = None
    handler_name: str | None = None
    approval_status: str = "未提交"
    invoice_status: str = "未收票"
    payment_status: str = "未付款"
    remarks: str | None = None

    @field_validator("cost_type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in COST_TYPES:
            raise ValueError(f"无效的成本类型: {v}")
        return v

    @field_validator("amount")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v is not None and v < 0:
            raise ValueError("金额不能为负数")
        return v


class CostCreate(CostBase):
    pass


class CostUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    cost_type: str | None = None
    contract_id: int | None = None
    supplier_name: str | None = None
    amount: float | None = None
    occurred_date: date | None = None
    handler_name: str | None = None
    approval_status: str | None = None
    invoice_status: str | None = None
    payment_status: str | None = None
    remarks: str | None = None


class CostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cost_code: str
    cost_type: str
    project_id: int
    project_name: str | None = None
    contract_id: int | None = None
    contract_name: str | None = None
    supplier_name: str | None = None
    amount: Any = 0
    occurred_date: date | None = None
    handler_name: str | None = None
    approval_status: str
    invoice_status: str
    payment_status: str
    remarks: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
