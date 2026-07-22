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
    start_at = f'{from_date[:10]} 00:00:00'
    end_at = f'{to_date[:10]} 23:59:59'
    c.execute(
        '''SELECT *
           FROM band_events
           WHERE band_id = ?
             AND starts_at >= ?
             AND starts_at <= ?
           ORDER BY starts_at DESC''',
        (band_id, start_at, end_at),
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
    event_id: str | None = None,
) -> str:
    expense_id = str(uuid.uuid4())
    db = get_db()
    c = db.cursor()
    c.execute(
        '''INSERT INTO band_expenses
           (id, band_id, data, descricao, valor, categoria, created_by_user_id, event_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            expense_id, band_id, data[:10], descricao[:200],
            valor, categoria[:40], created_by_user_id, event_id or None,
        ),
    )
    db.commit()
    db.close()
    return expense_id


def list_event_expenses(event_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT * FROM band_expenses
           WHERE event_id = ?
           ORDER BY created_at ASC''',
        (event_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def replace_event_expenses(
    band_id: str,
    event_id: str,
    *,
    data: str,
    items: list[dict],
    created_by_user_id: str,
) -> list[dict]:
    """Substitui despesas ligadas ao evento (fechamento de noite)."""
    db = get_db()
    c = db.cursor()
    c.execute(
        'DELETE FROM band_expenses WHERE event_id = ? AND band_id = ?',
        (event_id, band_id),
    )
    saved: list[dict] = []
    for raw in items:
        desc = (raw.get('descricao') or '').strip()[:200]
        try:
            valor = max(0.0, float(raw.get('valor') or 0))
        except (TypeError, ValueError):
            valor = 0.0
        if not desc or valor <= 0:
            continue
        categoria = (raw.get('categoria') or 'outros').strip()[:40] or 'outros'
        expense_id = str(uuid.uuid4())
        c.execute(
            '''INSERT INTO band_expenses
               (id, band_id, data, descricao, valor, categoria, created_by_user_id, event_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                expense_id, band_id, data[:10], desc, valor,
                categoria, created_by_user_id, event_id,
            ),
        )
        saved.append({
            'id': expense_id,
            'descricao': desc,
            'valor': valor,
            'categoria': categoria,
            'event_id': event_id,
        })
    db.commit()
    db.close()
    return saved


def list_event_fee_lines(event_id: str) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT * FROM band_event_fee_lines
           WHERE event_id = ?
           ORDER BY sort_order ASC, created_at ASC''',
        (event_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def replace_event_fee_lines(event_id: str, lines: list[dict]) -> list[dict]:
    """Grava snapshot da liquidação (quem recebe o quê)."""
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM band_event_fee_lines WHERE event_id = ?', (event_id,))
    saved: list[dict] = []
    for i, raw in enumerate(lines):
        kind = (raw.get('kind') or 'share').strip().lower()
        if kind not in ('fixed', 'share'):
            kind = 'share'
        try:
            amount = max(0.0, float(raw.get('amount') or 0))
        except (TypeError, ValueError):
            amount = 0.0
        name = (raw.get('name') or raw.get('display_name') or '—').strip()[:120] or '—'
        line_id = str(uuid.uuid4())
        c.execute(
            '''INSERT INTO band_event_fee_lines
               (id, event_id, user_id, guest_id, display_name, kind, amount, sort_order)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                line_id,
                event_id,
                raw.get('user_id') or None,
                raw.get('guest_id') or None,
                name,
                kind,
                amount,
                i,
            ),
        )
        saved.append({
            'id': line_id,
            'event_id': event_id,
            'user_id': raw.get('user_id'),
            'guest_id': raw.get('guest_id'),
            'display_name': name,
            'kind': kind,
            'amount': amount,
            'sort_order': i,
        })
    db.commit()
    db.close()
    return saved


def clear_event_fee_lines(event_id: str) -> None:
    db = get_db()
    c = db.cursor()
    c.execute('DELETE FROM band_event_fee_lines WHERE event_id = ?', (event_id,))
    db.commit()
    db.close()


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


def aggregate_platform_band_finance(*, from_date: str, to_date: str) -> dict:
    """Soma plataforma (todas as bandas) — sem lista de eventos/despesas.

    Retorna apenas montantes e contagens para a visão do master.
    Contas/bandas demo (showcase) são excluídas dos totais.
    """
    from demo_accounts import demo_band_ids
    from event_fees import _money

    skip_bands = demo_band_ids()
    db = get_db()
    c = db.cursor()
    start_at = f'{from_date[:10]} 00:00:00'
    end_at = f'{to_date[:10]} 23:59:59'
    c.execute(
        '''SELECT band_id, fee_total, fee_transport_discount,
                  fee_equipment_discount, fee_settled_at
           FROM band_events
           WHERE starts_at >= ? AND starts_at <= ?
             AND fee_total IS NOT NULL AND CAST(fee_total AS REAL) > 0''',
        (start_at, end_at),
    )
    events = [dict(r) for r in c.fetchall()]
    if skip_bands:
        ph = ','.join('?' for _ in skip_bands)
        c.execute(
            f'''SELECT COALESCE(SUM(valor), 0) AS total
                FROM band_expenses
                WHERE data >= ? AND data <= ?
                  AND band_id NOT IN ({ph})''',
            [from_date[:10], to_date[:10], *list(skip_bands)],
        )
    else:
        c.execute(
            '''SELECT COALESCE(SUM(valor), 0) AS total
               FROM band_expenses
               WHERE data >= ? AND data <= ?''',
            (from_date[:10], to_date[:10]),
        )
    exp_row = c.fetchone()
    db.close()

    receita = 0.0
    recebido = 0.0
    bands = set()
    shows = 0
    demo_skipped_shows = 0
    for e in events:
        bid = e.get('band_id')
        if bid and str(bid) in skip_bands:
            demo_skipped_shows += 1
            continue
        total = _money(e.get('fee_total'))
        transport = _money(e.get('fee_transport_discount'))
        equipment = _money(e.get('fee_equipment_discount'))
        net = max(0.0, total - transport - equipment) if total > 0 else 0.0
        if net <= 0:
            continue
        bands.add(bid)
        receita += net
        shows += 1
        if e.get('fee_settled_at'):
            recebido += net

    despesas = float((exp_row['total'] if exp_row else 0) or 0)
    return {
        'bandas_com_movimento': len(bands),
        'shows_com_cache': shows,
        'receita_confirmada': round(receita, 2),
        'recebido': round(recebido, 2),
        'a_receber': round(receita - recebido, 2),
        'despesas': round(despesas, 2),
        'demo_excluded_shows': demo_skipped_shows,
        'demo_excluded_bands': len(skip_bands),
    }


def list_member_fee_events(
    user_id: str,
    *,
    from_date: str,
    to_date: str,
    band_id: str | None = None,
) -> list[dict]:
    """Shows com cachê das bandas do músico (para painel pessoal)."""
    db = get_db()
    c = db.cursor()
    start_at = f'{from_date[:10]} 00:00:00'
    end_at = f'{to_date[:10]} 23:59:59'
    params: list = [start_at, end_at, user_id, user_id]
    band_filter = ''
    if band_id:
        band_filter = 'AND e.band_id = ?'
        params.append(band_id)
    c.execute(
        f'''SELECT e.*, b.name AS band_name
            FROM band_events e
            JOIN bands b ON b.id = e.band_id
            WHERE e.event_type = 'show'
              AND COALESCE(e.fee_total, 0) > 0
              AND e.starts_at >= ?
              AND e.starts_at <= ?
              AND (
                    EXISTS (
                        SELECT 1 FROM band_members bm
                        WHERE bm.band_id = e.band_id AND bm.user_id = ?
                    )
                    OR b.owner_id = ?
                  )
              {band_filter}
            ORDER BY e.starts_at DESC''',
        params,
    )
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows
