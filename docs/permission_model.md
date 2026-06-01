# 权限模型 (RBAC)

## 模型

用户 → 角色 → 权限。一个用户拥有一个角色，角色绑定一组权限码。
权限校验通过 FastAPI 依赖 `require_permission(code)` 在接口层强制执行；
前端通过 `PermissionGuard` 组件与 `hasPermission()` 控制按钮/菜单可见性。

## 权限码

| 权限码 | 名称 | 模块 |
|--------|------|------|
| project:view | 查看项目 | project |
| project:create | 新建项目 | project |
| project:update | 编辑项目 | project |
| project:delete | 删除项目 | project |
| dashboard:view | 查看驾驶舱 | dashboard |
| finance:view | 查看金额明细 | finance |
| audit:view | 查看操作日志 | system |
| user:view | 查看用户 | system |
| system:manage | 系统管理 | system |

## 角色与权限映射

| 角色 (code) | 中文 | 权限 |
|-------------|------|------|
| admin | 系统管理员 | 全部 |
| general_manager | 总经理 | 全部 |
| finance | 财务负责人 | dashboard:view, project:view, finance:view, audit:view |
| project_manager | 项目经理 | dashboard:view, project:view, project:create, project:update |
| safety | 安全员 | dashboard:view, project:view |
| quality | 质量员 | dashboard:view, project:view |
| document | 资料员 | dashboard:view, project:view |
| staff | 普通员工 | dashboard:view, project:view |

## 金额脱敏

拥有 `finance:view` 的角色（系统管理员、总经理、财务负责人）可见完整金额；
其余角色在项目列表、详情、驾驶舱中的金额字段显示为 `***`。
该逻辑沿用 legacy_streamlit/services/permission_service.py 的脱敏思想，
在后端 `services/permission_service.py` 实现，确保脱敏发生在服务端而非仅前端隐藏。
