"""Métricas de retenção para o painel admin (WAU, ativação D7, NPS, churn)."""

from __future__ import annotations

import time
from datetime import timedelta
from typing import Any

from config import app_now_naive
from database import IS_POSTGRES
from db import get_db


def _cutoff(days: int) -> str:
    return (app_now_naive() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')


def _future_cutoff(hours: int) -> str:
    return (app_now_naive() + timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')


def count_active_users(*, days: int) -> int:
    """Usuários com last_login_at (ou created_at) nos últimos N dias."""
    cutoff = _cutoff(days)
    db = get_db()
    c = db.cursor()
    if IS_POSTGRES:
        c.execute(
            '''SELECT COUNT(*) AS n FROM users
               WHERE COALESCE(last_login_at, created_at) >= ?::timestamp''',
            (cutoff,),
        )
    else:
        c.execute(
            '''SELECT COUNT(*) AS n FROM users
               WHERE datetime(COALESCE(last_login_at, created_at)) >= datetime(?)''',
            (cutoff,),
        )
    row = c.fetchone()
    db.close()
    return int(row['n'] if row else 0)


def activation_d7_rate() -> dict[str, Any]:
    """
    Entre usuários com ≥7 dias de conta, % que chegou em Modo Tocar (funil play_mode)
    em até 7 dias após o cadastro.
    """
    cohort_cutoff = _cutoff(7)
    db = get_db()
    c = db.cursor()
    if IS_POSTGRES:
        c.execute(
            '''SELECT COUNT(*) AS n FROM users
               WHERE created_at <= ?::timestamp''',
            (cohort_cutoff,),
        )
    else:
        c.execute(
            '''SELECT COUNT(*) AS n FROM users
               WHERE datetime(created_at) <= datetime(?)''',
            (cohort_cutoff,),
        )
    cohort = int((c.fetchone() or {}).get('n') or 0)

    if IS_POSTGRES:
        c.execute(
            '''SELECT COUNT(DISTINCT u.id) AS n
               FROM users u
               JOIN product_funnel_events f
                 ON f.user_id = u.id AND f.step = 'play_mode'
               WHERE u.created_at <= ?::timestamp
                 AND f.created_at <= (u.created_at + INTERVAL '7 days')''',
            (cohort_cutoff,),
        )
    else:
        c.execute(
            '''SELECT COUNT(DISTINCT u.id) AS n
               FROM users u
               JOIN product_funnel_events f
                 ON f.user_id = u.id AND f.step = 'play_mode'
               WHERE datetime(u.created_at) <= datetime(?)
                 AND datetime(f.created_at) <= datetime(u.created_at, '+7 days')''',
            (cohort_cutoff,),
        )
    activated = int((c.fetchone() or {}).get('n') or 0)
    db.close()
    pct = round(100.0 * activated / cohort, 1) if cohort else 0.0
    return {'cohort': cohort, 'activated': activated, 'pct': pct}


def trial_churn_stats() -> dict[str, Any]:
    """Trials de banda já encerrados: convertidos vs. voltaram ao grátis."""
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT COUNT(*) AS n FROM assinaturas
           WHERE trial_usado = 1 AND trial_fim IS NOT NULL
             AND trial_fim <= ?''',
        (app_now_naive().strftime('%Y-%m-%d %H:%M:%S'),),
    )
    expired = int((c.fetchone() or {}).get('n') or 0)
    c.execute(
        '''SELECT COUNT(*) AS n FROM assinaturas
           WHERE trial_usado = 1 AND trial_fim IS NOT NULL
             AND trial_fim <= ?
             AND plano IN ('pro', 'worship', 'individual')
             AND status = 'ativa' ''',
        (app_now_naive().strftime('%Y-%m-%d %H:%M:%S'),),
    )
    converted = int((c.fetchone() or {}).get('n') or 0)
    db.close()
    churned = max(0, expired - converted)
    churn_pct = round(100.0 * churned / expired, 1) if expired else 0.0
    convert_pct = round(100.0 * converted / expired, 1) if expired else 0.0
    return {
        'expired': expired,
        'converted': converted,
        'churned': churned,
        'churn_pct': churn_pct,
        'convert_pct': convert_pct,
    }


def nps_stats() -> dict[str, Any]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT COUNT(*) AS n, AVG(nps_score) AS avg_score
           FROM users WHERE nps_submitted_at IS NOT NULL AND nps_score IS NOT NULL'''
    )
    row = c.fetchone() or {}
    total = int(row.get('n') or 0)
    avg = round(float(row['avg_score']), 1) if row.get('avg_score') is not None else None

    c.execute(
        '''SELECT
             SUM(CASE WHEN nps_score >= 9 THEN 1 ELSE 0 END) AS promoters,
             SUM(CASE WHEN nps_score BETWEEN 7 AND 8 THEN 1 ELSE 0 END) AS passives,
             SUM(CASE WHEN nps_score <= 6 THEN 1 ELSE 0 END) AS detractors
           FROM users WHERE nps_submitted_at IS NOT NULL AND nps_score IS NOT NULL'''
    )
    dist = c.fetchone() or {}
    promoters = int(dist.get('promoters') or 0)
    passives = int(dist.get('passives') or 0)
    detractors = int(dist.get('detractors') or 0)
    nps = None
    if total:
        nps = round(100.0 * (promoters - detractors) / total, 1)

    c.execute(
        '''SELECT id, username, display_name, email, nps_score, nps_submitted_at
           FROM users
           WHERE nps_submitted_at IS NOT NULL AND nps_score IS NOT NULL AND nps_score <= 6
           ORDER BY nps_submitted_at DESC
           LIMIT 8'''
    )
    detractor_list = [dict(r) for r in c.fetchall()]
    db.close()
    return {
        'total': total,
        'avg': avg,
        'nps': nps,
        'promoters': promoters,
        'passives': passives,
        'detractors': detractors,
        'detractor_list': detractor_list,
    }


def incomplete_upcoming_events_count(*, within_hours: int = 24 * 7) -> int:
    """Eventos futuros (até N horas) sem setlist útil ou sem escala."""
    now = app_now_naive().strftime('%Y-%m-%d %H:%M:%S')
    end = _future_cutoff(within_hours)
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT e.id, e.setlist_id
           FROM band_events e
           WHERE e.starts_at >= ? AND e.starts_at < ?''',
        (now, end),
    )
    events = [dict(r) for r in c.fetchall()]
    if not events:
        db.close()
        return 0

    setlist_ids = [int(e['setlist_id']) for e in events if e.get('setlist_id')]
    counts: dict[int, int] = {}
    if setlist_ids:
        placeholders = ','.join('?' * len(setlist_ids))
        c.execute(
            f'''SELECT setlist_id, COUNT(*) AS n FROM setlist_cifras
                WHERE setlist_id IN ({placeholders}) GROUP BY setlist_id''',
            tuple(setlist_ids),
        )
        for row in c.fetchall():
            counts[int(row['setlist_id'])] = int(row['n'])

    # Escala: uma query só para todos os eventos (evita N+1).
    event_ids = [e['id'] for e in events]
    placeholders = ','.join('?' * len(event_ids))
    c.execute(
        f'''SELECT DISTINCT event_id FROM band_event_assignments
            WHERE event_id IN ({placeholders})''',
        tuple(event_ids),
    )
    events_with_scale = {row['event_id'] for row in c.fetchall()}
    db.close()

    incomplete = 0
    for e in events:
        sid = e.get('setlist_id')
        setlist_bad = (not sid) or counts.get(int(sid), 0) == 0
        no_scale = e['id'] not in events_with_scale
        if setlist_bad or no_scale:
            incomplete += 1
    return incomplete


def retention_campaign_counts(*, limit: int = 8) -> list[dict[str, Any]]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT campaign, COUNT(*) AS n
           FROM retention_emails
           WHERE status = 'enviado'
           GROUP BY campaign
           ORDER BY n DESC
           LIMIT ?''',
        (limit,),
    )
    rows = [{'campaign': r['campaign'], 'count': int(r['n'])} for r in c.fetchall()]
    db.close()
    return rows


# Cache em processo: o painel admin abre várias vezes ao dia e cada build roda
# ~8 queries agregadas. 5 min de TTL mantém o número fresco sem martelar o banco.
_METRICS_CACHE: dict[str, Any] = {'at': 0.0, 'data': None}
_METRICS_TTL_SECONDS = 300


def build_retention_metrics(*, force: bool = False) -> dict[str, Any]:
    now = time.time()
    cached = _METRICS_CACHE['data']
    if not force and cached is not None and (now - _METRICS_CACHE['at']) < _METRICS_TTL_SECONDS:
        return cached
    data = _compute_retention_metrics()
    _METRICS_CACHE['at'] = now
    _METRICS_CACHE['data'] = data
    return data


def _compute_retention_metrics() -> dict[str, Any]:
    users_total_db = get_db()
    c = users_total_db.cursor()
    c.execute('SELECT COUNT(*) AS n FROM users')
    users_total = int((c.fetchone() or {}).get('n') or 0)
    users_total_db.close()

    wau = count_active_users(days=7)
    mau = count_active_users(days=30)
    d7 = activation_d7_rate()
    trial = trial_churn_stats()
    nps = nps_stats()
    incomplete = incomplete_upcoming_events_count()
    campaigns = retention_campaign_counts()

    return {
        'wau': wau,
        'mau': mau,
        'wau_pct': round(100.0 * wau / users_total, 1) if users_total else 0.0,
        'mau_pct': round(100.0 * mau / users_total, 1) if users_total else 0.0,
        'users_total': users_total,
        'activation_d7': d7,
        'trial_churn': trial,
        'nps': nps,
        'incomplete_events_7d': incomplete,
        'campaigns': campaigns,
    }
