"""Contexto e métricas do painel do administrador master."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from config import app_now_naive
from database import IS_POSTGRES
from db import (
    count_bands,
    count_cifras,
    count_studios,
    count_users,
    count_users_without_band,
    get_db,
)
from product_funnel import FUNNEL_LABELS, funnel_activation_rows, funnel_counts
from retention_metrics import build_metrics_trend, build_retention_metrics, record_metrics_snapshot
from whatsapp_service import is_configured as whatsapp_configured


def _cutoff(days: int) -> str:
    return (app_now_naive() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')


def _user_rows(sql: str, params: tuple = (), *, limit: int = 8) -> list[dict]:
    db = get_db()
    c = db.cursor()
    c.execute(sql + f' LIMIT {int(limit)}', params)
    rows = [dict(r) for r in c.fetchall()]
    db.close()
    return rows


def engagement_action_queues(*, limit: int = 8) -> dict[str, Any]:
    """Filas acionáveis: cifra → tocar; solo saudável separado de abandono."""
    needs_cifra = _user_rows(
        '''SELECT u.id, u.username, u.display_name, u.email, u.phone, u.created_at, u.last_login_at
           FROM users u
           WHERE COALESCE(u.is_superadmin, 0) = 0
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'primeira_cifra'
             )
             AND NOT EXISTS (
               SELECT 1 FROM cifras c
               WHERE c.owner_user_id = u.id AND c.band_id IS NULL
             )
           ORDER BY u.created_at DESC''',
        limit=limit,
    )

    needs_play = _user_rows(
        '''SELECT u.id, u.username, u.display_name, u.email, u.phone, u.created_at, u.last_login_at
           FROM users u
           WHERE COALESCE(u.is_superadmin, 0) = 0
             AND COALESCE(u.play_mode_used, 0) = 0
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'play_mode'
             )
             AND (
               EXISTS (
                 SELECT 1 FROM product_funnel_events f
                 WHERE f.user_id = u.id AND f.step = 'primeira_cifra'
               )
               OR EXISTS (
                 SELECT 1 FROM cifras c
                 WHERE c.owner_user_id = u.id AND c.band_id IS NULL
               )
             )
           ORDER BY u.created_at DESC''',
        limit=limit,
    )

    solo_activated = _user_rows(
        '''SELECT u.id, u.username, u.display_name, u.email, u.phone, u.created_at, u.last_login_at
           FROM users u
           WHERE COALESCE(u.is_superadmin, 0) = 0
             AND NOT EXISTS (SELECT 1 FROM band_members bm WHERE bm.user_id = u.id)
             AND (
               COALESCE(u.play_mode_used, 0) = 1
               OR EXISTS (
                 SELECT 1 FROM product_funnel_events f
                 WHERE f.user_id = u.id AND f.step IN ('primeira_cifra', 'play_mode')
               )
               OR EXISTS (
                 SELECT 1 FROM cifras c
                 WHERE c.owner_user_id = u.id AND c.band_id IS NULL
               )
             )
           ORDER BY COALESCE(u.last_login_at, u.created_at) DESC''',
        limit=limit,
    )

    now = app_now_naive().strftime('%Y-%m-%d %H:%M:%S')
    week = (app_now_naive() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT a.banda_id, a.plano, a.trial_fim, b.name AS band_name, b.owner_id,
                  u.id AS user_id, u.username, u.display_name, u.email, u.phone
           FROM assinaturas a
           JOIN bands b ON b.id = a.banda_id
           LEFT JOIN users u ON u.id = b.owner_id
           WHERE a.trial_usado = 1
             AND a.trial_fim IS NOT NULL
             AND a.trial_fim > ?
             AND a.trial_fim <= ?
           ORDER BY a.trial_fim ASC
           LIMIT ?''',
        (now, week, limit),
    )
    trials_ending = [dict(r) for r in c.fetchall()]
    db.close()

    return {
        'needs_cifra': needs_cifra,
        'needs_play': needs_play,
        'solo_activated': solo_activated,
        'trials_ending': trials_ending,
    }


def monetization_snapshot() -> dict[str, Any]:
    """Planos ativos e trials — diagnóstico SaaS (não cachê de banda)."""
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT plano, COUNT(*) AS n FROM assinaturas
           WHERE status IN ('ativa', 'voucher')
             AND plano IN ('individual', 'pro', 'worship')
           GROUP BY plano'''
    )
    by_plan = {str(r['plano']): int(r['n']) for r in c.fetchall()}

    now = app_now_naive().strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        '''SELECT COUNT(*) AS n FROM assinaturas
           WHERE trial_usado = 1 AND trial_fim IS NOT NULL AND trial_fim > ?''',
        (now,),
    )
    trials_active = int((c.fetchone() or {}).get('n') or 0)

    c.execute("SELECT COUNT(*) AS n FROM assinaturas WHERE status = 'inadimplente'")
    inadimplente = int((c.fetchone() or {}).get('n') or 0)

    try:
        c.execute(
            '''SELECT COUNT(*) AS n FROM studio_subscriptions
               WHERE status IN ('ativa', 'voucher') AND plano = 'estudio_premium' '''
        )
        studio_premium = int((c.fetchone() or {}).get('n') or 0)
    except Exception:
        studio_premium = 0
    db.close()

    from retention_metrics import trial_churn_stats

    return {
        'by_plan': by_plan,
        'paid_total': sum(by_plan.values()),
        'individual': by_plan.get('individual', 0),
        'pro': by_plan.get('pro', 0),
        'worship': by_plan.get('worship', 0),
        'trials_active': trials_active,
        'inadimplente': inadimplente,
        'studio_premium': studio_premium,
        'trial_churn': trial_churn_stats(),
    }


def funnel_leak(funnel_rows: list[dict]) -> dict[str, Any] | None:
    worst = None
    for i, row in enumerate(funnel_rows):
        if i == 0:
            continue
        drop = 100 - int(row.get('pct_of_prev') or 100)
        if drop <= 0:
            continue
        prev = funnel_rows[i - 1]
        candidate = {
            'from_label': prev['label'],
            'to_label': row['label'],
            'drop_pct': drop,
            'from_count': prev['count'],
            'to_count': row['count'],
        }
        if worst is None or candidate['drop_pct'] > worst['drop_pct']:
            worst = candidate
    return worst


def cohort_activation_7d() -> dict[str, Any]:
    """Cadastros dos últimos 7 dias → cifra / Modo Tocar."""
    cutoff = _cutoff(7)
    db = get_db()
    c = db.cursor()
    ts = 'u.created_at >= ?::timestamp' if IS_POSTGRES else 'datetime(u.created_at) >= datetime(?)'
    c.execute(
        f'''SELECT COUNT(*) AS n FROM users u
            WHERE {ts} AND COALESCE(u.is_superadmin, 0) = 0''',
        (cutoff,),
    )
    signups = int((c.fetchone() or {}).get('n') or 0)

    c.execute(
        f'''SELECT COUNT(DISTINCT u.id) AS n FROM users u
            WHERE {ts} AND COALESCE(u.is_superadmin, 0) = 0
              AND (
                COALESCE(u.play_mode_used, 0) = 1
                OR EXISTS (
                  SELECT 1 FROM product_funnel_events f
                  WHERE f.user_id = u.id AND f.step = 'play_mode'
                )
              )''',
        (cutoff,),
    )
    played = int((c.fetchone() or {}).get('n') or 0)

    c.execute(
        f'''SELECT COUNT(DISTINCT u.id) AS n FROM users u
            WHERE {ts} AND COALESCE(u.is_superadmin, 0) = 0
              AND (
                EXISTS (
                  SELECT 1 FROM product_funnel_events f
                  WHERE f.user_id = u.id AND f.step = 'primeira_cifra'
                )
                OR EXISTS (
                  SELECT 1 FROM cifras c
                  WHERE c.owner_user_id = u.id AND c.band_id IS NULL
                )
              )''',
        (cutoff,),
    )
    with_cifra = int((c.fetchone() or {}).get('n') or 0)
    db.close()
    return {
        'signups': signups,
        'with_cifra': with_cifra,
        'played': played,
        'cifra_pct': round(100.0 * with_cifra / signups, 1) if signups else 0.0,
        'play_pct': round(100.0 * played / signups, 1) if signups else 0.0,
    }


def _engagement_totals() -> dict[str, int]:
    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT COUNT(*) AS n FROM users u
           WHERE COALESCE(u.is_superadmin, 0) = 0
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'primeira_cifra'
             )
             AND NOT EXISTS (
               SELECT 1 FROM cifras c
               WHERE c.owner_user_id = u.id AND c.band_id IS NULL
             )'''
    )
    needs_cifra = int((c.fetchone() or {}).get('n') or 0)
    c.execute(
        '''SELECT COUNT(*) AS n FROM users u
           WHERE COALESCE(u.is_superadmin, 0) = 0
             AND COALESCE(u.play_mode_used, 0) = 0
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'play_mode'
             )
             AND (
               EXISTS (
                 SELECT 1 FROM product_funnel_events f
                 WHERE f.user_id = u.id AND f.step = 'primeira_cifra'
               )
               OR EXISTS (
                 SELECT 1 FROM cifras c
                 WHERE c.owner_user_id = u.id AND c.band_id IS NULL
               )
             )'''
    )
    needs_play = int((c.fetchone() or {}).get('n') or 0)
    c.execute(
        '''SELECT COUNT(*) AS n FROM users u
           WHERE COALESCE(u.is_superadmin, 0) = 0
             AND NOT EXISTS (SELECT 1 FROM band_members bm WHERE bm.user_id = u.id)
             AND (
               COALESCE(u.play_mode_used, 0) = 1
               OR EXISTS (
                 SELECT 1 FROM product_funnel_events f
                 WHERE f.user_id = u.id AND f.step IN ('primeira_cifra', 'play_mode')
               )
               OR EXISTS (
                 SELECT 1 FROM cifras c
                 WHERE c.owner_user_id = u.id AND c.band_id IS NULL
               )
             )'''
    )
    solo_ok = int((c.fetchone() or {}).get('n') or 0)
    db.close()
    return {
        'needs_cifra': needs_cifra,
        'needs_play': needs_play,
        'solo_activated': solo_ok,
        'users_no_band': count_users_without_band(),
    }


def build_admin_dashboard_context() -> dict:
    """Contexto agregado (métricas/contagens) do painel admin."""
    users_total = count_users()
    funnel_rows = funnel_activation_rows(users_total=users_total)
    all_funnel = funnel_counts()

    _retention = build_retention_metrics()
    try:
        record_metrics_snapshot(_retention)
    except Exception:
        pass
    _trend = build_metrics_trend()

    monetization = monetization_snapshot()
    queues = engagement_action_queues(limit=8)
    queues['totals'] = _engagement_totals()
    cohort = cohort_activation_7d()
    leak = funnel_leak(funnel_rows)

    platform_finance = None
    try:
        from band_finance import build_platform_finance_totals, default_finance_period

        y, m, _, _ = default_finance_period()
        platform_finance = build_platform_finance_totals(year=y, month=m)
    except Exception:
        platform_finance = None

    return {
        'stats': {
            'bands': count_bands(),
            'cifras': count_cifras(),
            'users': users_total,
            'studios': count_studios(),
            'users_no_band': count_users_without_band(),
            'signups_7d': cohort['signups'],
        },
        'funnel_rows': funnel_rows,
        'funnel_extra': {
            'agenda': all_funnel.get('primeiro_evento_agenda', 0),
            'estudio': all_funnel.get('estudio_cadastrado', 0),
            'reserva': all_funnel.get('estudio_reserva_confirmada', 0),
        },
        'funnel_leak': leak,
        'retention': _retention,
        'metrics_trend': _trend,
        'monetization': monetization,
        'engagement_queues': queues,
        'cohort_7d': cohort,
        'whatsapp_configured': whatsapp_configured(),
        'platform_finance': platform_finance,
    }
