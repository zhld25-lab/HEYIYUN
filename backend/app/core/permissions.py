from __future__ import annotations

"""Central definition of RBAC permission codes and role -> permission mapping.

This mirrors the role / module logic from the legacy Streamlit prototype
(see legacy_streamlit/config/role_config.py and services/permission_service.py).
"""

# --- Permission codes -------------------------------------------------------
# Format: "<module>:<action>"
PERM_PROJECT_VIEW = "project:view"
PERM_PROJECT_CREATE = "project:create"
PERM_PROJECT_UPDATE = "project:update"
PERM_PROJECT_DELETE = "project:delete"

PERM_DASHBOARD_VIEW = "dashboard:view"

# Ability to see precise financial amounts (otherwise masked as ***)
PERM_FINANCE_VIEW = "finance:view"

# System administration
PERM_AUDIT_VIEW = "audit:view"
PERM_USER_VIEW = "user:view"
PERM_SYSTEM_MANAGE = "system:manage"

ALL_PERMISSIONS: list[tuple[str, str, str]] = [
    # (code, name, module)
    (PERM_PROJECT_VIEW, "查看项目", "project"),
    (PERM_PROJECT_CREATE, "新建项目", "project"),
    (PERM_PROJECT_UPDATE, "编辑项目", "project"),
    (PERM_PROJECT_DELETE, "删除项目", "project"),
    (PERM_DASHBOARD_VIEW, "查看驾驶舱", "dashboard"),
    (PERM_FINANCE_VIEW, "查看金额明细", "finance"),
    (PERM_AUDIT_VIEW, "查看操作日志", "system"),
    (PERM_USER_VIEW, "查看用户", "system"),
    (PERM_SYSTEM_MANAGE, "系统管理", "system"),
]

# --- Role definitions -------------------------------------------------------
# (role_code, role_name)
ROLES: list[tuple[str, str]] = [
    ("admin", "系统管理员"),
    ("general_manager", "总经理"),
    ("finance", "财务负责人"),
    ("project_manager", "项目经理"),
    ("safety", "安全员"),
    ("quality", "质量员"),
    ("document", "资料员"),
    ("staff", "普通员工"),
]

_FULL = [code for code, _, _ in ALL_PERMISSIONS]

# Role -> list of permission codes
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": _FULL,
    "general_manager": _FULL,
    "finance": [
        PERM_DASHBOARD_VIEW,
        PERM_PROJECT_VIEW,
        PERM_FINANCE_VIEW,
        PERM_AUDIT_VIEW,
    ],
    "project_manager": [
        PERM_DASHBOARD_VIEW,
        PERM_PROJECT_VIEW,
        PERM_PROJECT_CREATE,
        PERM_PROJECT_UPDATE,
    ],
    "safety": [PERM_DASHBOARD_VIEW, PERM_PROJECT_VIEW],
    "quality": [PERM_DASHBOARD_VIEW, PERM_PROJECT_VIEW],
    "document": [PERM_DASHBOARD_VIEW, PERM_PROJECT_VIEW],
    "staff": [PERM_DASHBOARD_VIEW, PERM_PROJECT_VIEW],
}
