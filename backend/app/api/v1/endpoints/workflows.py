from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission
from app.core.permissions import PERM_WORKFLOW_APPROVE, PERM_WORKFLOW_CREATE, PERM_WORKFLOW_VIEW
from app.db.session import get_db
from app.models.user import User
from app.models.workflow import Workflow, WorkflowAction, WorkflowStep
from app.services import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class WorkflowCreate(BaseModel):
    business_type: str
    business_id: int
    project_id: int | None = None
    title: str
    workflow_type: str
    remarks: str | None = None


class WorkflowActionRequest(BaseModel):
    comment: str | None = None


class TransferRequest(BaseModel):
    to_user_id: int
    comment: str | None = None


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _step_dict(s: WorkflowStep) -> dict:
    return {
        "id": s.id,
        "step_order": s.step_order,
        "step_name": s.step_name,
        "approver_role": s.approver_role,
        "approver_id": s.approver_id,
        "approver_name": s.approver_name,
        "status": s.status,
        "deadline_days": s.deadline_days,
        "due_at": s.due_at.isoformat() if s.due_at else None,
        "acted_at": s.acted_at.isoformat() if s.acted_at else None,
        "comment": s.comment,
    }


def _action_dict(a: WorkflowAction) -> dict:
    return {
        "id": a.id,
        "step_id": a.step_id,
        "actor_id": a.actor_id,
        "actor_name": a.actor_name,
        "action": a.action,
        "comment": a.comment,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _wf_dict(wf: Workflow, include_steps: bool = False) -> dict:
    d: dict = {
        "id": wf.id,
        "business_type": wf.business_type,
        "business_id": wf.business_id,
        "project_id": wf.project_id,
        "title": wf.title,
        "workflow_type": wf.workflow_type,
        "status": wf.status,
        "current_step": wf.current_step,
        "total_steps": wf.total_steps,
        "initiator_id": wf.initiator_id,
        "initiator_name": wf.initiator_name,
        "submitted_at": wf.submitted_at.isoformat() if wf.submitted_at else None,
        "completed_at": wf.completed_at.isoformat() if wf.completed_at else None,
        "remarks": wf.remarks,
        "created_at": wf.created_at.isoformat() if wf.created_at else None,
        "updated_at": wf.updated_at.isoformat() if wf.updated_at else None,
    }
    if include_steps:
        d["steps"] = [_step_dict(s) for s in wf.steps]
        d["actions"] = [_action_dict(a) for a in wf.actions]
    return d


def _ok(data: Any) -> dict:
    return {"code": 0, "message": "success", "data": data}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("")
def list_workflows(
    status: str | None = Query(None),
    business_type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_VIEW)),
):
    wfs = workflow_service.get_all_workflows(db, status=status, business_type=business_type)
    return _ok([_wf_dict(w) for w in wfs])


@router.get("/my-pending")
def my_pending(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_VIEW)),
):
    wfs = workflow_service.get_my_pending_workflows(db, current_user)
    return _ok([_wf_dict(w) for w in wfs])


@router.get("/my-done")
def my_done(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_VIEW)),
):
    wfs = workflow_service.get_my_done_workflows(db, current_user)
    return _ok([_wf_dict(w) for w in wfs])


@router.get("/my-initiated")
def my_initiated(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_VIEW)),
):
    wfs = workflow_service.get_my_initiated_workflows(db, current_user)
    return _ok([_wf_dict(w) for w in wfs])


@router.get("/business/{business_type}/{business_id}")
def by_business(
    business_type: str,
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_VIEW)),
):
    wfs = workflow_service.get_workflows_by_business(db, business_type, business_id)
    return _ok([_wf_dict(w, include_steps=True) for w in wfs])


@router.get("/overdue")
def overdue_steps(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_VIEW)),
):
    steps = workflow_service.detect_overdue_workflows(db)
    return _ok([_step_dict(s) for s in steps])


@router.post("")
def create_workflow(
    body: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_CREATE)),
):
    wf = workflow_service.create_workflow(
        db,
        business_type=body.business_type,
        business_id=body.business_id,
        title=body.title,
        workflow_type=body.workflow_type,
        initiator=current_user,
        project_id=body.project_id,
        remarks=body.remarks,
    )
    db.commit()
    db.refresh(wf)
    return _ok(_wf_dict(wf, include_steps=True))


@router.get("/{workflow_id}")
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_VIEW)),
):
    wf = db.get(Workflow, workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="审批流不存在")
    return _ok(_wf_dict(wf, include_steps=True))


@router.post("/{workflow_id}/submit")
def submit(
    workflow_id: int,
    body: WorkflowActionRequest = WorkflowActionRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_CREATE)),
):
    try:
        wf = workflow_service.submit_workflow(db, workflow_id, current_user, body.comment)
        db.commit()
        db.refresh(wf)
        return _ok(_wf_dict(wf))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/approve")
def approve(
    workflow_id: int,
    body: WorkflowActionRequest = WorkflowActionRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_APPROVE)),
):
    try:
        wf = workflow_service.approve_workflow(db, workflow_id, current_user, body.comment)
        db.commit()
        db.refresh(wf)
        return _ok(_wf_dict(wf))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/reject")
def reject(
    workflow_id: int,
    body: WorkflowActionRequest = WorkflowActionRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_APPROVE)),
):
    try:
        wf = workflow_service.reject_workflow(db, workflow_id, current_user, body.comment)
        db.commit()
        db.refresh(wf)
        return _ok(_wf_dict(wf))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/withdraw")
def withdraw(
    workflow_id: int,
    body: WorkflowActionRequest = WorkflowActionRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_CREATE)),
):
    try:
        wf = workflow_service.withdraw_workflow(db, workflow_id, current_user, body.comment)
        db.commit()
        db.refresh(wf)
        return _ok(_wf_dict(wf))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/urge")
def urge(
    workflow_id: int,
    body: WorkflowActionRequest = WorkflowActionRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_VIEW)),
):
    try:
        wf = workflow_service.urge_workflow(db, workflow_id, current_user, body.comment)
        db.commit()
        return _ok(_wf_dict(wf))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/transfer")
def transfer(
    workflow_id: int,
    body: TransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_WORKFLOW_APPROVE)),
):
    try:
        wf = workflow_service.transfer_workflow(db, workflow_id, current_user, body.to_user_id, body.comment)
        db.commit()
        return _ok(_wf_dict(wf))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
