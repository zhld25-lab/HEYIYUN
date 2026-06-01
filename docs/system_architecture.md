# 系统架构

## 系统定位

中国电力工程企业项目经营管理平台（Power Engineering ERP & Project Management Platform）面向电力工程企业，围绕项目全生命周期开展经营管理。本仓库由 Streamlit 原型迁移为前后端分离的全栈系统。

## 总体架构

```
┌─────────────┐      HTTP/JSON       ┌──────────────┐
│   前端 SPA   │  ◀───────────────▶  │   后端 API    │
│ React + AntD │   /api/v1/*          │   FastAPI    │
└─────────────┘                      └──────┬───────┘
                                            │ SQLAlchemy 2.x
                                     ┌──────▼───────┐
                                     │  PostgreSQL  │
                                     └──────────────┘
                                     ┌──────────────┐
                                     │    Redis     │ (缓存，后续阶段)
                                     └──────────────┘
                                     ┌──────────────┐
                                     │    MinIO     │ (文件存储，占位)
                                     └──────────────┘
```

## 后端分层

- `api/v1/endpoints` 路由层：参数校验、权限依赖、调用 service。
- `services` 业务逻辑层：项目派生指标、金额脱敏、审计、仪表盘统计。
- `crud` 数据访问层：SQLAlchemy 查询封装。
- `models` ORM 模型层。
- `schemas` Pydantic v2 输入/输出模型。
- `core` 配置、安全(JWT/bcrypt)、依赖、权限定义。

## 前端分层

- `api` Axios 封装 + 类型化请求。
- `store` Zustand 全局状态（认证、布局）。
- `pages` 业务页面。
- `components` 通用企业级组件。
- `layouts` 基础布局 / 登录布局。
- `router` React Router 路由表。
- 数据获取统一使用 TanStack Query。

## 与 legacy_streamlit 的关系

`legacy_streamlit/` 是原 Streamlit 原型，完整保留作为业务规则、字段定义、页面模块和风险逻辑的参考，不参与新系统运行。详见 `migration_from_streamlit.md`。
