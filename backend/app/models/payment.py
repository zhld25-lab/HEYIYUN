from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, FinanceEntityMixin


class Payment(Base, FinanceEntityMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    payment_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), default=None, index=True)

    payee_name: Mapped[str | None] = mapped_column(String(255), default=None)
    requested_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    paid_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    payment_date: Mapped[date | None] = mapped_column(Date, default=None)

    payment_status: Mapped[str] = mapped_column(String(32), default="未付款")
    approval_status: Mapped[str] = mapped_column(String(32), default="未提交")

    remarks: Mapped[str | None] = mapped_column(Text, default=None)

    project = relationship("Project", lazy="selectin")
    contract = relationship("Contract", lazy="selectin")

    @property
    def project_name(self) -> str | None:
        return self.project.project_name if self.project else None

    @property
    def contract_name(self) -> str | None:
        return self.contract.contract_name if self.contract else None
