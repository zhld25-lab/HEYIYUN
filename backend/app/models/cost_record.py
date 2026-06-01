from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, FinanceEntityMixin


class CostRecord(Base, FinanceEntityMixin):
    __tablename__ = "cost_records"

    id: Mapped[int] = mapped_column(primary_key=True)

    cost_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    cost_type: Mapped[str] = mapped_column(String(32), index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), default=None, index=True)

    supplier_name: Mapped[str | None] = mapped_column(String(255), default=None)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    occurred_date: Mapped[date | None] = mapped_column(Date, default=None)
    handler_name: Mapped[str | None] = mapped_column(String(64), default=None)

    approval_status: Mapped[str] = mapped_column(String(32), default="未提交")
    invoice_status: Mapped[str] = mapped_column(String(32), default="未收票")
    payment_status: Mapped[str] = mapped_column(String(32), default="未付款")

    remarks: Mapped[str | None] = mapped_column(Text, default=None)

    project = relationship("Project", lazy="selectin")
    contract = relationship("Contract", lazy="selectin")

    @property
    def project_name(self) -> str | None:
        return self.project.project_name if self.project else None

    @property
    def contract_name(self) -> str | None:
        return self.contract.contract_name if self.contract else None
