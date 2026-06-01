# 电力工程 ERP · Streamlit 数据看板

基于 FastAPI 后端 API 构建的 Streamlit 全功能网页应用。

## 功能页面

| 页面 | 功能 |
|------|------|
| 📊 经营驾驶舱 | KPI 指标 + 项目状态分布 + 成本构成 + 月度现金流 + 利润 Top10 |
| 🏗️ 项目中心 | 项目列表/筛选/新建/编辑/详情/财务汇总/审批记录 |
| 📄 合同中心 | 合同列表/新建/编辑/详情/提交审批/审批记录 |
| 💰 成本资金 | 成本台账/付款管理/回款管理/发票管理（含新增+审批提交）|
| ✅ 审批中心 | 我的待办/已办/发起/全部流程 + 在线审批操作 |
| ⚙️ 系统设置 | 用户列表 + 操作日志 |

## 前置条件

后端服务必须运行：

```bash
# 方式一：Docker Compose（推荐）
cd ..
cp .env.example .env
docker compose up -d --build

# 方式二：手动启动后端
cd ../backend
uvicorn app.main:app --reload --port 8000
```

## 安装与运行

```bash
cd streamlit_dashboard
cp .env.example .env        # 按需修改后端地址
pip install -r requirements.txt
streamlit run app.py
```

浏览器访问：http://localhost:8501

## 测试账号

| 用户名 | 密码 | 角色 | 金额可见 |
|--------|------|------|----------|
| admin | Admin123456 | 系统管理员 | ✅ |
| manager | Manager123456 | 总经理 | ✅ |
| finance | Finance123456 | 财务负责人 | ✅ |
| pm | PM123456 | 项目经理 | ✅ |
| staff | Staff123456 | 普通员工 | ❌（金额脱敏）|

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| ERP_API_URL | http://localhost:8000/api/v1 | 后端 API 地址 |
