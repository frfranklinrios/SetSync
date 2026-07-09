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

FUNNEL_LABELS: dict[str, str] = {
    'signup': 'Cadastros',
    'primeira_banda': '1ª banda',
    'primeira_cifra': '1ª música',
    'primeira_setlist': '1ª setlist',
    'play_mode': 'Modo Tocar',
    'primeiro_evento_agenda': '1º evento',
    'trial_iniciado': 'Trial Pro',
    'assinatura_paga': 'Assinatura paga',
    'estudio_cadastrado': 'Estúdio cadastrado',
    'estudio_reserva_confirmada': 'Reserva confirmada',
}

# Funil principal de ativação (ordem de exibição no painel admin)
ACTIVATION_FUNNEL = (
    'primeira_banda',
    'primeira_cifra',
    'primeira_setlist',
    'play_mode',
    'trial_iniciado',
    'assinatura_paga',
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


def funnel_activation_rows(*, users_total: int) -> list[dict[str, Any]]:
    """Linhas do funil de ativação com rótulos PT e % sobre etapa anterior."""
    counts = funnel_counts()
    baseline = max(users_total, counts.get('signup', 0), 1)
    rows: list[dict[str, Any]] = []
    prev = baseline
    for step in ACTIVATION_FUNNEL:
        n = counts.get(step, 0)
        rows.append({
            'step': step,
            'label': FUNNEL_LABELS.get(step, step),
            'count': n,
            'pct_of_users': round(100 * n / baseline) if baseline else 0,
            'pct_of_prev': round(100 * n / prev) if prev else 0,
        })
        if n > 0:
            prev = n
    return rows
