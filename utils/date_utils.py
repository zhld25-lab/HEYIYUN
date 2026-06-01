from __future__ import annotations

from datetime import date, datetime, timedelta


def today() -> date:
    return date.today()


def days_between(start, end) -> int:
    if isinstance(start, str):
        start = datetime.fromisoformat(start).date()
    if isinstance(end, str):
        end = datetime.fromisoformat(end).date()
    if isinstance(start, datetime):
        start = start.date()
    if isinstance(end, datetime):
        end = end.date()
    return (end - start).days


def add_days(value, days: int) -> date:
    if isinstance(value, str):
        value = datetime.fromisoformat(value).date()
    if isinstance(value, datetime):
        value = value.date()
    return value + timedelta(days=days)

