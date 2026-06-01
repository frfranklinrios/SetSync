#!/usr/bin/env python3
"""Lista usuários do SQLite em uso (útil para comparar local vs VPS)."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import DB_PATH, get_all_users, init_db, is_superadmin


def main() -> int:
    init_db()
    users = get_all_users()
    print(f'Banco: {DB_PATH}')
    print(f'Usuários: {len(users)}\n')
    for u in users:
        sa = ' [admin .env]' if is_superadmin(u['id']) else ''
        pwd = 'senha' if u.get('password_hash') else 'só Google'
        print(f"  {u['username']:20} {u.get('email') or '—':30} {pwd}{sa}")
    if not users:
        print('  (nenhum — registre-se em /auth/register ou copie banda.db do VPS)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
