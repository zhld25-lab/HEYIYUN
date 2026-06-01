from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import PERM_DASHBOARD_VIEW
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.dashboard import DashboardSummary, ProjectStatusItem
from app.schemas.finance import (
    CashflowItem,
    CostBreakdownItem,
    DashboardFinanceSummary,
    ProjectProfitItem,
)
from app.services import dashboard_service, finance_service
from app.services.permission_service import mask_dashboard_dict, mask_finance_dict

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=ResponseModel[DashboardSummary])
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_DASHBOARD_VIEW)),
) -> ResponseModel[DashboardSummary]:
    data = dashboard_service.get_summary(db)
    data = mask_dashboard_dict(data, current_user)
    return ResponseModel(data=DashboardSummary.model_validate(data))


@router.get("/project-status", response_model=ResponseModel[list[ProjectStatusItem]])
def project_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_DASHBOARD_VIEW)),
) -> ResponseModel[list[ProjectStatusItem]]:
    data = dashboard_service.get_project_status_distribution(db)
    return ResponseModel(data=[ProjectStatusItem.model_validate(d) for d in data])


@router.get("/finance-summary", response_model=ResponseModel[DashboardFinanceSummary])
def finance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_DASHBOARD_VIEW)),
) -> ResponseModel[DashboardFinanceSummary]:
    data = mask_dashboard_dict(finance_service.dashboard_finance_summary(db), current_user)
    return ResponseModel(data=DashboardFinanceSummary.model_validate(data))


@router.get("/cashflow", response_model=ResponseModel[list[CashflowItem]])
def cashflow(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_DASHBOARD_VIEW)),
) -> ResponseModel[list[CashflowItem]]:
    rows = finance_service.dashboard_cashflow(db)
    rows = [mask_finance_dict(r, current_user) for r in rows]
    return ResponseModel(data=[CashflowItem.model_validate(r) for r in rows])


@router.get("/cost-breakdown", response_model=ResponseModel[list[CostBreakdownItem]])
def cost_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_DASHBOARD_VIEW)),
) -> ResponseModel[list[CostBreakdownItem]]:
    rows = finance_service.dashboard_cost_breakdown(db)
    rows = [mask_finance_dict(r, current_user) for r in rows]
    return ResponseModel(data=[CostBreakdownItem.model_validate(r) for r in rows])


@router.get("/project-profit-top", response_model=ResponseModel[list[ProjectProfitItem]])
def project_profit_top(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_DASHBOARD_VIEW)),
) -> ResponseModel[list[ProjectProfitItem]]:
    rows = finance_service.dashboard_project_profit_top(db, limit=10)
    rows = [mask_finance_dict(r, current_user) for r in rows]
    return ResponseModel(data=[ProjectProfitItem.model_validate(r) for r in rows])
