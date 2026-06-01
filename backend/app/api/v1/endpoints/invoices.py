from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.core.permissions import PERM_CONTRACT_VIEW, PERM_FINANCE_DELETE, PERM_FINANCE_EDIT
from app.crud.crud_finance import CRUDFinance
from app.db.session import get_db
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.common import PageData, ResponseModel
from app.schemas.invoice import InvoiceCreate, InvoiceOut, InvoiceUpdate
from app.services import audit_service, finance_service
from app.services.permission_service import mask_finance_dict

router = APIRouter(prefix="/invoices", tags=["invoices"])
crud = CRUDFinance(Invoice, "invoice_code")
RESOURCE = "invoice"


def serialize(obj: Invoice, user: User) -> InvoiceOut:
    return InvoiceOut.model_validate(mask_finance_dict(InvoiceOut.model_validate(obj).model_dump(), user))


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("", response_model=ResponseModel[PageData[InvoiceOut]])
def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    invoice_code: str | None = None,
    invoice_direction: str | None = None,
    project_id: int | None = None,
    contract_id: int | None = None,
    certification_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[PageData[InvoiceOut]]:
    conditions = []
    if invoice_code:
        conditions.append(Invoice.invoice_code.ilike(f"%{invoice_code}%"))
    if invoice_direction:
        conditions.append(Invoice.invoice_direction == invoice_direction)
    if project_id:
        conditions.append(Invoice.project_id == project_id)
    if contract_id:
        conditions.append(Invoice.contract_id == contract_id)
    if certification_status:
        conditions.append(Invoice.certification_status == certification_status)

    items, total = crud.list_filtered(db, skip=(page - 1) * page_size, limit=page_size, conditions=conditions)
    return ResponseModel(
        data=PageData(items=[serialize(i, current_user) for i in items], total=total, page=page, page_size=page_size)
    )


@router.post("", response_model=ResponseModel[InvoiceOut])
def create_invoice(
    payload: InvoiceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_EDIT)),
) -> ResponseModel[InvoiceOut]:
    if crud.get_by_code(db, payload.invoice_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="发票编号已存在")
    obj = Invoice(**payload.model_dump(), created_by_id=current_user.id, updated_by_id=current_user.id)
    obj = crud.create(db, obj)
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(db, user=current_user, action="CREATE", resource_type=RESOURCE, resource_id=obj.id,
                         detail={"invoice_code": obj.invoice_code}, ip_address=_ip(request))
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="发票记录创建成功")


@router.get("/{invoice_id}", response_model=ResponseModel[InvoiceOut])
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_CONTRACT_VIEW)),
) -> ResponseModel[InvoiceOut]:
    obj = crud.get(db, invoice_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="发票记录不存在")
    return ResponseModel(data=serialize(obj, current_user))


@router.put("/{invoice_id}", response_model=ResponseModel[InvoiceOut])
def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_EDIT)),
) -> ResponseModel[InvoiceOut]:
    obj = crud.get(db, invoice_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="发票记录不存在")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_by_id = current_user.id
    db.commit()
    finance_service.recalculate(db, obj.project_id)
    audit_service.record(db, user=current_user, action="UPDATE", resource_type=RESOURCE, resource_id=obj.id,
                         detail=payload.model_dump(exclude_unset=True), ip_address=_ip(request))
    db.refresh(obj)
    return ResponseModel(data=serialize(obj, current_user), message="发票记录更新成功")


@router.delete("/{invoice_id}", response_model=ResponseModel[None])
def delete_invoice(
    invoice_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_FINANCE_DELETE)),
) -> ResponseModel[None]:
    obj = crud.get(db, invoice_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="发票记录不存在")
    project_id, code = obj.project_id, obj.invoice_code
    crud.soft_delete(db, obj)
    finance_service.recalculate(db, project_id)
    audit_service.record(db, user=current_user, action="DELETE", resource_type=RESOURCE, resource_id=invoice_id,
                         detail={"invoice_code": code}, ip_address=_ip(request))
    return ResponseModel(message="发票记录删除成功")
