"""Eventos de funil de produto (cadastro → ativação → pago)."""

from __future__ import annotations

import json
from typing import Any

from db import get_db

STEPS = (
    'signup',
    'primeira_banda',
    'primeira_cifra',
    'primeira_setlist',
    'play_mode',
    'primeiro_evento_agenda',
    'trial_iniciado',
    'assinatura_paga',
    'estudio_cadastrado',
    'estudio_reserva_confirmada',
)


def log_funnel_step(user_id: str | None, step: str, *, meta: dict | None = None) -> None:
    if not user_id or step not in STEPS:
        return
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT 1 FROM product_funnel_events WHERE user_id = ? AND step = ? LIMIT 1',
        (user_id, step),
    )
    if c.fetchone():
        db.close()
        return
    c.execute(
        '''INSERT INTO product_funnel_events (user_id, step, meta_json)
           VALUES (?, ?, ?)''',
        (user_id, step, json.dumps(meta or {}, ensure_ascii=False)),
    )
    db.commit()
    db.close()


def funnel_counts() -> dict[str, int]:
    db = get_db()
    c = db.cursor()
    out: dict[str, int] = {}
    for step in STEPS:
        c.execute('SELECT COUNT(*) AS n FROM product_funnel_events WHERE step = ?', (step,))
        row = c.fetchone()
        out[step] = int(row['n'] if row else 0)
    db.close()
    return out
