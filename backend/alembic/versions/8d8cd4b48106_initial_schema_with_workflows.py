"""initial schema with workflows

Revision ID: 8d8cd4b48106
Revises:
Create Date: 2026-06-01 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8d8cd4b48106"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # departments
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(32), unique=True, nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(32), unique=True, nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # permissions
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(64), unique=True, nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("module", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # role_permissions
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("permission_id", sa.Integer, sa.ForeignKey("permissions.id"), nullable=False),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(64), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(128), nullable=False),
        sa.Column("full_name", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=True),
        sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_username", "users", ["username"])

    # projects
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_code", sa.String(64), unique=True, nullable=False),
        sa.Column("project_name", sa.String(256), nullable=False),
        sa.Column("project_type", sa.String(64), nullable=True),
        sa.Column("voltage_level", sa.String(32), nullable=True),
        sa.Column("project_location", sa.String(256), nullable=True),
        sa.Column("region", sa.String(64), nullable=True),
        sa.Column("project_status", sa.String(32), default="报装中"),
        sa.Column("owner_unit", sa.String(128), nullable=True),
        sa.Column("construction_unit", sa.String(128), nullable=True),
        sa.Column("design_unit", sa.String(128), nullable=True),
        sa.Column("supervision_unit", sa.String(128), nullable=True),
        sa.Column("project_manager_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("planned_start_date", sa.Date, nullable=True),
        sa.Column("planned_end_date", sa.Date, nullable=True),
        sa.Column("actual_start_date", sa.Date, nullable=True),
        sa.Column("actual_end_date", sa.Date, nullable=True),
        sa.Column("contract_amount", sa.Numeric(18, 2), default=0),
        sa.Column("target_cost", sa.Numeric(18, 2), default=0),
        sa.Column("actual_cost", sa.Numeric(18, 2), default=0),
        sa.Column("received_amount", sa.Numeric(18, 2), default=0),
        sa.Column("paid_amount", sa.Numeric(18, 2), default=0),
        sa.Column("receivable_amount", sa.Numeric(18, 2), default=0),
        sa.Column("payable_amount", sa.Numeric(18, 2), default=0),
        sa.Column("profit", sa.Numeric(18, 2), default=0),
        sa.Column("profit_margin", sa.Numeric(8, 6), default=0),
        sa.Column("production_progress", sa.Numeric(5, 4), default=0),
        sa.Column("collection_progress", sa.Numeric(5, 4), default=0),
        sa.Column("cost_ratio", sa.Numeric(5, 4), default=0),
        sa.Column("document_completion_rate", sa.Numeric(5, 4), default=0),
        sa.Column("risk_level", sa.String(8), default="低"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_projects_project_code", "projects", ["project_code"])

    # contracts
    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("created_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("status", sa.String(32), default="active"),
        sa.Column("contract_code", sa.String(64), unique=True, nullable=False),
        sa.Column("contract_name", sa.String(256), nullable=False),
        sa.Column("contract_type", sa.String(32), nullable=True),
        sa.Column("party_a", sa.String(128), nullable=True),
        sa.Column("party_b", sa.String(128), nullable=True),
        sa.Column("contract_amount", sa.Numeric(18, 2), default=0),
        sa.Column("settlement_amount", sa.Numeric(18, 2), default=0),
        sa.Column("invoiced_amount", sa.Numeric(18, 2), default=0),
        sa.Column("received_amount", sa.Numeric(18, 2), default=0),
        sa.Column("paid_amount", sa.Numeric(18, 2), default=0),
        sa.Column("receivable_amount", sa.Numeric(18, 2), default=0),
        sa.Column("payable_amount", sa.Numeric(18, 2), default=0),
        sa.Column("contract_status", sa.String(32), default="执行中"),
        sa.Column("approval_status", sa.String(32), default="待提交"),
        sa.Column("archive_status", sa.String(32), default="未归档"),
        sa.Column("signed_date", sa.Date, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # cost_records
    op.create_table(
        "cost_records",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("created_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("status", sa.String(32), default="active"),
        sa.Column("cost_code", sa.String(64), unique=True, nullable=False),
        sa.Column("cost_type", sa.String(64), nullable=True),
        sa.Column("contract_id", sa.Integer, sa.ForeignKey("contracts.id"), nullable=True),
        sa.Column("supplier_name", sa.String(128), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), default=0),
        sa.Column("occurred_date", sa.Date, nullable=True),
        sa.Column("handler_name", sa.String(64), nullable=True),
        sa.Column("approval_status", sa.String(32), default="待提交"),
        sa.Column("invoice_status", sa.String(32), default="未开票"),
        sa.Column("payment_status", sa.String(32), default="未付款"),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # payments
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("created_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("status", sa.String(32), default="active"),
        sa.Column("payment_code", sa.String(64), unique=True, nullable=False),
        sa.Column("contract_id", sa.Integer, sa.ForeignKey("contracts.id"), nullable=True),
        sa.Column("payee_name", sa.String(128), nullable=True),
        sa.Column("requested_amount", sa.Numeric(18, 2), default=0),
        sa.Column("paid_amount", sa.Numeric(18, 2), default=0),
        sa.Column("payment_date", sa.Date, nullable=True),
        sa.Column("payment_status", sa.String(32), default="待付款"),
        sa.Column("approval_status", sa.String(32), default="待提交"),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # receipts
    op.create_table(
        "receipts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("created_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("status", sa.String(32), default="active"),
        sa.Column("receipt_code", sa.String(64), unique=True, nullable=False),
        sa.Column("contract_id", sa.Integer, sa.ForeignKey("contracts.id"), nullable=True),
        sa.Column("payer_name", sa.String(128), nullable=True),
        sa.Column("receipt_amount", sa.Numeric(18, 2), default=0),
        sa.Column("receipt_date", sa.Date, nullable=True),
        sa.Column("planned_receipt_date", sa.Date, nullable=True),
        sa.Column("is_overdue", sa.Boolean, default=False),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # invoices
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("created_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("status", sa.String(32), default="active"),
        sa.Column("invoice_code", sa.String(64), unique=True, nullable=False),
        sa.Column("invoice_type", sa.String(32), nullable=True),
        sa.Column("invoice_direction", sa.String(16), default="进项"),
        sa.Column("contract_id", sa.Integer, sa.ForeignKey("contracts.id"), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), default=0),
        sa.Column("tax_rate", sa.Numeric(5, 4), default=0),
        sa.Column("invoice_date", sa.Date, nullable=True),
        sa.Column("certification_status", sa.String(32), default="未认证"),
        sa.Column("approval_status", sa.String(32), default="待提交"),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("username", sa.String(64), nullable=True),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=True),
        sa.Column("resource_id", sa.Integer, nullable=True),
        sa.Column("detail", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_resource", "audit_logs", ["resource_type", "resource_id"])

    # workflows
    op.create_table(
        "workflows",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("business_type", sa.String(64), nullable=False, index=True),
        sa.Column("business_id", sa.Integer, nullable=False, index=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=True, index=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("workflow_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), default="draft"),
        sa.Column("current_step", sa.Integer, default=0),
        sa.Column("total_steps", sa.Integer, default=1),
        sa.Column("initiator_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("initiator_name", sa.String(64), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # workflow_steps
    op.create_table(
        "workflow_steps",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("workflow_id", sa.Integer, sa.ForeignKey("workflows.id"), nullable=False, index=True),
        sa.Column("step_order", sa.Integer, nullable=False),
        sa.Column("step_name", sa.String(64), nullable=False),
        sa.Column("approver_role", sa.String(64), nullable=True),
        sa.Column("approver_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approver_name", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), default="pending"),
        sa.Column("deadline_days", sa.Integer, nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
    )

    # workflow_actions
    op.create_table(
        "workflow_actions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("workflow_id", sa.Integer, sa.ForeignKey("workflows.id"), nullable=False, index=True),
        sa.Column("step_id", sa.Integer, sa.ForeignKey("workflow_steps.id"), nullable=True),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("actor_name", sa.String(64), nullable=True),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("workflow_actions")
    op.drop_table("workflow_steps")
    op.drop_table("workflows")
    op.drop_index("ix_audit_logs_resource", "audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("invoices")
    op.drop_table("receipts")
    op.drop_table("payments")
    op.drop_table("cost_records")
    op.drop_table("contracts")
    op.drop_index("ix_projects_project_code", "projects")
    op.drop_table("projects")
    op.drop_index("ix_users_username", "users")
    op.drop_table("users")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("departments")
