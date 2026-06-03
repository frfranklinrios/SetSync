#!/usr/bin/env python3
"""Copia dados de SQLite (data/banda.db) para PostgreSQL (DATABASE_URL)."""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TABLE_ORDER = [
    'users',
    'bands',
    'band_members',
    'cifras',
    'band_vocalists',
    'setlists',
    'setlist_cifras',
    'cifra_vocalist_transpose',
    'assinaturas',
    'vouchers',
    'voucher_usos',
    'notifications',
]


def _sqlite_path(arg: str | None) -> str:
    if arg:
        return arg
    url = (os.getenv('SQLITE_SOURCE') or 'sqlite:///data/banda.db').strip()
    if url.startswith('sqlite:///'):
        rel = url[len('sqlite:///'):]
        if os.path.isabs(rel):
            return rel
        return str(ROOT / rel)
    return str(ROOT / 'data' / 'banda.db')


def main() -> int:
    parser = argparse.ArgumentParser(description='Migra SQLite → PostgreSQL')
    parser.add_argument('--sqlite', help='Caminho do arquivo .db (padrão: data/banda.db)')
    parser.add_argument('--dry-run', action='store_true', help='Só lista tabelas/contagens')
    args = parser.parse_args()

    pg_url = (os.getenv('DATABASE_URL') or '').strip()
    if not pg_url.startswith(('postgresql://', 'postgres://')):
        print('Defina DATABASE_URL=postgresql://user:pass@host:5432/db', file=sys.stderr)
        return 1

    sqlite_path = _sqlite_path(args.sqlite)
    if not os.path.isfile(sqlite_path):
        print(f'SQLite não encontrado: {sqlite_path}', file=sys.stderr)
        return 1

    src = sqlite3.connect(sqlite_path)
    src.row_factory = sqlite3.Row

    os.environ['DATABASE_URL'] = pg_url
    for mod in list(sys.modules):
        if mod in ('database', 'db'):
            del sys.modules[mod]
    from database import IS_POSTGRES, get_db, table_columns
    from db import init_db

    if not IS_POSTGRES:
        print('DATABASE_URL deve ser PostgreSQL', file=sys.stderr)
        return 1

    print(f'Origem: {sqlite_path}')
    print(f'Destino: {pg_url.split("@")[-1] if "@" in pg_url else pg_url}')

    counts = {}
    for table in TABLE_ORDER:
        try:
            n = src.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        except sqlite3.OperationalError:
            n = 0
        counts[table] = n
        print(f'  {table}: {n} linhas')

    if args.dry_run:
        return 0

    init_db()
    dst = get_db()
    c = dst.cursor()
    c.execute(
        'TRUNCATE notifications, voucher_usos, vouchers, assinaturas, '
        'cifra_vocalist_transpose, setlist_cifras, setlists, band_vocalists, '
        'cifras, band_members, bands, users RESTART IDENTITY CASCADE'
    )
    dst.commit()

    for table in TABLE_ORDER:
        if counts.get(table, 0) == 0:
            continue
        rows = src.execute(f'SELECT * FROM {table}').fetchall()
        if not rows:
            continue
        pg_cols = set(table_columns(c, table))
        cols = [k for k in rows[0].keys() if k in pg_cols]
        skipped = [k for k in rows[0].keys() if k not in pg_cols]
        if skipped:
            print(f'  {table}: ignorando colunas extras {skipped}')
        if not cols:
            print(f'  {table}: pulado (nenhuma coluna em comum)')
            continue
        col_list = ', '.join(cols)
        placeholders = ', '.join(['?'] * len(cols))
        sql = f'INSERT INTO {table} ({col_list}) VALUES ({placeholders})'
        imported = 0
        for row in rows:
            data = {c: row[c] for c in cols}
            if table == 'assinaturas' and not (data.get('banda_id') or '').strip():
                print(f'  {table}: ignorando assinatura sem banda_id ({data.get("id")})')
                continue
            c.execute(sql, tuple(data[c] for c in cols))
            imported += 1
        dst.commit()
        print(f'importado {table}: {imported}' + (f' (de {len(rows)})' if imported != len(rows) else ''))

    if counts.get('setlists', 0):
        c.execute(
            "SELECT setval(pg_get_serial_sequence('setlists', 'id'), "
            'COALESCE((SELECT MAX(id) FROM setlists), 1), true)'
        )
        dst.commit()

    dst.close()
    src.close()
    print('Migração concluída.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
