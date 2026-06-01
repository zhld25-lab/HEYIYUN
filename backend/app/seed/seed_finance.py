from __future__ import annotations

"""Seed plausible (fictional) finance data for the Phase 3 closed loop.

Generates contracts / costs / payments / receipts / invoices linked to the
existing seed projects, then triggers project financial recalculation.
All names/amounts are fabricated for demo purposes only.
"""

import random
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.cost_record import CostRecord
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.project import Project
from app.models.receipt import Receipt
from app.services import finance_service

RNG = random.Random(20260601)
BASE_DATE = date(2025, 1, 1)

SUB_CONTRACT_TYPES = ["分包合同", "采购合同", "设备租赁合同", "周材租赁合同"]
COST_TYPES = [
    "分包成本", "材料成本", "人工成本", "机械设备成本", "周材租赁成本",
    "运输成本", "费用报销", "间接成本", "税费", "其他成本",
]
CONTRACT_STATUSES = ["拟定", "审批中", "执行中", "结算中", "已归档"]
APPROVAL_STATUSES = ["未提交", "审批中", "已通过", "已驳回"]
ARCHIVE_STATUSES = ["未归档", "归档中", "已归档"]
PAY_STATUSES = ["未付款", "部分付款", "已付款"]
INV_STATUSES = ["未收票", "部分收票", "已收票"]
INVOICE_TYPES = ["增值税专用发票", "增值税普通发票", "电子发票"]
CERT_STATUSES = ["未认证", "已认证", "无需认证"]


def _d(offset_days: int) -> date:
    return BASE_DATE + timedelta(days=offset_days)


def _money(low: int, high: int) -> float:
    return float(RNG.randint(low, high) * 1000)


def already_seeded(db: Session) -> bool:
    return db.scalar(select(Contract).limit(1)) is not None


def seed_finance(db: Session) -> None:
    if already_seeded(db):
        return

    projects = list(db.scalars(select(Project)).all())
    if not projects:
        return
    pids = [p.id for p in projects]
    by_id = {p.id: p for p in projects}

    # ---- Contracts: 1 main 承包合同 per project + sub-contracts up to 30 total ----
    contracts: list[Contract] = []
    cc = 1
    main_contract_by_project: dict[int, int] = {}
    for p in projects:
        c = Contract(
            contract_code=f"HT-2025-{cc:04d}",
            contract_name=f"{p.project_name}-总承包合同",
            contract_type="承包合同",
            project_id=p.id,
            party_a=p.owner_unit or "建设单位(示例)",
            party_b=p.construction_unit or "施工单位(示例)",
            contract_amount=_money(40000, 80000),
            settlement_amount=0,
            contract_status="执行中",
            approval_status="已通过",
            archive_status=RNG.choice(ARCHIVE_STATUSES),
            signed_date=_d(RNG.randint(10, 90)),
        )
        db.add(c)
        contracts.append(c)
        cc += 1

    db.flush()
    for c in contracts:
        main_contract_by_project[c.project_id] = c.id

    while len(contracts) < 30:
        pid = RNG.choice(pids)
        ctype = RNG.choice(SUB_CONTRACT_TYPES)
        c = Contract(
            contract_code=f"HT-2025-{cc:04d}",
            contract_name=f"{by_id[pid].project_name}-{ctype}{cc:02d}",
            contract_type=ctype,
            project_id=pid,
            party_a=by_id[pid].construction_unit or "施工单位(示例)",
            party_b=f"模拟供应商{RNG.randint(1, 40):02d}有限公司",
            contract_amount=_money(2000, 15000),
            settlement_amount=0,
            contract_status=RNG.choice(CONTRACT_STATUSES),
            approval_status=RNG.choice(APPROVAL_STATUSES),
            archive_status=RNG.choice(ARCHIVE_STATUSES),
            signed_date=_d(RNG.randint(20, 200)),
        )
        db.add(c)
        contracts.append(c)
        cc += 1
    db.flush()

    sub_contracts_by_project: dict[int, list[int]] = {pid: [] for pid in pids}
    for c in contracts:
        if c.contract_type != "承包合同":
            sub_contracts_by_project[c.project_id].append(c.id)

    def rand_sub(pid: int) -> int | None:
        subs = sub_contracts_by_project.get(pid) or []
        return RNG.choice(subs) if subs and RNG.random() < 0.7 else None

    # ---- Cost records: 80 ----
    for i in range(1, 81):
        pid = RNG.choice(pids)
        db.add(CostRecord(
            cost_code=f"CB-2025-{i:04d}",
            cost_type=RNG.choice(COST_TYPES),
            project_id=pid,
            contract_id=rand_sub(pid),
            supplier_name=f"模拟供应商{RNG.randint(1, 40):02d}有限公司",
            amount=_money(300, 1500),
            occurred_date=_d(RNG.randint(30, 330)),
            handler_name=RNG.choice(["王工", "张工", "刘工", "陈工", "赵工"]),
            approval_status=RNG.choice(APPROVAL_STATUSES),
            invoice_status=RNG.choice(INV_STATUSES),
            payment_status=RNG.choice(PAY_STATUSES),
        ))

    # ---- Payments: 50 (to sub-contractors / suppliers) ----
    for i in range(1, 51):
        pid = RNG.choice(pids)
        requested = _money(300, 1500)
        paid = round(requested * RNG.choice([0.3, 0.5, 0.8, 1.0]), 2)
        db.add(Payment(
            payment_code=f"FK-2025-{i:04d}",
            project_id=pid,
            contract_id=rand_sub(pid),
            payee_name=f"模拟供应商{RNG.randint(1, 40):02d}有限公司",
            requested_amount=requested,
            paid_amount=paid,
            payment_date=_d(RNG.randint(40, 340)),
            payment_status=RNG.choice(PAY_STATUSES),
            approval_status=RNG.choice(APPROVAL_STATUSES),
        ))

    # ---- Receipts: 50 (from owner, against main contract) ----
    for i in range(1, 51):
        pid = RNG.choice(pids)
        planned = _d(RNG.randint(60, 360))
        actual_offset = RNG.randint(-10, 40)
        receipt_dt = planned + timedelta(days=actual_offset)
        db.add(Receipt(
            receipt_code=f"HK-2025-{i:04d}",
            project_id=pid,
            contract_id=main_contract_by_project.get(pid),
            payer_name=by_id[pid].owner_unit or "建设单位(示例)",
            receipt_amount=_money(800, 2500),
            receipt_date=receipt_dt,
            planned_receipt_date=planned,
            is_overdue=actual_offset > 0,
        ))

    # ---- Invoices: 50 (进项 + 销项) ----
    for i in range(1, 51):
        pid = RNG.choice(pids)
        direction = RNG.choice(["进项", "销项"])
        contract_id = main_contract_by_project.get(pid) if direction == "销项" else rand_sub(pid)
        db.add(Invoice(
            invoice_code=f"FP-2025-{i:04d}",
            invoice_type=RNG.choice(INVOICE_TYPES),
            invoice_direction=direction,
            project_id=pid,
            contract_id=contract_id,
            amount=_money(500, 2000),
            tax_rate=RNG.choice([0.03, 0.06, 0.09, 0.13]),
            invoice_date=_d(RNG.randint(50, 350)),
            certification_status=RNG.choice(CERT_STATUSES),
        ))

    db.commit()

    # ---- Recompute project financial roll-ups from the seeded records ----
    for pid in pids:
        finance_service.recalculate(db, pid, commit=False)
    db.commit()
