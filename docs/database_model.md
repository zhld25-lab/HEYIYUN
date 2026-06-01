# 数据库模型（Phase 1 + Phase 2）

## users 用户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int PK | |
| username | str unique | 登录名 |
| hashed_password | str | bcrypt 哈希 |
| full_name | str | 姓名 |
| is_active | bool | 是否启用 |
| role_id | FK roles | 角色 |
| department_id | FK departments | 部门（可空）|
| created_at / updated_at | datetime | |

## roles 角色表
| id | code | name | description |
角色与权限通过 `role_permissions` 多对多关联。

## permissions 权限表
| id | code | name | module |
权限码格式 `<module>:<action>`，如 `project:create`、`finance:view`。

## role_permissions 关联表
| role_id | permission_id |

## departments 部门表
| id | code | name |

## projects 项目表
核心业务主数据，字段（节选）：
- 基本信息：project_code(唯一)、project_name、project_type、voltage_level、project_location、region、project_status
- 参建单位：owner_unit、construction_unit、design_unit、supervision_unit、project_manager_id(FK users)
- 时间计划：planned_start_date、planned_end_date、actual_start_date、actual_end_date
- 金额：contract_amount、target_cost、actual_cost、received_amount、paid_amount、receivable_amount、payable_amount、profit、profit_margin
- 进度/资料/风险：production_progress、collection_progress、cost_ratio、document_completion_rate、risk_level
- 文本：description、remarks

派生字段（后端自动计算）：
- profit = contract_amount - actual_cost
- profit_margin = profit / contract_amount
- cost_ratio = actual_cost / target_cost

## audit_logs 审计日志表
| id | user_id | username | action | resource_type | resource_id | detail | ip_address | created_at |

每个 create / update / delete 操作写入一条记录。

## 迁移说明

开发环境通过 `app.db.init_db` 直接由 SQLAlchemy metadata 建表并填充种子数据。生产环境使用 Alembic 管理迁移（`backend/alembic`）。
