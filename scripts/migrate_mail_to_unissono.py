#!/usr/bin/env python3
"""Migra caixas/histórico de @setsync.com.br → @unissono.app.

Uso (container mail ou web com volume compartilhado):
    python3 scripts/migrate_mail_to_unissono.py
"""

from __future__ import annotations

import os
import sqlite3
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from datetime import UTC

from mail_server.config import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    DATABASE_PATH,
    DOMAIN,
    canonical_mailbox,
)
from mail_server.server.storage import _hash_password


def migrate(db_path: str = DATABASE_PATH) -> dict:
    stats = {
        "emails_moved": 0,
        "users_renamed": 0,
        "users_merged": 0,
        "password_synced": 0,
    }
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        # 1) Reescreve owner_email legado → canônico.
        rows = conn.execute(
            "SELECT DISTINCT owner_email FROM emails WHERE owner_email LIKE ?",
            ("%@setsync.com.br",),
        ).fetchall()
        for row in rows:
            old = (row["owner_email"] or "").lower()
            new = canonical_mailbox(old)
            if old == new:
                continue
            cur = conn.execute(
                "UPDATE emails SET owner_email = ? WHERE owner_email = ?",
                (new, old),
            )
            stats["emails_moved"] += cur.rowcount

        # 2) Usuários: renomeia ou mescla com caixa canônica.
        users = conn.execute(
            "SELECT id, email, password_hash, is_admin FROM users WHERE email LIKE ?",
            ("%@setsync.com.br",),
        ).fetchall()
        for u in users:
            old = u["email"].lower()
            new = canonical_mailbox(old)
            if old == new:
                continue
            existing = conn.execute(
                "SELECT id, is_admin FROM users WHERE email = ?", (new,)
            ).fetchone()
            if existing:
                # Mantém a canônica; promove admin se legado era admin; remove legado.
                if u["is_admin"] and not existing["is_admin"]:
                    conn.execute(
                        "UPDATE users SET is_admin = 1 WHERE id = ?", (existing["id"],)
                    )
                conn.execute("DELETE FROM users WHERE id = ?", (u["id"],))
                stats["users_merged"] += 1
            else:
                conn.execute("UPDATE users SET email = ? WHERE id = ?", (new, u["id"]))
                stats["users_renamed"] += 1

        # 3) Garante contato@unissono.app com a senha do .env (MAIL_PASSWORD).
        admin = (ADMIN_EMAIL or f"contato@{DOMAIN}").lower()
        if ADMIN_PASSWORD:
            row = conn.execute(
                "SELECT id FROM users WHERE email = ?", (admin,)
            ).fetchone()
            hashed = _hash_password(ADMIN_PASSWORD)
            if row:
                conn.execute(
                    "UPDATE users SET password_hash = ?, is_admin = 1 WHERE id = ?",
                    (hashed, row["id"]),
                )
            else:
                from datetime import datetime

                conn.execute(
                    "INSERT INTO users (email, password_hash, is_admin, created_at) VALUES (?, ?, 1, ?)",
                    (admin, hashed, datetime.now(UTC).isoformat()),
                )
            stats["password_synced"] += 1

        conn.commit()
    finally:
        conn.close()
    return stats


def main() -> int:
    print(f"DB: {DATABASE_PATH}")
    print(f"Domínio canônico: {DOMAIN}")
    print(f"Admin: {ADMIN_EMAIL}")
    stats = migrate()
    print("OK:", stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
