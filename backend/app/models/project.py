from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.user import User


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Basic information
    project_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    project_name: Mapped[str] = mapped_column(String(255), index=True)
    project_type: Mapped[str] = mapped_column(String(64))
    voltage_level: Mapped[str | None] = mapped_column(String(32), default=None)
    project_location: Mapped[str | None] = mapped_column(String(255), default=None)
    region: Mapped[str | None] = mapped_column(String(64), default=None)
    project_status: Mapped[str] = mapped_column(String(32), default="立项", index=True)

    # Participating units
    owner_unit: Mapped[str | None] = mapped_column(String(255), default=None)
    construction_unit: Mapped[str | None] = mapped_column(String(255), default=None)
    design_unit: Mapped[str | None] = mapped_column(String(255), default=None)
    supervision_unit: Mapped[str | None] = mapped_column(String(255), default=None)
    project_manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), default=None)

    # Time plan
    planned_start_date: Mapped[date | None] = mapped_column(Date, default=None)
    planned_end_date: Mapped[date | None] = mapped_column(Date, default=None)
    actual_start_date: Mapped[date | None] = mapped_column(Date, default=None)
    actual_end_date: Mapped[date | None] = mapped_column(Date, default=None)

    # Financials (stored with 2 decimal precision)
    contract_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    target_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    actual_cost: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    received_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    paid_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    receivable_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    payable_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    profit: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    profit_margin: Mapped[float] = mapped_column(Numeric(8, 4), default=0)

    # Progress / documents / risk
    production_progress: Mapped[float] = mapped_column(Numeric(6, 4), default=0)
    collection_progress: Mapped[float] = mapped_column(Numeric(6, 4), default=0)
    cost_ratio: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    document_completion_rate: Mapped[float] = mapped_column(Numeric(6, 4), default=0)
    risk_level: Mapped[str] = mapped_column(String(16), default="低")

    # Free text
    description: Mapped[str | None] = mapped_column(Text, default=None)
    remarks: Mapped[str | None] = mapped_column(Text, default=None)

    project_manager: Mapped[User | None] = relationship(lazy="selectin")

    @property
    def project_manager_name(self) -> str | None:
        return self.project_manager.full_name if self.project_manager else None
