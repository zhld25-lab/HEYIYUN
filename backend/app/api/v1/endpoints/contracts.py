from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import (
    PERM_CONTRACT_CREATE,
    PERM_CONTRACT_DELETE,
    PERM_CONTRACT_UPDATE,
    PERM_CONTRACT_VIEW,
)
from app.crud.crud_finance import CRUDFinance
from app.db.session import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.common import PageData, ResponseModel
from app.schemas.contract import ContractCreate, ContractOut, ContractUpdate
from app.services import audit_service, finance_service
from app.services.permission_service import mask_finance_dict

router = APIRouter(prefix="/contracts", tags=["contracts"])
crud = CRUDFinance(Contract, "contract_code")
RESOURCE = "contract"


def serialize(obj: Contract, user: User) -> ContractOut:
    data = mask_finance_dict(ContractOut.model_validate(obj).model_dump(), user)
    return ContractOut.model_validate(data)


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("", response_model=ResponseModel[PageData[ContractOut]])
def list_contracts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    contract_code: str | None = None,
    contract_name: str | None = None,
    contract_type: str | None = None,
    project_id: int | None = None,
    contract_status: str | None = None,
    approval_status: str | None = None,
    archive_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[PageData[ContractOut]]:
    conditions = []
    if contract_code:
        conditions.append(Contract.contract_code.ilike(f"%{contract_code}%"))
    if contract_name:
        conditions.append(Contract.contract_name.ilike(f"%{contract_name}%"))
    if contract_type:
        conditions.append(Contract.contract_type == contract_type)
    if project_id:
        conditions.append(Contract.project_id == project_id)
    if contract_status:
        conditions.append(Contract.contract_status == contract_status)
    if approval_status:
        conditions.append(Contract.approval_status == approval_status)
    if archive_status:
        conditions.append(Contract.archive_status == archive_status)

    items, total = crud.list_filtered(db, skip=(page - 1) * page_size, limit=page_size, conditions=conditions)
    return ResponseModel(
        data=PageData(items=[serialize(i, current_user) for i in items], total=total, page=page, page_size=page_size)
    )


@router.post("", response_model=ResponseModel[ContractOut])
def create_contract(
    payload: ContractCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_CREATE)),
) -> ResponseModel[ContractOut]:
    if crud.get_by_code(db, payload.contract_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="合同编号已存在")
    obj = Contract(**payload.model_dump(), created_by_id=current_user.id, updated_by_id=current_user.id)
    obj = crud.create(db, obj)
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(
        db, user=current_user, action="CREATE", resource_type=RESOURCE, resource_id=obj.id,
        detail={"contract_code": obj.contract_code, "contract_name": obj.contract_name},
        ip_address=_client_ip(request),
    )
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="合同创建成功")


@router.get("/{contract_id}", response_model=ResponseModel[ContractOut])
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[ContractOut]:
    obj = crud.get(db, contract_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="合同不存在")
    return ResponseModel(data=serialize(obj, current_user))


@router.put("/{contract_id}", response_model=ResponseModel[ContractOut])
def update_contract(
    contract_id: int,
    payload: ContractUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_UPDATE)),
) -> ResponseModel[ContractOut]:
    obj = crud.get(db, contract_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="合同不存在")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_by_id = current_user.id
    db.commit()
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(
        db, user=current_user, action="UPDATE", resource_type=RESOURCE, resource_id=obj.id,
        detail=payload.model_dump(exclude_unset=True), ip_address=_client_ip(request),
    )
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="合同更新成功")


@router.delete("/{contract_id}", response_model=ResponseModel[None])
def delete_contract(
    contract_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_DELETE)),
) -> ResponseModel[None]:
    obj = crud.get(db, contract_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="合同不存在")
    project_id, code = obj.project_id, obj.contract_code
    crud.soft_delete(db, obj)
    finance_service.recalculate(db, project_id)
    audit_service.record(
        db, user=current_user, action="DELETE", resource_type=RESOURCE, resource_id=contract_id,
        detail={"contract_code": code}, ip_address=_client_ip(request),
    )
    return ResponseModel(message="合同删除成功")
