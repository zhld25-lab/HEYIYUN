from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, FinanceEntityMixin


class Receipt(Base, FinanceEntityMixin):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True)

    receipt_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), default=None, index=True)

    payer_name: Mapped[str | None] = mapped_column(String(255), default=None)
    receipt_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    receipt_date: Mapped[date | None] = mapped_column(Date, default=None)
    planned_receipt_date: Mapped[date | None] = mapped_column(Date, default=None)
    is_overdue: Mapped[bool] = mapped_column(Boolean, default=False)

    remarks: Mapped[str | None] = mapped_column(Text, default=None)

    project = relationship("Project", lazy="selectin")
    contract = relationship("Contract", lazy="selectin")

    @property
    def project_name(self) -> str | None:
        return self.project.project_name if self.project else None

    @property
    def contract_name(self) -> str | None:
        return self.contract.contract_name if self.contract else None
