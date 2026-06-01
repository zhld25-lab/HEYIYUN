# 从 Streamlit 原型迁移说明

## 背景

原系统为 Streamlit 多页面原型（现位于 `legacy_streamlit/`），用于演示电力工程企业项目经营管理的业务流程。本次迁移（方案 B）将其重构为前后端分离的全栈企业系统，原型完整保留作为业务参考，不被覆盖或删除。

## 保留 legacy_streamlit/ 的原因

1. **业务规则参考**：风险评分、项目健康度、成本超支判断等算法（`services/risk_service.py`、`project_service.py`、`cost_service.py`）是已验证的业务逻辑。
2. **字段定义参考**：`data/mock_*.py` 和 `docs/data_model.md` 定义了项目、合同、成本、材料、设备、资料等实体的完整字段。
3. **权限模型参考**：`config/role_config.py` 的角色—模块映射与金额脱敏规则。
4. **页面模块参考**：14 个业务模块的交互与展示需求。
5. **后续阶段蓝本**：合同、采购、审批流、风险引擎等模块迁移时直接参照。

## 已迁移内容（Phase 1 + Phase 2）

| Streamlit 原型 | 全栈实现 |
|----------------|----------|
| `services/permission_service.py` 金额脱敏 | `backend/app/services/permission_service.py` |
| 角色/模块映射 | `backend/app/core/permissions.py` + RBAC 数据表 |
| 项目字段 (`docs/data_model.md`) | `backend/app/models/project.py` |
| 项目中心页面 | `frontend/src/pages/ProjectCenter/*` |
| 决策驾驶舱 | `frontend/src/pages/Dashboard` |
| session_state 角色 | JWT + Zustand authStore |

## 未迁移内容（后续阶段）

合同、成本资金、采购物资、设备周材、施工现场、安全质量、资料档案、审批流引擎、风险预警引擎、逻辑图中心、MinIO 文件上传、Redis 缓存、仪表盘图表可视化。

这些模块在 `legacy_streamlit/` 中均有原型实现，可作为开发蓝本。

## 不应直接复用的部分

- Streamlit 组件 (`components/*.py`)、页面 (`pages/*.py`)：强依赖 Streamlit API，前端用 React + Ant Design 重写。
- mock 数据生成器：由数据库 + 种子数据 + 后续真实录入替代。
