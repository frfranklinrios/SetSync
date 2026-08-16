"""Eventos de funil de produto (cadastro → ativação → pago)."""

from __future__ import annotations

import json
from typing import Any

from db import get_db

STEPS = (
    'signup',
    'primeira_banda',
    'primeira_cifra',
    'primeira_cifra_real',
    'primeira_setlist',
    'play_mode',
    'play_mode_real',
    'primeiro_evento_agenda',
    'trial_iniciado',
    'assinatura_paga',
    'estudio_cadastrado',
    'estudio_reserva_confirmada',
)

FUNNEL_LABELS: dict[str, str] = {
    'signup': 'Cadastros',
    'primeira_banda': '1ª banda',
    'primeira_cifra': '1ª música (inclui demo)',
    'primeira_cifra_real': '1ª cifra real',
    'primeira_setlist': '1ª setlist',
    'play_mode': 'Modo Tocar (inclui demo)',
    'play_mode_real': 'Tocou cifra real',
    'primeiro_evento_agenda': '1º evento',
    'trial_iniciado': 'Trial Pro',
    'assinatura_paga': 'Assinatura paga',
    'estudio_cadastrado': 'Estúdio cadastrado',
    'estudio_reserva_confirmada': 'Reserva confirmada',
}

# Ativação de verdade: cifra que não é demo + palco dessa cifra
ACTIVATION_FUNNEL = (
    'signup',
    'primeira_cifra_real',
    'play_mode_real',
    'primeira_banda',
    'primeira_setlist',
    'trial_iniciado',
    'assinatura_paga',
)


def log_funnel_step(user_id: str | None, step: str, *, meta: dict | None = None) -> bool:
    """Registra step uma vez por usuário. Retorna True se inseriu."""
    if not user_id or step not in STEPS:
        return False
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT 1 FROM product_funnel_events WHERE user_id = ? AND step = ? LIMIT 1',
        (user_id, step),
    )
    if c.fetchone():
        db.close()
        return False
    c.execute(
        '''INSERT INTO product_funnel_events (user_id, step, meta_json)
           VALUES (?, ?, ?)''',
        (user_id, step, json.dumps(meta or {}, ensure_ascii=False)),
    )
    db.commit()
    db.close()
    return True


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


def get_user_funnel_steps(user_id: str) -> dict[str, Any]:
    """Checklist de ativação de um usuário (ficha admin)."""
    if not user_id:
        return {'done': set(), 'steps': [], 'next_step': None}
    db = get_db()
    c = db.cursor()
    c.execute(
        'SELECT step FROM product_funnel_events WHERE user_id = ?',
        (user_id,),
    )
    done = {str(r['step']) for r in c.fetchall()}
    db.close()
    steps = []
    next_step = None
    for step in ACTIVATION_FUNNEL:
        ok = step in done
        steps.append({
            'step': step,
            'label': FUNNEL_LABELS.get(step, step),
            'done': ok,
        })
        if not ok and next_step is None:
            next_step = step
    return {'done': done, 'steps': steps, 'next_step': next_step}


_backfill_ran = False


def backfill_product_funnel(*, force: bool = False) -> dict[str, int]:
    """
    Preenche eventos faltantes a partir do banco (idempotente via log_funnel_step).
    """
    global _backfill_ran
    if _backfill_ran and not force:
        return {'skipped': 1}
    _backfill_ran = True

    meta = {'source': 'backfill'}
    inserted: dict[str, int] = {s: 0 for s in STEPS}

    def _bump(step: str, ok: bool) -> None:
        if ok:
            inserted[step] += 1

    db = get_db()
    c = db.cursor()
    c.execute('SELECT id FROM users')
    user_ids = [r['id'] for r in c.fetchall()]
    c.execute('SELECT id FROM users WHERE COALESCE(play_mode_used, 0) = 1')
    play_ids = [r['id'] for r in c.fetchall()]
    c.execute(
        '''SELECT DISTINCT owner_user_id AS uid FROM cifras
           WHERE band_id IS NULL AND owner_user_id IS NOT NULL'''
    )
    personal_cifra = [r['uid'] for r in c.fetchall()]
    c.execute(
        '''SELECT DISTINCT b.owner_id AS uid
           FROM cifras cif JOIN bands b ON b.id = cif.band_id
           WHERE b.owner_id IS NOT NULL'''
    )
    band_cifra = [r['uid'] for r in c.fetchall()]
    c.execute('SELECT DISTINCT owner_id AS uid FROM bands WHERE owner_id IS NOT NULL')
    band_owners = [r['uid'] for r in c.fetchall()]
    c.execute(
        '''SELECT DISTINCT b.owner_id AS uid
           FROM setlists s JOIN bands b ON b.id = s.band_id
           WHERE b.owner_id IS NOT NULL'''
    )
    setlist_owners = [r['uid'] for r in c.fetchall()]
    c.execute(
        '''SELECT DISTINCT b.owner_id AS uid
           FROM assinaturas a JOIN bands b ON b.id = a.banda_id
           WHERE a.trial_usado = 1 AND b.owner_id IS NOT NULL'''
    )
    trial_owners = [r['uid'] for r in c.fetchall()]
    c.execute(
        '''SELECT DISTINCT b.owner_id AS uid, a.plano
           FROM assinaturas a JOIN bands b ON b.id = a.banda_id
           WHERE a.status IN ('ativa', 'voucher')
             AND a.plano IN ('individual', 'pro', 'worship')
             AND b.owner_id IS NOT NULL'''
    )
    paid_rows = [(r['uid'], r['plano']) for r in c.fetchall()]
    agenda_owners: list = []
    try:
        c.execute(
            '''SELECT DISTINCT b.owner_id AS uid
               FROM band_events e JOIN bands b ON b.id = e.band_id
               WHERE b.owner_id IS NOT NULL'''
        )
        agenda_owners = [r['uid'] for r in c.fetchall()]
    except Exception:
        pass
    studio_owners: list = []
    try:
        c.execute('SELECT DISTINCT owner_user_id AS uid FROM studios WHERE owner_user_id IS NOT NULL')
        studio_owners = [r['uid'] for r in c.fetchall()]
    except Exception:
        pass
    real_personal: list = []
    try:
        c.execute(
            '''SELECT DISTINCT owner_user_id AS uid FROM cifras
               WHERE band_id IS NULL AND owner_user_id IS NOT NULL
                 AND COALESCE(referencia_json, '') NOT LIKE '%"is_demo": true%'
                 AND COALESCE(referencia_json, '') NOT LIKE '%"is_demo":true%' '''
        )
        real_personal = [r['uid'] for r in c.fetchall()]
    except Exception:
        real_personal = []
    db.close()

    for uid in user_ids:
        _bump('signup', log_funnel_step(uid, 'signup', meta=meta))
    for uid in play_ids:
        _bump('play_mode', log_funnel_step(uid, 'play_mode', meta=meta))
    for uid in set(personal_cifra + band_cifra):
        _bump('primeira_cifra', log_funnel_step(uid, 'primeira_cifra', meta=meta))
    for uid in set(real_personal + band_cifra):
        _bump('primeira_cifra_real', log_funnel_step(uid, 'primeira_cifra_real', meta=meta))
    for uid in band_owners:
        _bump('primeira_banda', log_funnel_step(uid, 'primeira_banda', meta=meta))
    for uid in setlist_owners:
        _bump('primeira_setlist', log_funnel_step(uid, 'primeira_setlist', meta=meta))
    for uid in trial_owners:
        _bump('trial_iniciado', log_funnel_step(uid, 'trial_iniciado', meta=meta))
    for uid, plano in paid_rows:
        _bump('assinatura_paga', log_funnel_step(uid, 'assinatura_paga', meta={**meta, 'plano': plano}))
    for uid in agenda_owners:
        _bump('primeiro_evento_agenda', log_funnel_step(uid, 'primeiro_evento_agenda', meta=meta))
    for uid in studio_owners:
        _bump('estudio_cadastrado', log_funnel_step(uid, 'estudio_cadastrado', meta=meta))

    return inserted
