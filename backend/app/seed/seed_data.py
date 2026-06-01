from __future__ import annotations

"""Idempotent seeding of permissions, roles, users and sample projects."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import ALL_PERMISSIONS, ROLE_PERMISSIONS, ROLES
from app.core.security import hash_password
from app.models.permission import Permission
from app.models.project import Project
from app.models.role import Role
from app.models.user import User
from app.services.project_service import recompute_derived_fields

# username / password / role_code / full_name
SEED_USERS = [
    ("admin", "Admin123456", "admin", "系统管理员-陈工"),
    ("manager", "Manager123456", "general_manager", "总经理-周总"),
    ("finance", "Finance123456", "finance", "财务负责人-林会计"),
    ("pm", "PM123456", "project_manager", "项目经理-王工"),
    ("safety", "Safety123456", "safety", "安全员-刘工"),
    ("quality", "Quality123456", "quality", "质量员-黄工"),
    ("document", "Document123456", "document", "资料员-吴工"),
    ("staff", "Staff123456", "staff", "普通员工-李工"),
]

SEED_PROJECTS = [
    {
        "project_code": "PJ-2025-001",
        "project_name": "某工业园 10kV 配电工程",
        "project_type": "10kV配电工程",
        "voltage_level": "10kV",
        "region": "华东",
        "project_status": "施工中",
        "owner_unit": "某工业园管委会",
        "construction_unit": "恒运电力工程有限公司",
        "planned_start_date": date(2025, 3, 1),
        "planned_end_date": date(2025, 11, 30),
        "contract_amount": 18600000,
        "target_cost": 15200000,
        "actual_cost": 9800000,
        "received_amount": 11000000,
        "paid_amount": 8200000,
        "production_progress": 0.62,
        "collection_progress": 0.59,
        "document_completion_rate": 0.74,
        "risk_level": "中",
    },
    {
        "project_code": "PJ-2025-002",
        "project_name": "某 220kV 输变电工程配套项目",
        "project_type": "220kV输变电工程",
        "voltage_level": "220kV",
        "region": "华南",
        "project_status": "报装中",
        "owner_unit": "省电网建设公司",
        "construction_unit": "恒运电力工程有限公司",
        "planned_start_date": date(2025, 5, 10),
        "planned_end_date": date(2026, 6, 30),
        "contract_amount": 96000000,
        "target_cost": 82000000,
        "actual_cost": 23000000,
        "received_amount": 18000000,
        "paid_amount": 16500000,
        "production_progress": 0.24,
        "collection_progress": 0.18,
        "document_completion_rate": 0.55,
        "risk_level": "高",
    },
    {
        "project_code": "PJ-2025-003",
        "project_name": "某产业园光伏并网工程",
        "project_type": "光伏并网工程",
        "voltage_level": "35kV",
        "region": "华北",
        "project_status": "验收中",
        "owner_unit": "绿能新能源公司",
        "construction_unit": "恒运电力工程有限公司",
        "planned_start_date": date(2025, 1, 15),
        "planned_end_date": date(2025, 9, 20),
        "contract_amount": 42000000,
        "target_cost": 36000000,
        "actual_cost": 35200000,
        "received_amount": 38000000,
        "paid_amount": 33000000,
        "production_progress": 0.9,
        "collection_progress": 0.86,
        "document_completion_rate": 0.92,
        "risk_level": "低",
    },
]


def _seed_permissions(db: Session) -> dict[str, Permission]:
    existing = {p.code: p for p in db.scalars(select(Permission)).all()}
    for code, name, module in ALL_PERMISSIONS:
        if code not in existing:
            perm = Permission(code=code, name=name, module=module)
            db.add(perm)
            existing[code] = perm
    db.flush()
    return existing


def _seed_roles(db: Session, perms: dict[str, Permission]) -> dict[str, Role]:
    existing = {r.code: r for r in db.scalars(select(Role)).all()}
    for code, name in ROLES:
        role = existing.get(code)
        if role is None:
            role = Role(code=code, name=name)
            db.add(role)
            existing[code] = role
        role.permissions = [perms[c] for c in ROLE_PERMISSIONS.get(code, []) if c in perms]
    db.flush()
    return existing


def _seed_users(db: Session, roles: dict[str, Role]) -> dict[str, User]:
    existing = {u.username: u for u in db.scalars(select(User)).all()}
    for username, password, role_code, full_name in SEED_USERS:
        if username not in existing:
            user = User(
                username=username,
                hashed_password=hash_password(password),
                full_name=full_name,
                role_id=roles[role_code].id if role_code in roles else None,
            )
            db.add(user)
            existing[username] = user
    db.flush()
    return existing


def _seed_projects(db: Session, users: dict[str, User]) -> None:
    if db.scalar(select(Project).limit(1)) is not None:
        return
    pm = users.get("pm")
    for data in SEED_PROJECTS:
        project = Project(**data)
        if pm:
            project.project_manager_id = pm.id
        recompute_derived_fields(project)
        db.add(project)


def seed_all(db: Session) -> None:
    perms = _seed_permissions(db)
    roles = _seed_roles(db, perms)
    users = _seed_users(db, roles)
    _seed_projects(db, users)
    db.commit()
