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

## Phase 3 财务实体（contracts / cost_records / payments / receipts / invoices）

5 张表均含公共列：`id`、`project_id`(FK)、`created_at`、`updated_at`、`created_by_id`(FK users)、`updated_by_id`(FK users)、`deleted_at`(软删除)、`status`。

- **contracts**：contract_code(唯一)、contract_name、contract_type(承包/分包/采购/设备租赁/周材租赁)、party_a、party_b、contract_amount、settlement_amount、invoiced_amount、received_amount、paid_amount、receivable_amount、payable_amount、contract_status、approval_status、archive_status、signed_date、description、remarks。
- **cost_records**：cost_code(唯一)、cost_type(10 类)、contract_id(可空)、supplier_name、amount、occurred_date、handler_name、approval_status、invoice_status、payment_status、remarks。
- **payments**：payment_code(唯一)、contract_id(可空)、payee_name、requested_amount、paid_amount、payment_date、payment_status、approval_status、remarks。
- **receipts**：receipt_code(唯一)、contract_id(可空)、payer_name、receipt_amount、receipt_date、planned_receipt_date、is_overdue、remarks。
- **invoices**：invoice_code(唯一)、invoice_type、invoice_direction(进项/销项)、contract_id(可空)、amount、tax_rate、invoice_date、certification_status、remarks。

### 财务回算（finance_service.recalculate）
任一财务记录写操作后，按 project_id 重算合同级（received/paid/invoiced/receivable/payable）与项目级聚合：
contract_amount(承包合同汇总)、actual_cost(成本汇总)、paid_amount(付款汇总)、received_amount(回款汇总)、receivable_amount、payable_amount、profit、profit_margin(profit/received)、collection_progress(received/contract，0-1)、cost_ratio(actual/target，0-1)。

> 说明：collection_progress 与 cost_ratio 以 0-1 比例存储（前端 formatPercent 统一 ×100 展示），与 Phase 2 字段口径一致。

## audit_logs 审计日志表
| id | user_id | username | action | resource_type | resource_id | detail | ip_address | created_at |

每个 create / update / delete 操作写入一条记录。

## 迁移说明

开发环境通过 `app.db.init_db` 直接由 SQLAlchemy metadata 建表并填充种子数据。生产环境使用 Alembic 管理迁移（`backend/alembic`）。
