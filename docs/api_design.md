# API 设计

所有接口前缀 `/api/v1`，统一返回信封：

```json
{ "code": 0, "message": "success", "data": { } }
```

分页数据结构：

```json
{ "items": [], "total": 0, "page": 1, "page_size": 20 }
```

认证：除登录外，所有接口需在 `Authorization: Bearer <token>` 头中携带 JWT。

## 认证 Auth
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /auth/login | 登录，返回 token + 用户信息 | 公开 |
| GET | /auth/me | 当前登录用户 | 登录 |

## 项目 Projects
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /projects | 项目列表（支持筛选+分页）| project:view |
| POST | /projects | 新建项目 | project:create |
| GET | /projects/{id} | 项目详情 | project:view |
| PUT | /projects/{id} | 更新项目 | project:update |
| DELETE | /projects/{id} | 删除项目 | project:delete |
| GET | /projects/{id}/overview | 项目总览（Phase 2 返回基础信息）| project:view |

筛选参数：project_name、project_code、project_type、voltage_level、project_status、risk_level、page、page_size。

金额脱敏：无 `finance:view` 权限的用户，金额字段返回 `"***"`。

## 仪表盘 Dashboard
| GET | /dashboard/summary | 经营 KPI 汇总 | dashboard:view |
| GET | /dashboard/project-status | 项目状态分布 | dashboard:view |

## 合同 Contracts (Phase 3)
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /contracts | 合同列表（筛选+分页）| contract:view |
| POST | /contracts | 新建合同 | contract:create |
| GET | /contracts/{id} | 合同详情 | contract:view |
| PUT | /contracts/{id} | 更新合同 | contract:update |
| DELETE | /contracts/{id} | 删除合同（软删除）| contract:delete |

## 成本/付款/回款/发票 (Phase 3)
`/costs`、`/payments`、`/receipts`、`/invoices` 均提供 GET 列表、POST、GET/{id}、PUT/{id}、DELETE/{id}。
读取需 `contract:view`；新增/编辑需 `finance:edit`；删除需 `finance:delete`。

## 项目财务联动 (Phase 3)
| GET | /projects/{id}/contracts | 项目下合同 | contract:view |
| GET | /projects/{id}/costs | 项目下成本 | contract:view |
| GET | /projects/{id}/payments | 项目下付款 | contract:view |
| GET | /projects/{id}/receipts | 项目下回款 | contract:view |
| GET | /projects/{id}/invoices | 项目下发票 | contract:view |
| GET | /projects/{id}/finance-summary | 项目财务汇总 | project:view |

## 驾驶舱财务 (Phase 3)
| GET | /dashboard/finance-summary | 全局财务汇总 | dashboard:view |
| GET | /dashboard/cashflow | 月度回款/付款/净现金流 | dashboard:view |
| GET | /dashboard/cost-breakdown | 成本构成 | dashboard:view |
| GET | /dashboard/project-profit-top | 项目利润 Top 10 | dashboard:view |

所有金额字段对无 `finance:view` 的角色脱敏为 `***`。

## 系统 System
| GET | /system/audit-logs | 操作日志（分页，可按 resource_type/resource_id 过滤）| audit:view |

## 用户 Users
| GET | /users | 用户列表 | user:view |

## 健康检查
| GET | /health | 服务健康状态 | 公开 |

在线文档：后端启动后访问 `http://localhost:8000/docs`（Swagger UI）。
