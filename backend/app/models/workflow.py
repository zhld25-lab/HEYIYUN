from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Workflow(Base, TimestampMixin):
    """审批流主表：一条业务记录对应一个或多个流程实例。"""

    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # 关联业务
    business_type: Mapped[str] = mapped_column(String(64), index=True)  # project/contract/payment/cost/invoice
    business_id: Mapped[int] = mapped_column(Integer, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True, default=None)
    title: Mapped[str] = mapped_column(String(256))
    workflow_type: Mapped[str] = mapped_column(String(64))  # 项目立项审批/合同审批/...
    status: Mapped[str] = mapped_column(String(32), default="draft")
    # draft / pending / approved / rejected / withdrawn
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, default=1)
    initiator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), default=None)
    initiator_name: Mapped[str | None] = mapped_column(String(64), default=None)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    remarks: Mapped[str | None] = mapped_column(Text, default=None)

    steps: Mapped[list[WorkflowStep]] = relationship(
        "WorkflowStep", back_populates="workflow", order_by="WorkflowStep.step_order", cascade="all, delete-orphan"
    )
    actions: Mapped[list[WorkflowAction]] = relationship(
        "WorkflowAction", back_populates="workflow", order_by="WorkflowAction.created_at", cascade="all, delete-orphan"
    )


class WorkflowStep(Base):
    """流程步骤定义（每个流程有若干步骤，按 step_order 顺序）。"""

    __tablename__ = "workflow_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), index=True)
    step_order: Mapped[int] = mapped_column(Integer)
    step_name: Mapped[str] = mapped_column(String(64))
    approver_role: Mapped[str | None] = mapped_column(String(64), default=None)  # role code
    approver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), default=None)
    approver_name: Mapped[str | None] = mapped_column(String(64), default=None)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    # pending / approved / rejected / skipped / transferred
    deadline_days: Mapped[int | None] = mapped_column(Integer, default=None)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    acted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    comment: Mapped[str | None] = mapped_column(Text, default=None)

    workflow: Mapped[Workflow] = relationship("Workflow", back_populates="steps")


class WorkflowAction(Base):
    """审批动作记录（流水账，不可修改）。"""

    __tablename__ = "workflow_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), index=True)
    step_id: Mapped[int | None] = mapped_column(ForeignKey("workflow_steps.id"), default=None)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), default=None)
    actor_name: Mapped[str | None] = mapped_column(String(64), default=None)
    action: Mapped[str] = mapped_column(String(32))  # submit/approve/reject/withdraw/urge/transfer
    comment: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    workflow: Mapped[Workflow] = relationship("Workflow", back_populates="actions")
