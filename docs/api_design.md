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

## 系统 System
| GET | /system/audit-logs | 操作日志（分页，可按 resource_type/resource_id 过滤）| audit:view |

## 用户 Users
| GET | /users | 用户列表 | user:view |

## 健康检查
| GET | /health | 服务健康状态 | 公开 |

在线文档：后端启动后访问 `http://localhost:8000/docs`（Swagger UI）。
