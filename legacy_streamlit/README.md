# HEYIYUN

中国电力工程企业项目经营管理平台  
Power Engineering ERP & Project Management Platform

## 项目简介

HEYIYUN 是一个基于 Streamlit 的电力工程行业 ERP 与项目经营管理系统 Demo，围绕“项目”建立业务主线，覆盖项目立项、供电报装、合同签订、预算/目标成本、材料计划、采购合同、到货入库、施工进度、安全质量检查、工程量确认、变更签证、成本归集、付款/回款、发票、结算、竣工资料和项目复盘。

系统使用模拟数据，仅用于产品原型、学习、作品集、课程设计、业务方案展示和 GitHub 项目展示。

## 行业背景

电力工程企业通常同时管理多个配电、输变电、光伏并网、箱变安装、电缆迁改、充电站配套、临时用电和配电房改造项目。项目过程中涉及建设单位、设计、监理、分包、供应商、仓库、施工班组、安全质量和资料归档等多方协同。本 Demo 用 Streamlit 快速模拟一套项目全生命周期经营管理平台。

## 核心功能

- 首页工作台：待办、已办、我的发起、风险提醒、快捷入口。
- 决策驾驶舱：公司级 KPI、现金流、利润、风险、供应商和分包商排名。
- 项目中心：项目列表、筛选、项目详情 Tabs、健康度评分。
- 合同中心：承包、分包、采购、设备租赁、周材租赁合同管理。
- 采购物资中心：材料计划、采购、到货、入库、出库、库存和价格库。
- 设备周材中心：设备台账、调度、维修、保养、租赁和结算。
- 成本资金中心：成本台账、费用报销、付款、回款、发票、资金计划、保证金。
- 施工现场中心：施工日志、班组、人员进退场、工序、工程量、签证变更。
- 安全质量中心：安全隐患、质量缺陷、整改复查和闭环。
- 资料档案中心：全过程资料、完整率、缺失提醒、模拟上传、审核流程。
- 审批中心：OA/BPM 审批流模拟。
- 风险预警中心：工期、成本、资金、合同、采购、材料、设备、安全、质量、资料、审批风险。
- 逻辑图中心：项目生命周期、数据关联和关键业务流程图。
- 系统设置：用户、角色、权限、组织、菜单、字典、流程和日志模拟。

## 系统截图占位

后续可以在 `docs/images/` 中补充以下截图：

- 首页经营概览截图
- 决策驾驶舱截图
- 项目中心详情截图
- 风险预警中心截图
- 逻辑图中心截图

## 技术栈

- Python 3.10+
- Streamlit
- pandas
- numpy
- plotly
- openpyxl
- python-dotenv

## 项目结构

```text
HEYIYUN/
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── config/
├── data/
├── services/
├── components/
├── pages/
├── utils/
├── assets/
├── docs/
└── tests/
```

## 安装方法

```bash
pip install -r requirements.txt
```

## 运行方法

```bash
streamlit run app.py
```

启动后在浏览器中打开 Streamlit 提示的本地地址。

## 页面说明

Streamlit 多页面位于 `pages/` 目录。页面文件名使用英文以避免跨平台编码问题，但页面标题、菜单说明、表格字段和业务说明均为中文。

## 数据模型

模拟数据位于 `data/` 目录，统一由 `data/data_loader.py` 生成。核心模型包括：

- Project：项目主数据
- Contract：合同数据
- Cost：成本数据
- Material：材料数据
- Equipment：设备周材数据
- Finance：资金、发票、保证金数据
- Workflow：审批流程数据
- Risk：风险预警数据
- Document：资料档案数据
- SafetyQuality：安全质量记录

所有业务数据均通过 `project_id` 与项目关联。

## 风险预警逻辑

`services/risk_service.py` 实现 `calculate_project_risk(project, related_data)`，根据以下规则计算风险：

- 工期延期
- 成本超预算
- 收款进度低于产值进度 20% 以上
- 付款异常
- 安全隐患未闭环
- 质量问题未闭环
- 资料完整率低于 80%
- 审批流程超时

## 权限角色说明

系统通过 `st.session_state` 模拟当前角色。普通员工金额脱敏显示为 `***`；财务负责人、总经理和系统管理员可查看完整财务金额。

角色包括：系统管理员、总经理、财务负责人、项目经理、采购负责人、仓库管理员、安全员、质量员、资料员、施工班组长、普通员工。

## GitHub 提交方式

```bash
git init
git add .
git commit -m "Initial commit: HEYIYUN power engineering ERP Streamlit prototype"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

请将 `<your-github-repo-url>` 替换为你自己的 GitHub 仓库地址。

## 后续升级计划

- 接入真实登录、用户、角色和权限。
- 使用 PostgreSQL/MySQL 替代 mock 数据。
- 使用 FastAPI 提供后端接口。
- 使用 Vue/React 构建正式前端。
- 引入真实文件上传、对象存储和资料版本管理。
- 接入 BPMN 审批流引擎。
- 增加移动端、小程序、现场扫码和照片水印。
- 增加合同、采购、成本和资金的真实业务校验。

## 免责声明

本项目使用模拟数据，仅用于产品原型、学习、作品集和业务方案展示，不包含真实企业敏感数据。
