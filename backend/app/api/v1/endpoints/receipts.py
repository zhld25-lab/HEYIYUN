from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import PERM_CONTRACT_VIEW, PERM_FINANCE_DELETE, PERM_FINANCE_EDIT
from app.crud.crud_finance import CRUDFinance
from app.db.session import get_db
from app.models.receipt import Receipt
from app.models.user import User
from app.schemas.common import PageData, ResponseModel
from app.schemas.receipt import ReceiptCreate, ReceiptOut, ReceiptUpdate
from app.services import audit_service, finance_service
from app.services.permission_service import mask_finance_dict

router = APIRouter(prefix="/receipts", tags=["receipts"])
crud = CRUDFinance(Receipt, "receipt_code")
RESOURCE = "receipt"


def serialize(obj: Receipt, user: User) -> ReceiptOut:
    return ReceiptOut.model_validate(mask_finance_dict(ReceiptOut.model_validate(obj).model_dump(), user))


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("", response_model=ResponseModel[PageData[ReceiptOut]])
def list_receipts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    receipt_code: str | None = None,
    project_id: int | None = None,
    contract_id: int | None = None,
    is_overdue: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[PageData[ReceiptOut]]:
    conditions = []
    if receipt_code:
        conditions.append(Receipt.receipt_code.ilike(f"%{receipt_code}%"))
    if project_id:
        conditions.append(Receipt.project_id == project_id)
    if contract_id:
        conditions.append(Receipt.contract_id == contract_id)
    if is_overdue is not None:
        conditions.append(Receipt.is_overdue.is_(is_overdue))

    items, total = crud.list_filtered(db, skip=(page - 1) * page_size, limit=page_size, conditions=conditions)
    return ResponseModel(
        data=PageData(items=[serialize(i, current_user) for i in items], total=total, page=page, page_size=page_size)
    )


@router.post("", response_model=ResponseModel[ReceiptOut])
def create_receipt(
    payload: ReceiptCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_EDIT)),
) -> ResponseModel[ReceiptOut]:
    if crud.get_by_code(db, payload.receipt_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="回款编号已存在")
    obj = Receipt(**payload.model_dump(), created_by_id=current_user.id, updated_by_id=current_user.id)
    obj = crud.create(db, obj)
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(db, user=current_user, action="CREATE", resource_type=RESOURCE, resource_id=obj.id,
                         detail={"receipt_code": obj.receipt_code}, ip_address=_ip(request))
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="回款记录创建成功")


@router.get("/{receipt_id}", response_model=ResponseModel[ReceiptOut])
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[ReceiptOut]:
    obj = crud.get(db, receipt_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回款记录不存在")
    return ResponseModel(data=serialize(obj, current_user))


@router.put("/{receipt_id}", response_model=ResponseModel[ReceiptOut])
def update_receipt(
    receipt_id: int,
    payload: ReceiptUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_EDIT)),
) -> ResponseModel[ReceiptOut]:
    obj = crud.get(db, receipt_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回款记录不存在")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_by_id = current_user.id
    db.commit()
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(db, user=current_user, action="UPDATE", resource_type=RESOURCE, resource_id=obj.id,
                         detail=payload.model_dump(exclude_unset=True), ip_address=_ip(request))
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="回款记录更新成功")


@router.delete("/{receipt_id}", response_model=ResponseModel[None])
def delete_receipt(
    receipt_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_DELETE)),
) -> ResponseModel[None]:
    obj = crud.get(db, receipt_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回款记录不存在")
    project_id, code = obj.project_id, obj.receipt_code
    crud.soft_delete(db, obj)
    finance_service.recalculate(db, project_id)
    audit_service.record(db, user=current_user, action="DELETE", resource_type=RESOURCE, resource_id=receipt_id,
                         detail={"receipt_code": code}, ip_address=_ip(request))
    return ResponseModel(message="回款记录删除成功")
