from __future__ import annotations

"""Phase 3 finance closed-loop logic.

Project → Contract → Cost → Payment / Receipt / Invoice → project financial roll-up.

On every create/update/delete of a finance entity, ``recalculate(db, project_id)``
recomputes the contract-level and project-level aggregates so that the project
financial summary always reflects the underlying records.
"""

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.cost_record import CostRecord
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.project import Project
from app.models.receipt import Receipt

MAIN_CONTRACT_TYPE = "承包合同"


def _f(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _active(query):
    return query


def _load_project_records(db: Session, project_id: int):
    def alive(model):
        return list(
            db.scalars(
                select(model).where(model.project_id == project_id, model.deleted_at.is_(None))
            ).all()
        )

    return (
        alive(Contract),
        alive(CostRecord),
        alive(Payment),
        alive(Receipt),
        alive(Invoice),
    )


def recalculate(db: Session, project_id: int, *, commit: bool = True) -> None:
    """Recompute contract-level and project-level financial aggregates."""
    project = db.get(Project, project_id)
    if project is None:
        return

    contracts, costs, payments, receipts, invoices = _load_project_records(db, project_id)

    # --- group child records by contract for contract-level roll-up ---
    paid_by_contract: dict[int, float] = defaultdict(float)
    received_by_contract: dict[int, float] = defaultdict(float)
    invoiced_by_contract: dict[int, float] = defaultdict(float)
    for p in payments:
        if p.contract_id:
            paid_by_contract[p.contract_id] += _f(p.paid_amount)
    for r in receipts:
        if r.contract_id:
            received_by_contract[r.contract_id] += _f(r.receipt_amount)
    for inv in invoices:
        if inv.contract_id:
            invoiced_by_contract[inv.contract_id] += _f(inv.amount)

    for c in contracts:
        c.received_amount = round(received_by_contract.get(c.id, 0.0), 2)
        c.paid_amount = round(paid_by_contract.get(c.id, 0.0), 2)
        c.invoiced_amount = round(invoiced_by_contract.get(c.id, 0.0), 2)
        c.receivable_amount = round(_f(c.contract_amount) - c.received_amount, 2)
        base = _f(c.settlement_amount) or _f(c.contract_amount)
        c.payable_amount = round(base - c.paid_amount, 2)

    # --- project-level aggregates ---
    contract_amount = sum(_f(c.contract_amount) for c in contracts if c.contract_type == MAIN_CONTRACT_TYPE)
    actual_cost = sum(_f(c.amount) for c in costs)
    paid_amount = sum(_f(p.paid_amount) for p in payments)
    received_amount = sum(_f(r.receipt_amount) for r in receipts)
    target_cost = _f(project.target_cost)

    project.contract_amount = round(contract_amount, 2)
    project.actual_cost = round(actual_cost, 2)
    project.paid_amount = round(paid_amount, 2)
    project.received_amount = round(received_amount, 2)
    project.receivable_amount = round(contract_amount - received_amount, 2)
    project.payable_amount = round(actual_cost - paid_amount, 2)
    project.profit = round(received_amount - actual_cost, 2)
    project.profit_margin = round(project.profit / received_amount, 4) if received_amount > 0 else 0
    # Stored as 0-1 ratios to stay consistent with Phase 2 schema and frontend formatPercent.
    project.collection_progress = round(received_amount / contract_amount, 4) if contract_amount > 0 else 0
    project.cost_ratio = round(actual_cost / target_cost, 4) if target_cost > 0 else 0

    if commit:
        db.commit()


def get_project_finance_summary(db: Session, project_id: int) -> dict | None:
    project = db.get(Project, project_id)
    if project is None:
        return None
    return {
        "project_id": project.id,
        "contract_amount": project.contract_amount,
        "target_cost": project.target_cost,
        "actual_cost": project.actual_cost,
        "received_amount": project.received_amount,
        "paid_amount": project.paid_amount,
        "receivable_amount": project.receivable_amount,
        "payable_amount": project.payable_amount,
        "profit": project.profit,
        "profit_margin": project.profit_margin,
        "collection_progress": float(project.collection_progress or 0),
        "cost_ratio": float(project.cost_ratio or 0),
    }


# --------------------------- Dashboard aggregations ---------------------------

def dashboard_finance_summary(db: Session) -> dict:
    projects = list(db.scalars(select(Project)).all())
    return {
        "total_contract_amount": round(sum(_f(p.contract_amount) for p in projects), 2),
        "total_actual_cost": round(sum(_f(p.actual_cost) for p in projects), 2),
        "total_received": round(sum(_f(p.received_amount) for p in projects), 2),
        "total_paid": round(sum(_f(p.paid_amount) for p in projects), 2),
        "total_receivable": round(sum(_f(p.receivable_amount) for p in projects), 2),
        "total_payable": round(sum(_f(p.payable_amount) for p in projects), 2),
        "total_profit": round(sum(_f(p.profit) for p in projects), 2),
    }


def dashboard_cashflow(db: Session) -> list[dict]:
    """Monthly received vs paid net cashflow."""
    received: dict[str, float] = defaultdict(float)
    paid: dict[str, float] = defaultdict(float)

    for r in db.scalars(select(Receipt).where(Receipt.deleted_at.is_(None))).all():
        if r.receipt_date:
            received[r.receipt_date.strftime("%Y-%m")] += _f(r.receipt_amount)
    for p in db.scalars(select(Payment).where(Payment.deleted_at.is_(None))).all():
        if p.payment_date:
            paid[p.payment_date.strftime("%Y-%m")] += _f(p.paid_amount)

    months = sorted(set(received) | set(paid))
    return [
        {
            "month": m,
            "received": round(received.get(m, 0.0), 2),
            "paid": round(paid.get(m, 0.0), 2),
            "net": round(received.get(m, 0.0) - paid.get(m, 0.0), 2),
        }
        for m in months
    ]


def dashboard_cost_breakdown(db: Session) -> list[dict]:
    totals: dict[str, float] = defaultdict(float)
    for c in db.scalars(select(CostRecord).where(CostRecord.deleted_at.is_(None))).all():
        totals[c.cost_type] += _f(c.amount)
    items = [{"cost_type": k, "amount": round(v, 2)} for k, v in totals.items()]
    return sorted(items, key=lambda x: x["amount"], reverse=True)


def dashboard_project_profit_top(db: Session, limit: int = 10) -> list[dict]:
    projects = list(db.scalars(select(Project)).all())
    ranked = sorted(projects, key=lambda p: _f(p.profit), reverse=True)[:limit]
    return [
        {"project_id": p.id, "project_name": p.project_name, "profit": round(_f(p.profit), 2)}
        for p in ranked
    ]
