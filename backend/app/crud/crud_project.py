from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.project import Project


class CRUDProject(CRUDBase[Project]):
    def get_by_code(self, db: Session, project_code: str) -> Project | None:
        return db.scalar(select(Project).where(Project.project_code == project_code))

    def list_filtered(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        project_name: str | None = None,
        project_code: str | None = None,
        project_type: str | None = None,
        voltage_level: str | None = None,
        project_status: str | None = None,
        risk_level: str | None = None,
    ) -> tuple[list[Project], int]:
        stmt = select(Project)
        count_stmt = select(func.count()).select_from(Project)

        conditions = []
        if project_name:
            conditions.append(Project.project_name.ilike(f"%{project_name}%"))
        if project_code:
            conditions.append(Project.project_code.ilike(f"%{project_code}%"))
        if project_type:
            conditions.append(Project.project_type == project_type)
        if voltage_level:
            conditions.append(Project.voltage_level == voltage_level)
        if project_status:
            conditions.append(Project.project_status == project_status)
        if risk_level:
            conditions.append(Project.risk_level == risk_level)

        for cond in conditions:
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        total = db.scalar(count_stmt) or 0
        stmt = stmt.order_by(Project.id.desc()).offset(skip).limit(limit)
        items = list(db.scalars(stmt).all())
        return items, total


crud_project = CRUDProject(Project)
