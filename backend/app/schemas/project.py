from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

# Reference enums (kept in sync with frontend constants and legacy prototype).
PROJECT_TYPES = [
    "10kV配电工程",
    "220kV输变电工程",
    "光伏并网工程",
    "充电桩配套电力工程",
    "小区电力改造",
    "工业园配电",
    "电缆迁改",
    "临时用电",
    "箱变安装",
    "架空线路改造",
]
VOLTAGE_LEVELS = ["0.4kV", "10kV", "35kV", "110kV", "220kV"]
PROJECT_STATUSES = ["立项", "报装中", "施工中", "验收中", "结算中", "已完工", "暂停", "取消"]
RISK_LEVELS = ["低", "中", "高", "严重"]


class ProjectBase(BaseModel):
    project_code: str
    project_name: str
    project_type: str
    voltage_level: str | None = None
    project_location: str | None = None
    region: str | None = None
    project_status: str = "立项"

    owner_unit: str | None = None
    construction_unit: str | None = None
    design_unit: str | None = None
    supervision_unit: str | None = None
    project_manager_id: int | None = None

    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None

    contract_amount: float = 0
    target_cost: float = 0
    actual_cost: float = 0
    received_amount: float = 0
    paid_amount: float = 0
    receivable_amount: float = 0
    payable_amount: float = 0

    production_progress: float = 0
    collection_progress: float = 0
    document_completion_rate: float = 0
    risk_level: str = "低"

    description: str | None = None
    remarks: str | None = None

    @field_validator("contract_amount", "target_cost", "actual_cost")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v is not None and v < 0:
            raise ValueError("金额不能为负数")
        return v

    @field_validator("project_type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in PROJECT_TYPES:
            raise ValueError(f"无效的项目类型: {v}")
        return v

    @model_validator(mode="after")
    def check_dates(self) -> "ProjectBase":
        if self.planned_start_date and self.planned_end_date:
            if self.planned_end_date <= self.planned_start_date:
                raise ValueError("计划结束日期必须晚于计划开始日期")
        return self


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    """All fields optional for partial update."""

    model_config = ConfigDict(extra="ignore")

    project_name: str | None = None
    project_type: str | None = None
    voltage_level: str | None = None
    project_location: str | None = None
    region: str | None = None
    project_status: str | None = None
    owner_unit: str | None = None
    construction_unit: str | None = None
    design_unit: str | None = None
    supervision_unit: str | None = None
    project_manager_id: int | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None
    contract_amount: float | None = None
    target_cost: float | None = None
    actual_cost: float | None = None
    received_amount: float | None = None
    paid_amount: float | None = None
    receivable_amount: float | None = None
    payable_amount: float | None = None
    production_progress: float | None = None
    collection_progress: float | None = None
    document_completion_rate: float | None = None
    risk_level: str | None = None
    description: str | None = None
    remarks: str | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_code: str
    project_name: str
    project_type: str
    voltage_level: str | None = None
    project_location: str | None = None
    region: str | None = None
    project_status: str

    owner_unit: str | None = None
    construction_unit: str | None = None
    design_unit: str | None = None
    supervision_unit: str | None = None
    project_manager_id: int | None = None
    project_manager_name: str | None = None

    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None

    # Financial fields are typed as Any so the service layer can mask them ("***").
    contract_amount: Any = 0
    target_cost: Any = 0
    actual_cost: Any = 0
    received_amount: Any = 0
    paid_amount: Any = 0
    receivable_amount: Any = 0
    payable_amount: Any = 0
    profit: Any = 0
    profit_margin: Any = 0

    production_progress: float = 0
    collection_progress: float = 0
    cost_ratio: float = 0
    document_completion_rate: float = 0
    risk_level: str = "低"

    description: str | None = None
    remarks: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
