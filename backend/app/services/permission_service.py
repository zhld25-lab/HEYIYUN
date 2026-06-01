from __future__ import annotations

"""Permission helpers including financial field masking.

Mirrors the masking behaviour from the legacy Streamlit prototype
(legacy_streamlit/services/permission_service.py): users without the
``finance:view`` permission see sensitive amounts as ``***``.
"""

from app.core.permissions import PERM_FINANCE_VIEW
from app.models.user import User

MASK_VALUE = "***"

# Project financial fields subject to masking.
SENSITIVE_PROJECT_FIELDS = [
    "contract_amount",
    "target_cost",
    "actual_cost",
    "received_amount",
    "paid_amount",
    "receivable_amount",
    "payable_amount",
    "profit",
    "profit_margin",
]

SENSITIVE_DASHBOARD_FIELDS = [
    "contract_amount",
    "received_amount",
    "paid_amount",
    "current_profit",
    "total_contract_amount",
    "total_actual_cost",
    "total_received",
    "total_paid",
    "total_receivable",
    "total_payable",
    "total_profit",
]

# Amount fields for the Phase 3 finance entities subject to masking.
SENSITIVE_FINANCE_FIELDS = [
    "contract_amount",
    "settlement_amount",
    "invoiced_amount",
    "received_amount",
    "paid_amount",
    "receivable_amount",
    "payable_amount",
    "amount",
    "requested_amount",
    "receipt_amount",
    "profit",
    "profit_margin",
    "target_cost",
    "actual_cost",
]


def has_permission(user: User, code: str) -> bool:
    return code in user.permission_codes


def can_view_finance(user: User) -> bool:
    return has_permission(user, PERM_FINANCE_VIEW)


def mask_project_dict(data: dict, user: User) -> dict:
    """Replace sensitive amounts with *** when the user lacks finance access."""
    if can_view_finance(user):
        return data
    result = dict(data)
    for field in SENSITIVE_PROJECT_FIELDS:
        if field in result and result[field] is not None:
            result[field] = MASK_VALUE
    return result


def mask_dashboard_dict(data: dict, user: User) -> dict:
    if can_view_finance(user):
        return data
    result = dict(data)
    for field in SENSITIVE_DASHBOARD_FIELDS:
        if field in result and result[field] is not None:
            result[field] = MASK_VALUE
    return result


def mask_finance_dict(data: dict, user: User) -> dict:
    """Mask amount fields on contract / cost / payment / receipt / invoice / summary."""
    if can_view_finance(user):
        return data
    result = dict(data)
    for field in SENSITIVE_FINANCE_FIELDS:
        if field in result and result[field] is not None:
            result[field] = MASK_VALUE
    return result
