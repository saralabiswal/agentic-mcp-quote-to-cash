# Author: Sarala Biswal
"""Local bootstrap helper for validating seed data and initializing demo storage."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from seed_data.loader import load_json


def main() -> None:
    accounts = load_json("accounts.json")
    db_path = Path("audit.db")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seed_accounts (
                account_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO seed_accounts(account_id, payload)
            VALUES (?, ?)
            ON CONFLICT(account_id) DO UPDATE SET payload=excluded.payload
            """,
            [(account_id, json.dumps(payload)) for account_id, payload in accounts.items()],
        )
    print(f"Loaded {len(accounts)} seed accounts into {db_path} for demo mode.")


if __name__ == "__main__":
    main()
