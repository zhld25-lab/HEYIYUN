# 中国电力工程企业项目经营管理平台

**Power Engineering ERP & Project Management Platform**

面向电力工程企业的全栈项目经营管理系统，围绕项目全生命周期（立项、报装、合同、采购、施工、成本、资金、安全质量、资料、审批、风险预警）开展管理。本仓库由 Streamlit 原型迁移而来，现为前后端分离架构。

> 当前进度：**Phase 1（系统骨架）+ Phase 2（项目中心）** 已完成。

---

## 1. 项目简介

- 后端：FastAPI 提供 RESTful API，PostgreSQL 持久化，JWT 认证 + RBAC 权限，操作审计日志。
- 前端：React + TypeScript 单页应用，Ant Design 企业级 UI，深蓝侧边栏 + 白色卡片内容区。
- 项目中心：项目 CRUD、列表筛选、企业级立项表单、项目详情、金额按角色脱敏。

## 2. 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React, TypeScript, Vite, Ant Design, React Router, TanStack Query, Axios, Zustand |
| 后端 | Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic v2, Alembic |
| 存储 | PostgreSQL, Redis（缓存，后续）, MinIO（文件，占位）|
| 安全 | JWT, bcrypt, RBAC |
| DevOps | Docker, Docker Compose |

## 3. 架构

```
frontend/  React SPA（Ant Design）
backend/   FastAPI（api → services → crud → models）
infra/     Nginx 反向代理配置
docs/      架构 / 数据库 / API / 权限 / 迁移文档
legacy_streamlit/  原 Streamlit 原型（业务参考，不参与运行）
docker-compose.yml / Makefile / .env.example
```

详见 `docs/system_architecture.md`。

## 4. 为何保留 legacy_streamlit/

`legacy_streamlit/` 是原 Streamlit 原型，**完整保留作为业务规则、字段定义、页面模块、mock 数据和风险逻辑的参考**，不被覆盖或删除。新模块（合同、成本、审批流、风险引擎等）迁移时以其为蓝本。详见 `docs/migration_from_streamlit.md`。

## 5. 使用 Docker Compose 运行

```bash
cp .env.example .env        # 按需修改密码与密钥
docker compose up -d --build
```

- 前端：http://localhost:5173
- 后端 API 文档：http://localhost:8000/docs
- 后端首次启动会自动建表并填充种子数据。

校验编排配置：`docker compose config` 或 `make compose-config`。

## 6. 手动运行后端

前置条件：本地有一个运行中的 PostgreSQL，并存在与 `.env` 一致的数据库和用户。
例如（仅首次需要）：

```bash
createdb power_engineering_erp
psql -c "CREATE USER erp_user WITH PASSWORD 'erp_password';"
psql -c "ALTER DATABASE power_engineering_erp OWNER TO erp_user;"
```

启动后端：

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# 指向本地 PostgreSQL（默认值见 app/core/config.py）
export POSTGRES_HOST=localhost POSTGRES_USER=erp_user POSTGRES_PASSWORD=erp_password POSTGRES_DB=power_engineering_erp
uvicorn app.main:app --reload --port 8000
```

启动时会自动建表并填充种子数据（也可手动执行 `python -m app.db.init_db`）。
若未设置 `SECRET_KEY`，将使用 `config.py` 中的开发默认值，生产环境务必覆盖。

## 7. 手动运行前端

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173 （已配置 /api 代理到 8000）
```

## 8. 种子账号与密码

| 用户名 | 密码 | 角色 | 金额可见 |
|--------|------|------|----------|
| admin | Admin123456 | 系统管理员 | ✅ |
| manager | Manager123456 | 总经理 | ✅ |
| finance | Finance123456 | 财务负责人 | ✅ |
| pm | PM123456 | 项目经理 | ❌ |
| safety | Safety123456 | 安全员 | ❌ |
| quality | Quality123456 | 质量员 | ❌ |
| document | Document123456 | 资料员 | ❌ |
| staff | Staff123456 | 普通员工 | ❌ |

## 9. API 文档地址

- Swagger UI：http://localhost:8000/docs
- 设计文档：`docs/api_design.md`

## 10. 前端地址

http://localhost:5173

## 11. 已实现功能

**Phase 1 + 2（系统骨架 + 项目中心）**
- JWT 登录认证、bcrypt 密码加密、`/auth/me` 当前用户。
- RBAC 权限体系（用户—角色—权限），接口级 + 字段级（金额脱敏）控制。
- 项目 CRUD：列表（多条件筛选 + 分页）、新建立项表单（6 个分区 + 校验）、详情（Tabs）、编辑、删除。
- 项目金额按角色脱敏（普通员工显示 `***`）。
- 操作审计日志：所有写操作自动记录，系统设置与详情页可查看。
- 决策驾驶舱：经营 KPI 汇总 + 项目状态分布。
- 企业级前端布局：深蓝侧边栏、顶部用户/角色/退出、面包屑。
- Docker Compose 一键运行（postgres / redis / minio / backend / frontend）。

**Phase 3（合同中心 + 成本资金中心 + 业务闭环）**
- 5 个新业务实体：合同(Contract)、成本(CostRecord)、付款(Payment)、回款(Receipt)、发票(Invoice)，均含软删除与创建/更新人追踪。
- 合同中心：列表（多条件筛选）、分区表单（5 个区）、详情页、增删改查。
- 成本资金中心：成本台账 / 付款 / 回款 / 发票 / 财务分析 五个 Tab，含 ECharts 图表（成本构成、回款付款趋势、利润 Top10、应收应付对比）。
- **业务闭环**：项目 → 合同 → 成本 → 付款/回款 → 发票 → 项目财务汇总。任何财务记录变更都会实时回算项目 `contract_amount / actual_cost / paid_amount / received_amount / receivable / payable / profit / profit_margin / collection_progress / cost_ratio`。
- 项目详情页「合同记录」「成本资金」Tab 已联动真实数据 + 项目财务汇总卡片。
- 合同/成本/财务记录的金额继续遵循角色脱敏；财务删除仅限管理员/总经理/财务负责人，项目经理可看可编辑但不可删除。
- 全部 create/update/delete 写入 audit_logs。
- 种子数据：30 合同 / 80 成本 / 50 付款 / 50 回款 / 50 发票（模拟数据，按 project_id 关联）。

## 12. 后续阶段 (Next Phases)

- MinIO 资料档案上传（Document upload）
- 审批工作流引擎（Workflow engine）
- 风险预警引擎（Risk engine）
- 采购物资 / 设备周材 / 施工现场 / 安全质量模块
- 首个 Alembic 迁移脚本（替代开发期 create_all）
- 前端打包体积优化（图表库按需/懒加载）
