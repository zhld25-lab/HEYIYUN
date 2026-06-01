from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.department import Department
from app.models.role import Role


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), default=None)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), default=None)

    role: Mapped[Role | None] = relationship(lazy="selectin")
    department: Mapped[Department | None] = relationship(lazy="selectin")

    @property
    def role_code(self) -> str | None:
        return self.role.code if self.role else None

    @property
    def role_name(self) -> str | None:
        return self.role.name if self.role else None

    @property
    def permission_codes(self) -> list[str]:
        return self.role.permission_codes if self.role else []
