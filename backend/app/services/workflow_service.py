from __future__ import annotations

"""Workflow / approval engine service.

Supports 8 workflow types:
  项目立项审批 / 合同审批 / 付款审批 / 成本审批 / 发票审批 / 结算审批 / 采购审批 / 报销审批

Default step chains are defined per type. Actual approver assignment is done
by role-code — the front-end or caller can later assign specific user IDs.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workflow import Workflow, WorkflowAction, WorkflowStep
from app.models.user import User

# ---------------------------------------------------------------------------
# Default step definitions  {workflow_type: [(step_order, name, role, days)]}
# ---------------------------------------------------------------------------
DEFAULT_STEPS: dict[str, list[tuple[int, str, str, int]]] = {
    "项目立项审批": [
        (1, "项目经理审核", "project_manager", 3),
        (2, "财务负责人审核", "finance", 3),
        (3, "总经理审批", "general_manager", 5),
    ],
    "合同审批": [
        (1, "项目经理审核", "project_manager", 3),
        (2, "财务负责人审核", "finance", 3),
        (3, "总经理审批", "general_manager", 5),
    ],
    "付款审批": [
        (1, "项目经理审核", "project_manager", 2),
        (2, "财务负责人审批", "finance", 3),
        (3, "总经理审批", "general_manager", 3),
    ],
    "成本审批": [
        (1, "项目经理审核", "project_manager", 2),
        (2, "财务负责人审批", "finance", 3),
    ],
    "发票审批": [
        (1, "财务负责人审核", "finance", 3),
        (2, "总经理审批", "general_manager", 3),
    ],
    "结算审批": [
        (1, "项目经理审核", "project_manager", 5),
        (2, "财务负责人审核", "finance", 5),
        (3, "总经理审批", "general_manager", 7),
    ],
    "采购审批": [
        (1, "项目经理审核", "project_manager", 2),
        (2, "财务负责人审批", "finance", 3),
    ],
    "报销审批": [
        (1, "项目经理审核", "project_manager", 2),
        (2, "财务负责人审批", "finance", 3),
    ],
}

BUSINESS_TYPE_WORKFLOW_MAP: dict[str, str] = {
    "project": "项目立项审批",
    "contract": "合同审批",
    "payment": "付款审批",
    "cost": "成本审批",
    "invoice": "发票审批",
}

_NOW = lambda: datetime.now(timezone.utc)  # noqa: E731


def build_default_workflow_steps(
    db: Session,
    workflow: Workflow,
    workflow_type: str,
) -> None:
    """Attach default steps to a Workflow instance based on its type."""
    steps_def = DEFAULT_STEPS.get(workflow_type, [])
    now = _NOW()
    for order, name, role, days in steps_def:
        due = now + timedelta(days=days)
        step = WorkflowStep(
            workflow_id=workflow.id,
            step_order=order,
            step_name=name,
            approver_role=role,
            status="pending" if order == 1 else "waiting",
            deadline_days=days,
            due_at=due,
        )
        db.add(step)
    workflow.total_steps = len(steps_def)
    workflow.current_step = 1 if steps_def else 0


def create_workflow(
    db: Session,
    business_type: str,
    business_id: int,
    title: str,
    workflow_type: str,
    initiator: User,
    project_id: int | None = None,
    remarks: str | None = None,
) -> Workflow:
    """Create a workflow in draft status with default steps."""
    wf = Workflow(
        business_type=business_type,
        business_id=business_id,
        project_id=project_id,
        title=title,
        workflow_type=workflow_type,
        status="draft",
        initiator_id=initiator.id,
        initiator_name=initiator.full_name,
        remarks=remarks,
    )
    db.add(wf)
    db.flush()  # get wf.id
    build_default_workflow_steps(db, wf, workflow_type)
    db.flush()
    return wf


def submit_workflow(db: Session, workflow_id: int, actor: User, comment: str | None = None) -> Workflow:
    """Submit a draft workflow for approval."""
    wf = _get_or_404(db, workflow_id)
    if wf.status != "draft":
        raise ValueError(f"流程状态为 {wf.status}，无法提交")
    wf.status = "pending"
    wf.submitted_at = _NOW()
    _record_action(db, wf, actor, "submit", comment)
    _update_business_approval_status(db, wf.business_type, wf.business_id, "审批中")
    return wf


def approve_workflow(db: Session, workflow_id: int, actor: User, comment: str | None = None) -> Workflow:
    """Approve current step. Auto-advance or complete if last step."""
    wf = _get_or_404(db, workflow_id)
    if wf.status != "pending":
        raise ValueError(f"流程状态为 {wf.status}，无法审批")
    step = _current_step(wf)
    if step:
        step.status = "approved"
        step.acted_at = _NOW()
        step.comment = comment
    _record_action(db, wf, actor, "approve", comment)

    # Check if there are more steps
    next_step = _next_step(wf)
    if next_step:
        next_step.status = "pending"
        wf.current_step += 1
    else:
        wf.status = "approved"
        wf.completed_at = _NOW()
        _update_business_approval_status(db, wf.business_type, wf.business_id, "已批准")
    return wf


def reject_workflow(db: Session, workflow_id: int, actor: User, comment: str | None = None) -> Workflow:
    wf = _get_or_404(db, workflow_id)
    if wf.status != "pending":
        raise ValueError(f"流程状态为 {wf.status}，无法驳回")
    step = _current_step(wf)
    if step:
        step.status = "rejected"
        step.acted_at = _NOW()
        step.comment = comment
    wf.status = "rejected"
    wf.completed_at = _NOW()
    _record_action(db, wf, actor, "reject", comment)
    _update_business_approval_status(db, wf.business_type, wf.business_id, "已驳回")
    return wf


def withdraw_workflow(db: Session, workflow_id: int, actor: User, comment: str | None = None) -> Workflow:
    wf = _get_or_404(db, workflow_id)
    if wf.status not in ("draft", "pending"):
        raise ValueError(f"流程状态为 {wf.status}，无法撤回")
    wf.status = "withdrawn"
    wf.completed_at = _NOW()
    _record_action(db, wf, actor, "withdraw", comment)
    _update_business_approval_status(db, wf.business_type, wf.business_id, "待提交")
    return wf


def urge_workflow(db: Session, workflow_id: int, actor: User, comment: str | None = None) -> Workflow:
    wf = _get_or_404(db, workflow_id)
    if wf.status != "pending":
        raise ValueError(f"流程状态为 {wf.status}，无法催办")
    _record_action(db, wf, actor, "urge", comment or "催办提醒")
    return wf


def transfer_workflow(
    db: Session, workflow_id: int, actor: User, to_user_id: int, comment: str | None = None
) -> Workflow:
    """Transfer current step approval to another user."""
    wf = _get_or_404(db, workflow_id)
    if wf.status != "pending":
        raise ValueError(f"流程状态为 {wf.status}，无法转办")
    step = _current_step(wf)
    if step:
        target = db.get(User, to_user_id)
        if target:
            step.approver_id = target.id
            step.approver_name = target.full_name
    _record_action(db, wf, actor, "transfer", comment or f"转办给用户 {to_user_id}")
    return wf


def get_my_pending_workflows(db: Session, user: User) -> list[Workflow]:
    """Return workflows where the current step is assigned to this user's role."""
    role_code = user.role_code
    stmt = (
        select(Workflow)
        .join(WorkflowStep, WorkflowStep.workflow_id == Workflow.id)
        .where(
            Workflow.status == "pending",
            WorkflowStep.step_order == Workflow.current_step,
            WorkflowStep.approver_role == role_code,
        )
    )
    return list(db.scalars(stmt).all())


def get_my_done_workflows(db: Session, user: User) -> list[Workflow]:
    stmt = (
        select(Workflow)
        .join(WorkflowAction, WorkflowAction.workflow_id == Workflow.id)
        .where(
            WorkflowAction.actor_id == user.id,
            WorkflowAction.action.in_(["approve", "reject"]),
        )
        .distinct()
    )
    return list(db.scalars(stmt).all())


def get_my_initiated_workflows(db: Session, user: User) -> list[Workflow]:
    stmt = select(Workflow).where(Workflow.initiator_id == user.id).order_by(Workflow.created_at.desc())
    return list(db.scalars(stmt).all())


def get_all_workflows(db: Session, status: str | None = None, business_type: str | None = None) -> list[Workflow]:
    stmt = select(Workflow).order_by(Workflow.created_at.desc())
    if status:
        stmt = stmt.where(Workflow.status == status)
    if business_type:
        stmt = stmt.where(Workflow.business_type == business_type)
    return list(db.scalars(stmt).all())


def get_workflows_by_business(db: Session, business_type: str, business_id: int) -> list[Workflow]:
    stmt = (
        select(Workflow)
        .where(Workflow.business_type == business_type, Workflow.business_id == business_id)
        .order_by(Workflow.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_workflows_by_project(db: Session, project_id: int) -> list[Workflow]:
    stmt = select(Workflow).where(Workflow.project_id == project_id).order_by(Workflow.created_at.desc())
    return list(db.scalars(stmt).all())


def detect_overdue_workflows(db: Session) -> list[WorkflowStep]:
    now = _NOW()
    stmt = (
        select(WorkflowStep)
        .join(Workflow, Workflow.id == WorkflowStep.workflow_id)
        .where(
            Workflow.status == "pending",
            WorkflowStep.status == "pending",
            WorkflowStep.due_at < now,
        )
    )
    return list(db.scalars(stmt).all())


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_or_404(db: Session, workflow_id: int) -> Workflow:
    wf = db.get(Workflow, workflow_id)
    if wf is None:
        raise ValueError(f"审批流 {workflow_id} 不存在")
    return wf


def _current_step(wf: Workflow) -> WorkflowStep | None:
    for step in wf.steps:
        if step.step_order == wf.current_step:
            return step
    return None


def _next_step(wf: Workflow) -> WorkflowStep | None:
    next_order = wf.current_step + 1
    for step in wf.steps:
        if step.step_order == next_order:
            return step
    return None


def _record_action(
    db: Session, wf: Workflow, actor: User, action: str, comment: str | None
) -> WorkflowAction:
    step = _current_step(wf)
    act = WorkflowAction(
        workflow_id=wf.id,
        step_id=step.id if step else None,
        actor_id=actor.id,
        actor_name=actor.full_name,
        action=action,
        comment=comment,
    )
    db.add(act)
    return act


def _update_business_approval_status(
    db: Session, business_type: str, business_id: int, new_status: str
) -> None:
    """Update the approval_status field on the related business entity."""
    model_map: dict[str, Any] = {}
    try:
        from app.models.contract import Contract
        from app.models.cost_record import CostRecord
        from app.models.payment import Payment
        from app.models.invoice import Invoice
        from app.models.project import Project

        model_map = {
            "project": Project,
            "contract": Contract,
            "cost": CostRecord,
            "payment": Payment,
            "invoice": Invoice,
        }
    except ImportError:
        return

    model_cls = model_map.get(business_type)
    if model_cls is None:
        return
    obj = db.get(model_cls, business_id)
    if obj and hasattr(obj, "approval_status"):
        obj.approval_status = new_status
