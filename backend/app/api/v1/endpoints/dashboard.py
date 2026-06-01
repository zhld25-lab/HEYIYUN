from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import PERM_DASHBOARD_VIEW
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.dashboard import DashboardSummary, ProjectStatusItem
from app.services import dashboard_service
from app.services.permission_service import mask_dashboard_dict

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
