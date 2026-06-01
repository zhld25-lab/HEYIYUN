from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, FinanceEntityMixin


class Invoice(Base, FinanceEntityMixin):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)

    invoice_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    invoice_type: Mapped[str] = mapped_column(String(32), default="增值税专用发票")
    invoice_direction: Mapped[str] = mapped_column(String(8), default="销项", index=True)  # 进项 / 销项
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), default=None, index=True)

    amount: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    tax_rate: Mapped[float] = mapped_column(Numeric(6, 4), default=0)
    invoice_date: Mapped[date | None] = mapped_column(Date, default=None)
    certification_status: Mapped[str] = mapped_column(String(32), default="未认证")

    remarks: Mapped[str | None] = mapped_column(Text, default=None)

    project = relationship("Project", lazy="selectin")
    contract = relationship("Contract", lazy="selectin")

    @property
    def project_name(self) -> str | None:
        return self.project.project_name if self.project else None

    @property
    def contract_name(self) -> str | None:
        return self.contract.contract_name if self.contract else None
