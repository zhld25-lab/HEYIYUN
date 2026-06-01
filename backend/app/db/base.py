from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# Import models so that Alembic / metadata.create_all can discover them.
# (Imported at the bottom to avoid circular imports.)
from app.models import (  # noqa: E402,F401
    audit_log,
    department,
    permission,
    project,
    role,
    user,
)
