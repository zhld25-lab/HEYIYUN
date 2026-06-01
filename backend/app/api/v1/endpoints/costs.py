from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import PERM_CONTRACT_VIEW, PERM_FINANCE_DELETE, PERM_FINANCE_EDIT
from app.crud.crud_finance import CRUDFinance
from app.db.session import get_db
from app.models.cost_record import CostRecord
from app.models.user import User
from app.schemas.common import PageData, ResponseModel
from app.schemas.cost import CostCreate, CostOut, CostUpdate
from app.services import audit_service, finance_service
from app.services.permission_service import mask_finance_dict

router = APIRouter(prefix="/costs", tags=["costs"])
crud = CRUDFinance(CostRecord, "cost_code")
RESOURCE = "cost"


def serialize(obj: CostRecord, user: User) -> CostOut:
    return CostOut.model_validate(mask_finance_dict(CostOut.model_validate(obj).model_dump(), user))


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("", response_model=ResponseModel[PageData[CostOut]])
def list_costs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    cost_code: str | None = None,
    cost_type: str | None = None,
    project_id: int | None = None,
    contract_id: int | None = None,
    payment_status: str | None = None,
    invoice_status: str | None = None,
    approval_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[PageData[CostOut]]:
    conditions = []
    if cost_code:
        conditions.append(CostRecord.cost_code.ilike(f"%{cost_code}%"))
    if cost_type:
        conditions.append(CostRecord.cost_type == cost_type)
    if project_id:
        conditions.append(CostRecord.project_id == project_id)
    if contract_id:
        conditions.append(CostRecord.contract_id == contract_id)
    if payment_status:
        conditions.append(CostRecord.payment_status == payment_status)
    if invoice_status:
        conditions.append(CostRecord.invoice_status == invoice_status)
    if approval_status:
        conditions.append(CostRecord.approval_status == approval_status)

    items, total = crud.list_filtered(db, skip=(page - 1) * page_size, limit=page_size, conditions=conditions)
    return ResponseModel(
        data=PageData(items=[serialize(i, current_user) for i in items], total=total, page=page, page_size=page_size)
    )


@router.post("", response_model=ResponseModel[CostOut])
def create_cost(
    payload: CostCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_EDIT)),
) -> ResponseModel[CostOut]:
    if crud.get_by_code(db, payload.cost_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="成本编号已存在")
    obj = CostRecord(**payload.model_dump(), created_by_id=current_user.id, updated_by_id=current_user.id)
    obj = crud.create(db, obj)
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(db, user=current_user, action="CREATE", resource_type=RESOURCE, resource_id=obj.id,
                         detail={"cost_code": obj.cost_code, "amount": str(obj.amount)}, ip_address=_ip(request))
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="成本记录创建成功")


@router.get("/{cost_id}", response_model=ResponseModel[CostOut])
def get_cost(
    cost_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[CostOut]:
    obj = crud.get(db, cost_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成本记录不存在")
    return ResponseModel(data=serialize(obj, current_user))


@router.put("/{cost_id}", response_model=ResponseModel[CostOut])
def update_cost(
    cost_id: int,
    payload: CostUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_EDIT)),
) -> ResponseModel[CostOut]:
    obj = crud.get(db, cost_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成本记录不存在")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_by_id = current_user.id
    db.commit()
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(db, user=current_user, action="UPDATE", resource_type=RESOURCE, resource_id=obj.id,
                         detail=payload.model_dump(exclude_unset=True), ip_address=_ip(request))
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="成本记录更新成功")


@router.delete("/{cost_id}", response_model=ResponseModel[None])
def delete_cost(
    cost_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_DELETE)),
) -> ResponseModel[None]:
    obj = crud.get(db, cost_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成本记录不存在")
    project_id, code = obj.project_id, obj.cost_code
    crud.soft_delete(db, obj)
    finance_service.recalculate(db, project_id)
    audit_service.record(db, user=current_user, action="DELETE", resource_type=RESOURCE, resource_id=cost_id,
                         detail={"cost_code": code}, ip_address=_ip(request))
    return ResponseModel(message="成本记录删除成功")
