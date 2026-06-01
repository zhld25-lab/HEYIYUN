from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, FinanceEntityMixin


class Contract(Base, FinanceEntityMixin):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)

    contract_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    contract_name: Mapped[str] = mapped_column(String(255), index=True)
    contract_type: Mapped[str] = mapped_column(String(32), index=True)

    party_a: Mapped[str | None] = mapped_column(String(255), default=None)
    party_b: Mapped[str | None] = mapped_column(String(255), default=None)

    contract_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    settlement_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    invoiced_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    received_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    paid_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    receivable_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    payable_amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)

    contract_status: Mapped[str] = mapped_column(String(32), default="拟定")
    approval_status: Mapped[str] = mapped_column(String(32), default="未提交")
    archive_status: Mapped[str] = mapped_column(String(32), default="未归档")

    signed_date: Mapped[date | None] = mapped_column(Date, default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    remarks: Mapped[str | None] = mapped_column(Text, default=None)

    project = relationship("Project", lazy="selectin")

    @property
    def project_name(self) -> str | None:
        return self.project.project_name if self.project else None
