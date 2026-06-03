"""Conexão SQLite ou PostgreSQL (DATABASE_URL)."""
from __future__ import annotations

import os
import re
import sqlite3
from typing import Any

DATABASE_URL = (os.getenv('DATABASE_URL') or 'sqlite:///data/banda.db').strip()
IS_POSTGRES = DATABASE_URL.startswith(('postgresql://', 'postgres://'))


def _sqlite_path() -> str:
    if DATABASE_URL.startswith('sqlite:///'):
        rel = DATABASE_URL[len('sqlite:///'):]
        if os.path.isabs(rel):
            return rel
        return os.path.normpath(os.path.join(os.path.dirname(__file__), rel))
    return os.path.join(os.path.dirname(__file__), 'data', 'banda.db')


SQLITE_PATH = _sqlite_path()

if IS_POSTGRES:
    import psycopg2
    import psycopg2.extras

    IntegrityError = psycopg2.IntegrityError
else:
    IntegrityError = sqlite3.IntegrityError


def _adapt_sql(sql: str) -> str:
    if not IS_POSTGRES:
        return sql
    s = sql.replace('?', '%s')
    s = s.replace("datetime('now')", 'CURRENT_TIMESTAMP')
    return s


def _row_to_dict(row: Any) -> dict | None:
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    return dict(row)


class CompatCursor:
    """Cursor com placeholders ? e helpers de linha única."""

    def __init__(self, raw, *, is_postgres: bool):
        self._raw = raw
        self._is_postgres = is_postgres
        self._last_insert_id: int | None = None

    def execute(self, sql: str, params: tuple | list = ()):
        sql = _adapt_sql(sql)
        if self._is_postgres and 'INSERT OR IGNORE' in sql.upper():
            sql, params = self._pg_insert_or_ignore(sql, params)
        elif self._is_postgres and 'INSERT OR REPLACE' in sql.upper():
            sql, params = self._pg_insert_or_replace(sql, params)
        self._raw.execute(sql, params)
        return self

    @staticmethod
    def _pg_insert_or_ignore(sql: str, params: tuple | list):
        sql = re.sub(r'INSERT\s+OR\s+IGNORE\s+INTO', 'INSERT INTO', sql, flags=re.I)
        if 'cifra_vocalist_transpose' in sql.lower():
            sql = sql.rstrip().rstrip(';') + ' ON CONFLICT (cifra_id, vocalist_id) DO NOTHING'
        return sql, params

    @staticmethod
    def _pg_insert_or_replace(sql: str, params: tuple | list):
        sql = re.sub(r'INSERT\s+OR\s+REPLACE\s+INTO', 'INSERT INTO', sql, flags=re.I)
        if 'cifra_vocalist_transpose' in sql.lower():
            sql = (
                sql.rstrip().rstrip(';')
                + ' ON CONFLICT (cifra_id, vocalist_id) DO UPDATE SET '
                'transpose_semitones = EXCLUDED.transpose_semitones'
            )
        return sql, params

    def executemany(self, sql: str, params_seq):
        return self._raw.executemany(_adapt_sql(sql), params_seq)

    def fetchone(self):
        return _row_to_dict(self._raw.fetchone())

    def fetchall(self):
        return [_row_to_dict(r) for r in self._raw.fetchall()]

    @property
    def lastrowid(self) -> int | None:
        if self._last_insert_id is not None:
            return self._last_insert_id
        return getattr(self._raw, 'lastrowid', None)

    @property
    def rowcount(self) -> int:
        return self._raw.rowcount

    @property
    def connection(self):
        return self._raw.connection


class CompatConnection:
    def __init__(self, raw, *, is_postgres: bool):
        self._raw = raw
        self._is_postgres = is_postgres

    def cursor(self) -> CompatCursor:
        if self._is_postgres:
            return CompatCursor(
                self._raw.cursor(cursor_factory=psycopg2.extras.RealDictCursor),
                is_postgres=True,
            )
        cur = self._raw.cursor()
        self._raw.row_factory = sqlite3.Row
        return CompatCursor(cur, is_postgres=False)

    def commit(self):
        self._raw.commit()

    def rollback(self):
        self._raw.rollback()

    def close(self):
        self._raw.close()

    def executescript(self, script: str) -> None:
        if self._is_postgres:
            for stmt in script.split(';'):
                stmt = stmt.strip()
                if stmt:
                    self.cursor().execute(stmt)
        else:
            self._raw.executescript(script)


def get_db() -> CompatConnection:
    if IS_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return CompatConnection(conn, is_postgres=True)
    os.makedirs(os.path.dirname(SQLITE_PATH) or '.', exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return CompatConnection(conn, is_postgres=False)


def table_columns(cursor: CompatCursor, table: str) -> list[str]:
    if IS_POSTGRES:
        cursor.execute(
            '''SELECT column_name FROM information_schema.columns
               WHERE table_schema = 'public' AND table_name = %s
               ORDER BY ordinal_position''',
            (table,),
        )
        return [r['column_name'] for r in cursor.fetchall()]
    cursor.execute(f'PRAGMA table_info({table})')
    return [row['name'] for row in cursor.fetchall()]


def table_exists(cursor: CompatCursor, table: str) -> bool:
    if IS_POSTGRES:
        cursor.execute(
            '''SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'public' AND table_name = %s''',
            (table,),
        )
        return cursor.fetchone() is not None
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    )
    return cursor.fetchone() is not None


def add_column_if_missing(cursor: CompatCursor, table: str, col: str, typedef: str) -> None:
    cols = set(table_columns(cursor, table))
    if col in cols:
        return
    if IS_POSTGRES:
        cursor.execute(f'ALTER TABLE {table} ADD COLUMN {col} {typedef}')
    else:
        cursor.execute(f'ALTER TABLE {table} ADD COLUMN {col} {typedef}')
    cursor.connection.commit()
