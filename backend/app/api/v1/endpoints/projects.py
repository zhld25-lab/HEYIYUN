from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints import contracts as contracts_ep
from app.api.v1.endpoints import costs as costs_ep
from app.api.v1.endpoints import invoices as invoices_ep
from app.api.v1.endpoints import payments as payments_ep
from app.api.v1.endpoints import receipts as receipts_ep
from app.core.deps import get_current_user, require_permission
from app.core.permissions import (
    PERM_CONTRACT_VIEW,
    PERM_PROJECT_CREATE,
    PERM_PROJECT_DELETE,
    PERM_PROJECT_UPDATE,
    PERM_PROJECT_VIEW,
    PERM_WORKFLOW_CREATE,
    PERM_WORKFLOW_VIEW,
)
from app.crud.crud_finance import CRUDFinance
from app.crud.crud_project import crud_project
from app.db.session import get_db
from app.models.contract import Contract
from app.models.cost_record import CostRecord
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.receipt import Receipt
from app.models.user import User
from app.schemas.common import PageData, ResponseModel
from app.schemas.contract import ContractOut
from app.schemas.cost import CostOut
from app.schemas.finance import ProjectFinanceSummary
from app.schemas.invoice import InvoiceOut
from app.schemas.payment import PaymentOut
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.schemas.receipt import ReceiptOut
from app.services import audit_service, finance_service, project_service, workflow_service
from app.services.permission_service import mask_finance_dict, mask_project_dict
from app.api.v1.endpoints.workflows import _wf_dict

router = APIRouter(prefix="/projects", tags=["projects"])

RESOURCE = "project"


def _serialize(project, user: User) -> ProjectOut:
    data = ProjectOut.model_validate(project).model_dump()
    data = mask_project_dict(data, user)
    return ProjectOut.model_validate(data)


@router.get("", response_model=ResponseModel[PageData[ProjectOut]])
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    project_name: str | None = None,
    project_code: str | None = None,
    project_type: str | None = None,
    voltage_level: str | None = None,
    project_status: str | None = None,
    risk_level: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_VIEW)),
) -> ResponseModel[PageData[ProjectOut]]:
    items, total = crud_project.list_filtered(
        db,
        skip=(page - 1) * page_size,
        limit=page_size,
        project_name=project_name,
        project_code=project_code,
        project_type=project_type,
        voltage_level=voltage_level,
        project_status=project_status,
        risk_level=risk_level,
    )
    data = PageData(
        items=[_serialize(p, current_user) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ResponseModel(data=data)


@router.post("", response_model=ResponseModel[ProjectOut])
def create_project(
    payload: ProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_CREATE)),
) -> ResponseModel[ProjectOut]:
    if crud_project.get_by_code(db, payload.project_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="项目编号已存在")
    project = project_service.create_project_obj(payload)
    project = crud_project.create(db, project)
    audit_service.record(
        db,
        user=current_user,
        action="CREATE",
        resource_type=RESOURCE,
        resource_id=project.id,
        detail={"project_code": project.project_code, "project_name": project.project_name},
        ip_address=request.client.host if request.client else None,
    )
    return ResponseModel(data=_serialize(project, current_user), message="项目创建成功")


@router.get("/{project_id}", response_model=ResponseModel[ProjectOut])
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_VIEW)),
) -> ResponseModel[ProjectOut]:
    project = crud_project.get(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return ResponseModel(data=_serialize(project, current_user))


@router.get("/{project_id}/overview", response_model=ResponseModel[ProjectOut])
def project_overview(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_VIEW)),
) -> ResponseModel[ProjectOut]:
    # Phase 2: overview returns the masked base project. Related modules
    # (contracts, costs, risks ...) are placeholders for later phases.
    project = crud_project.get(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return ResponseModel(data=_serialize(project, current_user))


@router.put("/{project_id}", response_model=ResponseModel[ProjectOut])
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_UPDATE)),
) -> ResponseModel[ProjectOut]:
    project = crud_project.get(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    project_service.apply_update(project, payload)
    db.commit()
    db.refresh(project)
    audit_service.record(
        db,
        user=current_user,
        action="UPDATE",
        resource_type=RESOURCE,
        resource_id=project.id,
        detail=payload.model_dump(exclude_unset=True),
        ip_address=request.client.host if request.client else None,
    )
    return ResponseModel(data=_serialize(project, current_user), message="项目更新成功")


def _project_children(db, model, project_id: int):
    crud = CRUDFinance(model, "id")
    items, _ = crud.list_filtered(db, limit=500, conditions=[model.project_id == project_id])
    return items


@router.get("/{project_id}/contracts", response_model=ResponseModel[list[ContractOut]])
def project_contracts(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[list[ContractOut]]:
    items = _project_children(db, Contract, project_id)
    return ResponseModel(data=[contracts_ep.serialize(i, current_user) for i in items])


@router.get("/{project_id}/costs", response_model=ResponseModel[list[CostOut]])
def project_costs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[list[CostOut]]:
    items = _project_children(db, CostRecord, project_id)
    return ResponseModel(data=[costs_ep.serialize(i, current_user) for i in items])


@router.get("/{project_id}/payments", response_model=ResponseModel[list[PaymentOut]])
def project_payments(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[list[PaymentOut]]:
    items = _project_children(db, Payment, project_id)
    return ResponseModel(data=[payments_ep.serialize(i, current_user) for i in items])


@router.get("/{project_id}/receipts", response_model=ResponseModel[list[ReceiptOut]])
def project_receipts(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[list[ReceiptOut]]:
    items = _project_children(db, Receipt, project_id)
    return ResponseModel(data=[receipts_ep.serialize(i, current_user) for i in items])


@router.get("/{project_id}/invoices", response_model=ResponseModel[list[InvoiceOut]])
def project_invoices(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[list[InvoiceOut]]:
    items = _project_children(db, Invoice, project_id)
    return ResponseModel(data=[invoices_ep.serialize(i, current_user) for i in items])


@router.get("/{project_id}/finance-summary", response_model=ResponseModel[ProjectFinanceSummary])
def project_finance_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_VIEW)),
) -> ResponseModel[ProjectFinanceSummary]:
    summary = finance_service.get_project_finance_summary(db, project_id)
    if summary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    summary = mask_finance_dict(summary, current_user)
    return ResponseModel(data=ProjectFinanceSummary.model_validate(summary))


@router.get("/{project_id}/workflows")
def project_workflows(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_VIEW)),
):
    wfs = workflow_service.get_workflows_by_project(db, project_id)
    return {"code": 0, "message": "success", "data": [_wf_dict(w, include_steps=True) for w in wfs]}


@router.post("/{project_id}/submit-approval")
def project_submit_approval(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_CREATE)),
):
    project = crud_project.get(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    wf = workflow_service.create_workflow(
        db,
        business_type="project",
        business_id=project_id,
        title=f"项目立项审批 - {project.project_name}",
        workflow_type="项目立项审批",
        initiator=current_user,
        project_id=project_id,
    )
    workflow_service.submit_workflow(db, wf.id, current_user)
    db.commit()
    db.refresh(wf)
    return {"code": 0, "message": "success", "data": _wf_dict(wf)}


@router.delete("/{project_id}", response_model=ResponseModel[None])
def delete_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_DELETE)),
) -> ResponseModel[None]:
    project = crud_project.get(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    code = project.project_code
    crud_project.remove(db, project)
    audit_service.record(
        db,
        user=current_user,
        action="DELETE",
        resource_type=RESOURCE,
        resource_id=project_id,
        detail={"project_code": code},
        ip_address=request.client.host if request.client else None,
    )
    return ResponseModel(message="项目删除成功")
