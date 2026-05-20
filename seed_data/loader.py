# Author: Sarala Biswal
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, TypeVar, cast

ROOT = Path(__file__).resolve().parent
JsonDict = dict[str, Any]
T = TypeVar("T")


def load_json(name: str) -> JsonDict:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return cast(JsonDict, json.load(handle))


def day(offset: int | None) -> date | None:
    if offset is None:
        return None
    return date.today() + timedelta(days=offset)


def moment(offset: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=offset)


def require_account(data: dict[str, T], account_id: str) -> T:
    try:
        return data[account_id]
    except KeyError as exc:
        raise KeyError(f"Unknown seed account_id: {account_id}") from exc
