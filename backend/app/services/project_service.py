from __future__ import annotations

"""Project domain logic.

Derived metrics (profit, profit_margin, cost_ratio) follow the same intent as
the legacy Streamlit prototype (legacy_streamlit/services/project_service.py
and risk_service.py).
"""

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def _to_float(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def recompute_derived_fields(project: Project) -> None:
    """Recompute profit / profit_margin / cost_ratio from base amounts."""
    contract_amount = _to_float(project.contract_amount)
    actual_cost = _to_float(project.actual_cost)
    target_cost = _to_float(project.target_cost)

    project.profit = round(contract_amount - actual_cost, 2)
    project.profit_margin = round(project.profit / contract_amount, 4) if contract_amount else 0
    project.cost_ratio = round(actual_cost / target_cost, 4) if target_cost else 0


def create_project_obj(payload: ProjectCreate) -> Project:
    project = Project(**payload.model_dump())
    recompute_derived_fields(project)
    return project


def apply_update(project: Project, payload: ProjectUpdate) -> None:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    recompute_derived_fields(project)
