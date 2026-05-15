"""Helpers to read/write the app_settings key/value table."""
from __future__ import annotations

from typing import Any, Dict, Iterable

from sqlalchemy.orm import Session

from app.models.app_setting import AppSetting


def get_value(db: Session, key: str, default: str = "") -> str:
    row = db.get(AppSetting, key)
    return row.value if row and row.value is not None else default


def get_many(db: Session, keys: Iterable[str]) -> Dict[str, str]:
    rows = db.query(AppSetting).filter(AppSetting.key.in_(list(keys))).all()
    return {r.key: (r.value or "") for r in rows}


def set_value(db: Session, key: str, value: str | None) -> None:
    row = db.get(AppSetting, key)
    if row is None:
        row = AppSetting(key=key, value=value)
        db.add(row)
    else:
        row.value = value


def set_many(db: Session, kv: Dict[str, Any]) -> None:
    for k, v in kv.items():
        set_value(db, k, "" if v is None else str(v))
