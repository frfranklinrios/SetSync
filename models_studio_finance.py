"""Persistência — financeiro do estúdio."""

from __future__ import annotations

import uuid

from config import app_now_str
from db import get_db
from studio_scheduling import BOOKING_CONFIRMADO


def list_studio_bookings_for_finance(
    studio_id: str,
    *,
    from_date: str,
    to_date: str,
) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT b.*, r.nome AS room_nome, r.preco_hora AS room_preco_hora, bd.name AS band_name
           FROM studio_bookings b
           JOIN studio_rooms r ON r.id = b.room_id
           LEFT JOIN bands bd ON bd.id = b.band_id
           WHERE r.studio_id = ?
             AND b.status = ?
             AND b.data >= ? AND b.data <= ?
           ORDER BY b.data DESC, b.hora_inicio DESC''',
        (studio_id, BOOKING_CONFIRMADO, from_date[:10], to_date[:10]),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def update_booking_finance(
    booking_id: str,
    *,
    valor_cobrado: float | None = None,
    clear_valor: bool = False,
    paid: bool | None = None,
    finance_notes: str | None = None,
) -> None:
    db = get_db()
    c = db.cursor()
    sets: list[str] = []
    params: list = []

    if clear_valor:
        sets.append('valor_cobrado = NULL')
    elif valor_cobrado is not None:
        sets.append('valor_cobrado = ?')
        params.append(valor_cobrado)

    if paid is True:
        sets.append('pago_em = ?')
        params.append(app_now_str())
    elif paid is False:
        sets.append('pago_em = NULL')

    if finance_notes is not None:
        sets.append('finance_notes = ?')
        params.append(finance_notes[:500] if finance_notes else None)

    if not sets:
        db.close()
        return

    params.append(booking_id)
    c.execute(
        f'UPDATE studio_bookings SET {", ".join(sets)} WHERE id = ?',
        params,
    )
    db.commit()
    db.close()


def create_studio_expense(
    studio_id: str,
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
        '''INSERT INTO studio_expenses
           (id, studio_id, data, descricao, valor, categoria, created_by_user_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (
            expense_id, studio_id, data[:10], descricao[:200],
            valor, categoria[:40], created_by_user_id,
        ),
    )
    db.commit()
    db.close()
    return expense_id


def delete_studio_expense(expense_id: str, studio_id: str) -> bool:
    db = get_db()
    c = db.cursor()
    c.execute(
        'DELETE FROM studio_expenses WHERE id = ? AND studio_id = ?',
        (expense_id, studio_id),
    )
    deleted = c.rowcount > 0
    db.commit()
    db.close()
    return deleted


def list_studio_expenses(
    studio_id: str,
    *,
    from_date: str,
    to_date: str,
) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT * FROM studio_expenses
           WHERE studio_id = ? AND data >= ? AND data <= ?
           ORDER BY data DESC, created_at DESC''',
        (studio_id, from_date[:10], to_date[:10]),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows
