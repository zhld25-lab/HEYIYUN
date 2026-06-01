from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import PERM_CONTRACT_VIEW, PERM_FINANCE_DELETE, PERM_FINANCE_EDIT
from app.crud.crud_finance import CRUDFinance
from app.db.session import get_db
from app.models.payment import Payment
from app.models.user import User
from app.schemas.common import PageData, ResponseModel
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentUpdate
from app.services import audit_service, finance_service
from app.services.permission_service import mask_finance_dict

router = APIRouter(prefix="/payments", tags=["payments"])
crud = CRUDFinance(Payment, "payment_code")
RESOURCE = "payment"


def serialize(obj: Payment, user: User) -> PaymentOut:
    return PaymentOut.model_validate(mask_finance_dict(PaymentOut.model_validate(obj).model_dump(), user))


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("", response_model=ResponseModel[PageData[PaymentOut]])
def list_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    payment_code: str | None = None,
    project_id: int | None = None,
    contract_id: int | None = None,
    payment_status: str | None = None,
    approval_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[PageData[PaymentOut]]:
    conditions = []
    if payment_code:
        conditions.append(Payment.payment_code.ilike(f"%{payment_code}%"))
    if project_id:
        conditions.append(Payment.project_id == project_id)
    if contract_id:
        conditions.append(Payment.contract_id == contract_id)
    if payment_status:
        conditions.append(Payment.payment_status == payment_status)
    if approval_status:
        conditions.append(Payment.approval_status == approval_status)

    items, total = crud.list_filtered(db, skip=(page - 1) * page_size, limit=page_size, conditions=conditions)
    return ResponseModel(
        data=PageData(items=[serialize(i, current_user) for i in items], total=total, page=page, page_size=page_size)
    )


@router.post("", response_model=ResponseModel[PaymentOut])
def create_payment(
    payload: PaymentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_EDIT)),
) -> ResponseModel[PaymentOut]:
    if crud.get_by_code(db, payload.payment_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="付款编号已存在")
    obj = Payment(**payload.model_dump(), created_by_id=current_user.id, updated_by_id=current_user.id)
    obj = crud.create(db, obj)
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(db, user=current_user, action="CREATE", resource_type=RESOURCE, resource_id=obj.id,
                         detail={"payment_code": obj.payment_code}, ip_address=_ip(request))
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="付款记录创建成功")


@router.get("/{payment_id}", response_model=ResponseModel[PaymentOut])
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[PaymentOut]:
    obj = crud.get(db, payment_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="付款记录不存在")
    return ResponseModel(data=serialize(obj, current_user))


@router.put("/{payment_id}", response_model=ResponseModel[PaymentOut])
def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_EDIT)),
) -> ResponseModel[PaymentOut]:
    obj = crud.get(db, payment_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="付款记录不存在")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_by_id = current_user.id
    db.commit()
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(db, user=current_user, action="UPDATE", resource_type=RESOURCE, resource_id=obj.id,
                         detail=payload.model_dump(exclude_unset=True), ip_address=_ip(request))
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="付款记录更新成功")


@router.delete("/{payment_id}", response_model=ResponseModel[None])
def delete_payment(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_DELETE)),
) -> ResponseModel[None]:
    obj = crud.get(db, payment_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="付款记录不存在")
    project_id, code = obj.project_id, obj.payment_code
    crud.soft_delete(db, obj)
    finance_service.recalculate(db, project_id)
    audit_service.record(db, user=current_user, action="DELETE", resource_type=RESOURCE, resource_id=payment_id,
                         detail={"payment_code": code}, ip_address=_ip(request))
    return ResponseModel(message="付款记录删除成功")
