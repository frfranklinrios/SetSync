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


_EXCLUDE_USER_SQL = """
COALESCE(u.is_superadmin, 0) = 0
AND COALESCE(u.is_demo, 0) = 0
AND LOWER(COALESCE(u.username, '')) NOT IN (
  'amanda', 'showcase', 'igreja_showcase', 'carlos_groove', 'ana_costa'
)
"""


def engagement_action_queues(*, limit: int = 8) -> dict[str, Any]:
    """Filas acionáveis: concierge de cifra real → palco → chamar a banda."""
    since14 = _cutoff(14)
    needs_cifra = _user_rows(
        f'''SELECT u.id, u.username, u.display_name, u.email, u.phone, u.created_at, u.last_login_at
           FROM users u
           WHERE {_EXCLUDE_USER_SQL}
             AND u.created_at >= ?
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'primeira_cifra_real'
             )
           ORDER BY u.created_at DESC''',
        (since14,),
        limit=limit,
    )

    needs_play = _user_rows(
        f'''SELECT u.id, u.username, u.display_name, u.email, u.phone, u.created_at, u.last_login_at
           FROM users u
           WHERE {_EXCLUDE_USER_SQL}
             AND EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'primeira_cifra_real'
             )
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'play_mode_real'
             )
           ORDER BY u.created_at DESC''',
        limit=limit,
    )

    solo_activated = _user_rows(
        f'''SELECT u.id, u.username, u.display_name, u.email, u.phone, u.created_at, u.last_login_at
           FROM users u
           WHERE {_EXCLUDE_USER_SQL}
             AND EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'play_mode_real'
             )
             AND NOT EXISTS (
               SELECT 1 FROM band_members me
               JOIN band_members other
                 ON other.band_id = me.band_id AND other.user_id <> me.user_id
               WHERE me.user_id = u.id
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

    # Campeões de escala (não demo / não fundador) — prioridade de outreach
    c.execute(
        '''SELECT u.id, u.username, u.display_name, u.email, u.phone, u.last_login_at,
                  COUNT(*) AS scale_accepts
           FROM users u
           JOIN band_event_assignments a ON a.user_id = u.id AND a.response_status = 'accepted'
           WHERE COALESCE(u.is_superadmin, 0) = 0
             AND COALESCE(u.is_demo, 0) = 0
             AND LOWER(COALESCE(u.username, '')) NOT IN ('amanda', 'showcase', 'igreja_showcase')
           GROUP BY u.id, u.username, u.display_name, u.email, u.phone, u.last_login_at
           HAVING COUNT(*) >= 2
           ORDER BY COUNT(*) DESC, COALESCE(u.last_login_at, u.created_at) DESC
           LIMIT ?''',
        (limit,),
    )
    scale_champions = [dict(r) for r in c.fetchall()]

    # Trial acabou (14d) e ainda grátis — conversão
    ago14 = (app_now_naive() - timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        '''SELECT a.banda_id, a.plano, a.trial_fim, b.name AS band_name, b.owner_id,
                  u.id AS user_id, u.username, u.display_name, u.email, u.phone
           FROM assinaturas a
           JOIN bands b ON b.id = a.banda_id
           LEFT JOIN users u ON u.id = b.owner_id
           WHERE a.trial_usado = 1
             AND a.trial_fim IS NOT NULL
             AND a.trial_fim < ?
             AND a.trial_fim >= ?
             AND a.plano = 'gratis'
             AND COALESCE(u.is_superadmin, 0) = 0
             AND COALESCE(u.is_demo, 0) = 0
             AND LOWER(COALESCE(u.username, '')) <> 'amanda'
           ORDER BY a.trial_fim DESC
           LIMIT ?''',
        (now, ago14, limit),
    )
    trials_churned = [dict(r) for r in c.fetchall()]

    # Shows próximos sem escala
    until30 = (app_now_naive() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        '''SELECT e.id AS event_id, e.title, e.starts_at, b.id AS band_id, b.name AS band_name,
                  u.id AS user_id, u.username, u.display_name, u.email, u.phone
           FROM band_events e
           JOIN bands b ON b.id = e.band_id
           LEFT JOIN users u ON u.id = b.owner_id
           WHERE e.starts_at >= ? AND e.starts_at <= ?
             AND e.event_type = 'show'
             AND COALESCE(u.is_demo, 0) = 0
             AND LOWER(COALESCE(u.username, '')) <> 'amanda'
             AND NOT EXISTS (
               SELECT 1 FROM band_event_assignments a WHERE a.event_id = e.id
             )
           ORDER BY e.starts_at ASC
           LIMIT ?''',
        (now, until30, limit),
    )
    shows_no_scale = [dict(r) for r in c.fetchall()]

    # Bandas reais sem nenhum evento — empurrar Comando / 1º show
    c.execute(
        '''SELECT b.id AS band_id, b.name AS band_name, b.created_at,
                  u.id AS user_id, u.username, u.display_name, u.email, u.phone, u.last_login_at
           FROM bands b
           LEFT JOIN users u ON u.id = b.owner_id
           WHERE COALESCE(u.is_superadmin, 0) = 0
             AND COALESCE(u.is_demo, 0) = 0
             AND LOWER(COALESCE(u.username, '')) NOT IN (
               'amanda', 'showcase', 'igreja_showcase', 'carlos_groove', 'ana_costa'
             )
             AND LOWER(COALESCE(b.name, '')) NOT LIKE 'banda teste%'
             AND COALESCE(u.phone, '') NOT LIKE '%999990000'
             AND NOT EXISTS (SELECT 1 FROM band_events e WHERE e.band_id = b.id)
           ORDER BY COALESCE(u.last_login_at, b.created_at) DESC
           LIMIT ?''',
        (limit,),
    )
    bands_no_events = [dict(r) for r in c.fetchall()]
    db.close()

    return {
        'needs_cifra': needs_cifra,
        'needs_play': needs_play,
        'solo_activated': solo_activated,
        'trials_ending': trials_ending,
        'scale_champions': scale_champions,
        'trials_churned': trials_churned,
        'shows_no_scale': shows_no_scale,
        'bands_no_events': bands_no_events,
    }


def monetization_snapshot() -> dict[str, Any]:
    """Planos ativos e trials — diagnóstico SaaS (não cachê de banda)."""
    # Contas/bandas do fundador não contam como cliente pagante no Pulse.
    _founder_user_sql = (
        "LOWER(COALESCE(u.username, '')) IN ('amanda') "
        "OR COALESCE(u.is_superadmin, 0) = 1"
    )
    _founder_band_sql = (
        "LOWER(COALESCE(b.name, '')) LIKE 'banda teste%' "
        f"OR {_founder_user_sql}"
    )

    db = get_db()
    c = db.cursor()
    c.execute(
        '''SELECT plano, COUNT(*) AS n FROM assinaturas
           WHERE status IN ('ativa', 'voucher')
             AND plano IN ('individual', 'pro', 'worship')
           GROUP BY plano'''
    )
    by_plan = {str(r['plano']): int(r['n']) for r in c.fetchall()}

    # Pagante real = Mercado Pago ativo, excl. fundador. Sem MP conta como voucher/cortesia.
    _mp_ok = (
        '(a.mp_preapproval_id IS NOT NULL OR a.mp_subscription_id IS NOT NULL)'
    )
    c.execute(
        f'''SELECT COUNT(*) AS n
            FROM assinaturas a
            JOIN bands b ON b.id = a.banda_id
            LEFT JOIN users u ON u.id = b.owner_id
            WHERE a.status = 'ativa'
              AND a.plano IN ('individual', 'pro', 'worship')
              AND {_mp_ok}
              AND NOT ({_founder_band_sql})'''
    )
    paid_real = int((c.fetchone() or {}).get('n') or 0)

    c.execute(
        f'''SELECT COUNT(*) AS n
            FROM assinaturas a
            JOIN bands b ON b.id = a.banda_id
            LEFT JOIN users u ON u.id = b.owner_id
            WHERE a.plano IN ('individual', 'pro', 'worship')
              AND NOT ({_founder_band_sql})
              AND (
                a.status = 'voucher'
                OR (a.status = 'ativa' AND NOT {_mp_ok})
              )'''
    )
    voucher_total = int((c.fetchone() or {}).get('n') or 0)

    now = app_now_naive().strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        f'''SELECT COUNT(*) AS n
            FROM assinaturas a
            JOIN bands b ON b.id = a.banda_id
            LEFT JOIN users u ON u.id = b.owner_id
            WHERE a.trial_usado = 1 AND a.trial_fim IS NOT NULL AND a.trial_fim > ?
              AND NOT ({_founder_band_sql})''',
        (now,),
    )
    trials_active = int((c.fetchone() or {}).get('n') or 0)

    c.execute("SELECT COUNT(*) AS n FROM assinaturas WHERE status = 'inadimplente'")
    inadimplente = int((c.fetchone() or {}).get('n') or 0)

    studio_paid = 0
    studio_voucher = 0
    _mp_ok_plain = '(mp_preapproval_id IS NOT NULL OR mp_subscription_id IS NOT NULL)'
    try:
        c.execute(
            f'''SELECT COUNT(*) AS n FROM studio_subscriptions
                WHERE status = 'ativa' AND plano = 'estudio_premium'
                  AND {_mp_ok_plain}'''
        )
        studio_paid = int((c.fetchone() or {}).get('n') or 0)
        c.execute(
            f'''SELECT COUNT(*) AS n FROM studio_subscriptions
                WHERE plano = 'estudio_premium'
                  AND (
                    status = 'voucher'
                    OR (status = 'ativa' AND NOT {_mp_ok_plain})
                  )'''
        )
        studio_voucher = int((c.fetchone() or {}).get('n') or 0)
    except Exception:
        pass
    studio_premium = studio_paid + studio_voucher

    cutoff = _cutoff(7)
    c.execute(
        '''SELECT COUNT(DISTINCT a.event_id) AS n
           FROM band_event_assignments a
           JOIN band_events e ON e.id = a.event_id
           WHERE e.created_at >= ? OR a.assigned_at >= ?''',
        (cutoff, cutoff),
    )
    try:
        scale_events_7d = int((c.fetchone() or {}).get('n') or 0)
    except Exception:
        scale_events_7d = 0
    c.execute(
        '''SELECT COUNT(DISTINCT g.event_id) AS n
           FROM band_event_guests g
           JOIN band_events e ON e.id = g.event_id
           WHERE g.created_at >= ?''',
        (cutoff,),
    )
    try:
        guest_events_7d = int((c.fetchone() or {}).get('n') or 0)
    except Exception:
        guest_events_7d = 0
    c.execute(
        '''SELECT COUNT(DISTINCT e.band_id) AS n
           FROM band_event_assignments a
           JOIN band_events e ON e.id = a.event_id'''
    )
    bands_with_scale = int((c.fetchone() or {}).get('n') or 0)
    c.execute(
        '''SELECT COUNT(DISTINCT e.band_id) AS n
           FROM band_event_guests g
           JOIN band_events e ON e.id = g.event_id'''
    )
    bands_with_guest = int((c.fetchone() or {}).get('n') or 0)
    db.close()

    from retention_metrics import trial_churn_stats

    return {
        'by_plan': by_plan,
        'paid_total': paid_real + voucher_total,
        'paid_real': paid_real,
        'voucher_total': voucher_total,
        'individual': by_plan.get('individual', 0),
        'pro': by_plan.get('pro', 0),
        'worship': by_plan.get('worship', 0),
        'trials_active': trials_active,
        'inadimplente': inadimplente,
        'studio_premium': studio_premium,
        'studio_paid': studio_paid,
        'studio_voucher': studio_voucher,
        'trial_churn': trial_churn_stats(),
        'scale_events_7d': scale_events_7d,
        'guest_events_7d': guest_events_7d,
        'bands_with_scale': bands_with_scale,
        'bands_with_guest': bands_with_guest,
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
    since14 = _cutoff(14)
    c.execute(
        f'''SELECT COUNT(*) AS n FROM users u
           WHERE {_EXCLUDE_USER_SQL}
             AND u.created_at >= ?
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'primeira_cifra_real'
             )''',
        (since14,),
    )
    needs_cifra = int((c.fetchone() or {}).get('n') or 0)
    c.execute(
        f'''SELECT COUNT(*) AS n FROM users u
           WHERE {_EXCLUDE_USER_SQL}
             AND EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'primeira_cifra_real'
             )
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'play_mode_real'
             )'''
    )
    needs_play = int((c.fetchone() or {}).get('n') or 0)
    c.execute(
        f'''SELECT COUNT(*) AS n FROM users u
           WHERE {_EXCLUDE_USER_SQL}
             AND EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'play_mode_real'
             )
             AND NOT EXISTS (
               SELECT 1 FROM band_members me
               JOIN band_members other
                 ON other.band_id = me.band_id AND other.user_id <> me.user_id
               WHERE me.user_id = u.id
             )'''
    )
    solo_ok = int((c.fetchone() or {}).get('n') or 0)
    c.execute(
        '''SELECT COUNT(*) AS n FROM bands b
           LEFT JOIN users u ON u.id = b.owner_id
           WHERE COALESCE(u.is_superadmin, 0) = 0
             AND COALESCE(u.is_demo, 0) = 0
             AND LOWER(COALESCE(u.username, '')) NOT IN (
               'amanda', 'showcase', 'igreja_showcase', 'carlos_groove', 'ana_costa'
             )
             AND LOWER(COALESCE(b.name, '')) NOT LIKE 'banda teste%'
             AND COALESCE(u.phone, '') NOT LIKE '%999990000'
             AND NOT EXISTS (SELECT 1 FROM band_events e WHERE e.band_id = b.id)'''
    )
    bands_no_events = int((c.fetchone() or {}).get('n') or 0)
    db.close()
    return {
        'needs_cifra': needs_cifra,
        'needs_play': needs_play,
        'solo_activated': solo_ok,
        'bands_no_events': bands_no_events,
        'users_no_band': count_users_without_band(),
    }


def jornada_snapshot(*, tourist_limit: int = 20) -> dict[str, Any]:
    """Cadastro → cifra real → palco: contas reais, turistas e vazamento."""
    db = get_db()
    c = db.cursor()
    c.execute(
        f'''SELECT COUNT(*) AS n FROM users u
           WHERE {_EXCLUDE_USER_SQL}'''
    )
    row = c.fetchone()
    real_users = int(row['n'] if row else 0)
    c.execute(
        f"""SELECT COUNT(DISTINCT f.user_id) AS n
           FROM product_funnel_events f
           JOIN users u ON u.id = f.user_id
           WHERE {_EXCLUDE_USER_SQL} AND f.step = 'primeira_cifra_real'"""
    )
    row = c.fetchone()
    with_real = int(row['n'] if row else 0)
    c.execute(
        f"""SELECT COUNT(DISTINCT f.user_id) AS n
           FROM product_funnel_events f
           JOIN users u ON u.id = f.user_id
           WHERE {_EXCLUDE_USER_SQL} AND f.step = 'play_mode_real'"""
    )
    row = c.fetchone()
    played_real = int(row['n'] if row else 0)
    db.close()

    if IS_POSTGRES:
        stale = (
            "u.created_at < (CURRENT_TIMESTAMP - INTERVAL '1 day') "
            "AND (u.last_login_at IS NULL OR u.last_login_at <= u.created_at + INTERVAL '2 hours')"
        )
    else:
        stale = (
            "datetime(u.created_at) < datetime('now', '-1 day') "
            "AND (u.last_login_at IS NULL "
            "OR datetime(u.last_login_at) <= datetime(u.created_at, '+2 hours'))"
        )
    tourists = _user_rows(
        f'''SELECT u.id, u.username, u.display_name, u.email, u.phone, u.created_at, u.last_login_at
           FROM users u
           WHERE {_EXCLUDE_USER_SQL}
             AND {stale}
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'primeira_cifra_real'
             )
           ORDER BY u.created_at DESC''',
        limit=tourist_limit,
    )
    db = get_db()
    c = db.cursor()
    c.execute(
        f'''SELECT COUNT(*) AS n FROM users u
           WHERE {_EXCLUDE_USER_SQL}
             AND {stale}
             AND NOT EXISTS (
               SELECT 1 FROM product_funnel_events f
               WHERE f.user_id = u.id AND f.step = 'primeira_cifra_real'
             )'''
    )
    row = c.fetchone()
    tourist_total = int(row['n'] if row else 0)
    db.close()

    cifra_pct = round(100.0 * with_real / real_users) if real_users else 0
    play_pct = round(100.0 * played_real / real_users) if real_users else 0
    play_of_cifra = round(100.0 * played_real / with_real) if with_real else 0
    return {
        'real_users': real_users,
        'with_real': with_real,
        'played_real': played_real,
        'cifra_pct': cifra_pct,
        'play_pct': play_pct,
        'play_of_cifra': play_of_cifra,
        'tourists': tourists,
        'tourist_total': tourist_total,
    }


def build_admin_dashboard_context() -> dict:
    """Contexto agregado (métricas/contagens) do painel admin."""
    try:
        from product_funnel import backfill_product_funnel

        backfill_product_funnel()
    except Exception:
        pass

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

    winback = {'total': 0, 'by_segment': {}, 'with_phone': 0, 'email_ok': False}
    try:
        from winback import preview_winback
        winback = preview_winback(min_inactive_days=5)
    except Exception:
        pass

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
        'winback': winback,
    }
