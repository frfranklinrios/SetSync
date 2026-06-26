"""Persistência — financeiro da banda."""

from __future__ import annotations

import uuid

from config import app_now_str
from db import get_db
from studio_scheduling import BOOKING_CONFIRMADO


def list_band_events_for_finance(
    band_id: str,
    *,
    from_date: str,
    to_date: str,
) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT *
           FROM band_events
           WHERE band_id = ?
             AND substr(starts_at, 1, 10) >= ?
             AND substr(starts_at, 1, 10) <= ?
           ORDER BY starts_at DESC''',
        (band_id, from_date[:10], to_date[:10]),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def list_band_studio_bookings_for_finance(
    band_id: str,
    *,
    from_date: str,
    to_date: str,
) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT b.*, r.nome AS room_nome, r.preco_hora AS room_preco_hora,
                  s.nome AS studio_nome, s.preco_hora AS studio_preco_hora
           FROM studio_bookings b
           JOIN studio_rooms r ON r.id = b.room_id
           JOIN studios s ON s.id = r.studio_id
           WHERE b.band_id = ?
             AND b.status = ?
             AND b.data >= ? AND b.data <= ?
           ORDER BY b.data DESC, b.hora_inicio DESC''',
        (band_id, BOOKING_CONFIRMADO, from_date[:10], to_date[:10]),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def create_band_expense(
    band_id: str,
    *,
    data: str,
    descricao: str,
    valor: float,
    categoria: str,
    created_by_user_id: str,
) -> str:
    expense_id = str(uuid.uuid4())
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO band_expenses
           (id, band_id, data, descricao, valor, categoria, created_by_user_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            expense_id, band_id, data[:10], descricao[:200],
            valor, categoria[:40], created_by_user_id,
        ),
    )
    db.commit()
    db.close()
    return expense_id


def delete_band_expense(expense_id: str, band_id: str) -> bool:
    db = get_db()
    c = db.cursor()
    c.execute(
        'DELETE FROM band_expenses WHERE id = ? AND band_id = ?',
        (expense_id, band_id),
    )
    deleted = c.rowcount > 0
    db.commit()
    db.close()
    return deleted


def list_band_expenses(
    band_id: str,
    *,
    from_date: str,
    to_date: str,
) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT * FROM band_expenses
           WHERE band_id = ? AND data >= ? AND data <= ?
           ORDER BY data DESC, created_at DESC''',
        (band_id, from_date[:10], to_date[:10]),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows
