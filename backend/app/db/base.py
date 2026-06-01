from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class FinanceEntityMixin(TimestampMixin):
    """Shared columns for Phase 3 finance entities.

    Adds project linkage, created/updated actor tracking, a generic record
    status and a soft-delete marker (``deleted_at``).
    """

    @declared_attr
    def project_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("projects.id"), index=True)

    @declared_attr
    def created_by_id(cls) -> Mapped[int | None]:
        return mapped_column(ForeignKey("users.id"), default=None)

    @declared_attr
    def updated_by_id(cls) -> Mapped[int | None]:
        return mapped_column(ForeignKey("users.id"), default=None)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")


# Import models so that Alembic / metadata.create_all can discover them.
# (Imported at the bottom to avoid circular imports.)
from app.models import (  # noqa: E402,F401
    audit_log,
    contract,
    cost_record,
    department,
    invoice,
    payment,
    permission,
    project,
    receipt,
    role,
    user,
    workflow,
)
