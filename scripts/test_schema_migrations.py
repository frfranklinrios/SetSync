#!/usr/bin/env python3
"""Garante que init_db aplica as mesmas migrações em SQLite e Postgres."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ['SECRET_KEY'] = 'test-secret-key-min-32-chars-long!!'
os.environ['FLASK_ENV'] = 'development'

# Colunas/tabelas que já causaram divergência SQLite vs Postgres
_REQUIRED = {
    'vouchers': {'destino', 'eh_vitalicio'},
    'cifras': {'play_notes', 'referencia_json', 'spotify_url'},
    'setlist_cifras': {'play_notes', 'vocalist_id'},
    'studio_bookings': {'valor_cobrado', 'pago_em', 'finance_notes'},
    'studio_rooms': {'preco_hora'},
    'studio_subscriptions': {'data_proxima_cobranca', 'trial_fim'},
}
_REQUIRED_TABLES = frozenset({
    'studio_voucher_usos',
    'studio_expenses',
    'band_expenses',
    'band_vocalists',
})


class SchemaMigrationsTest(unittest.TestCase):
    def _assert_schema(self, label: str) -> None:
        from database import IS_POSTGRES, table_columns
        from db import get_db, init_db

        self.assertTrue(IS_POSTGRES if label == 'postgres' else not IS_POSTGRES, label)
        db = get_db()
        c = db.cursor()
        for table, cols in _REQUIRED.items():
            have = set(table_columns(c, table))
            missing = cols - have
            self.assertFalse(missing, f'{label}: faltam {table}.{missing}')
        if IS_POSTGRES:
            c.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            )
            names = {r['tablename'] for r in c.fetchall()}
        else:
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            names = {r['name'] for r in c.fetchall()}
        missing_tables = _REQUIRED_TABLES - names
        self.assertFalse(missing_tables, f'{label}: tabelas ausentes {missing_tables}')
        db.close()

    def test_sqlite_migrations(self):
        os.environ['DATABASE_URL'] = f'sqlite:///{tempfile.mkdtemp()}/test.db'
        if 'database' in sys.modules:
            del sys.modules['database']
        if 'db' in sys.modules:
            del sys.modules['db']
        from db import init_db

        init_db()
        self._assert_schema('sqlite')

    def test_postgres_migrations_smoke(self):
        """Só roda se DATABASE_URL apontar para Postgres (ex.: container prod)."""
        url = os.environ.get('DATABASE_URL', '')
        if not url.startswith('postgres'):
            self.skipTest('DATABASE_URL não é Postgres')
        if 'database' in sys.modules:
            del sys.modules['database']
        if 'db' in sys.modules:
            del sys.modules['db']
        from db import init_db

        init_db()
        self._assert_schema('postgres')


if __name__ == '__main__':
    unittest.main()
