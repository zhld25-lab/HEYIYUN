from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project

ACTIVE_STATUSES = ("报装中", "施工中", "验收中")
HIGH_RISK_LEVELS = ("高", "严重")


def get_summary(db: Session) -> dict:
    projects = list(db.scalars(select(Project)).all())
    contract_amount = sum(float(p.contract_amount or 0) for p in projects)
    received = sum(float(p.received_amount or 0) for p in projects)
    paid = sum(float(p.paid_amount or 0) for p in projects)
    actual_cost = sum(float(p.actual_cost or 0) for p in projects)
    return {
        "project_count": len(projects),
        "active_project_count": sum(1 for p in projects if p.project_status in ACTIVE_STATUSES),
        "contract_amount": round(contract_amount, 2),
        "received_amount": round(received, 2),
        "paid_amount": round(paid, 2),
        "current_profit": round(received - actual_cost, 2),
        "high_risk_count": sum(1 for p in projects if p.risk_level in HIGH_RISK_LEVELS),
    }


def get_project_status_distribution(db: Session) -> list[dict]:
    stmt = select(Project.project_status, func.count()).group_by(Project.project_status)
    return [{"status": status, "count": count} for status, count in db.execute(stmt).all()]
