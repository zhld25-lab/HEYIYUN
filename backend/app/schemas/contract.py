from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

CONTRACT_TYPES = ["承包合同", "分包合同", "采购合同", "设备租赁合同", "周材租赁合同"]
CONTRACT_STATUSES = ["拟定", "审批中", "执行中", "结算中", "已归档"]
APPROVAL_STATUSES = ["未提交", "审批中", "已通过", "已驳回"]
ARCHIVE_STATUSES = ["未归档", "归档中", "已归档"]


class ContractBase(BaseModel):
    contract_code: str
    contract_name: str
    contract_type: str
    project_id: int
    party_a: str | None = None
    party_b: str | None = None
    contract_amount: float = 0
    settlement_amount: float = 0
    contract_status: str = "拟定"
    approval_status: str = "未提交"
    archive_status: str = "未归档"
    signed_date: date | None = None
    description: str | None = None
    remarks: str | None = None

    @field_validator("contract_type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in CONTRACT_TYPES:
            raise ValueError(f"无效的合同类型: {v}")
        return v

    @field_validator("contract_amount", "settlement_amount")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v is not None and v < 0:
            raise ValueError("金额不能为负数")
        return v


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    contract_name: str | None = None
    contract_type: str | None = None
    party_a: str | None = None
    party_b: str | None = None
    contract_amount: float | None = None
    settlement_amount: float | None = None
    contract_status: str | None = None
    approval_status: str | None = None
    archive_status: str | None = None
    signed_date: date | None = None
    description: str | None = None
    remarks: str | None = None


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_code: str
    contract_name: str
    contract_type: str
    project_id: int
    project_name: str | None = None
    party_a: str | None = None
    party_b: str | None = None

    contract_amount: Any = 0
    settlement_amount: Any = 0
    invoiced_amount: Any = 0
    received_amount: Any = 0
    paid_amount: Any = 0
    receivable_amount: Any = 0
    payable_amount: Any = 0

    contract_status: str
    approval_status: str
    archive_status: str
    signed_date: date | None = None
    description: str | None = None
    remarks: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
