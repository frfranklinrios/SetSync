"""Alavancas de conversão — gates leves em cima do freemium (ago/2026).

Grátis prova o aha; operação de show (2º cachê, freela, N eventos) puxa Pro.
"""

from __future__ import annotations

from typing import Any

from monetizacao import (
    PLANO_GRATIS,
    PLANO_INDIVIDUAL,
    PLANO_PRO,
    PLANOS,
    get_plano_efetivo,
)

# Cotas extras do Grátis (além de LIMITES_GRATIS)
LIMITES_GRATIS_EXTRA = {
    'freela_por_evento': 1,       # convidados por show
    'eventos_agenda': 1,          # eventos totais da banda
    'fechamentos_cache': 1,       # shows com fee_total > 0 antes do paywall
}


def banda_eh_paga(band_id: str | None) -> bool:
    if not band_id:
        return False
    return get_plano_efetivo(band_id) != PLANO_GRATIS


def _count_sql(sql: str, params: tuple) -> int:
    from db import get_db

    db = get_db()
    c = db.cursor()
    c.execute(sql, params)
    row = c.fetchone()
    db.close()
    if not row:
        return 0
    val = row[0] if not hasattr(row, 'keys') else list(row.values())[0]
    return int(val or 0)


def count_band_events(band_id: str) -> int:
    return _count_sql(
        'SELECT COUNT(*) FROM band_events WHERE band_id = ?',
        (band_id,),
    )


def count_band_shows_with_fee(band_id: str) -> int:
    return _count_sql(
        '''SELECT COUNT(*) FROM band_events
           WHERE band_id = ? AND event_type = 'show'
             AND COALESCE(fee_total, 0) > 0''',
        (band_id,),
    )


def count_event_guests(event_id: str) -> int:
    return _count_sql(
        '''SELECT COUNT(*) FROM band_event_guests
           WHERE event_id = ?
             AND LOWER(COALESCE(response_status, 'pending')) != 'declined' ''',
        (event_id,),
    )


def count_band_scale_events_30d(band_id: str) -> int:
    """Shows/ensaios com ≥1 confirmação de escala nos últimos 30 dias."""
    from datetime import timedelta
    from config import app_now_naive

    cutoff = (app_now_naive() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    return _count_sql(
        '''SELECT COUNT(DISTINCT e.id)
           FROM band_events e
           JOIN band_event_assignments a ON a.event_id = e.id
           WHERE e.band_id = ?
             AND COALESCE(a.response_status, '') = 'accepted'
             AND e.starts_at >= ?''',
        (band_id, cutoff),
    )

def pode_criar_evento(band_id: str) -> bool:
    if banda_eh_paga(band_id):
        return True
    return count_band_events(band_id) < LIMITES_GRATIS_EXTRA['eventos_agenda']


def pode_adicionar_freela(event_id: str, band_id: str) -> bool:
    if banda_eh_paga(band_id):
        return True
    return count_event_guests(event_id) < LIMITES_GRATIS_EXTRA['freela_por_evento']


def pode_salvar_fechamento(band_id: str, *, event_id: str | None = None) -> bool:
    """1º show com cachê grátis; a partir do 2º precisa Pro.

    Se o evento já tem fee, re-salvar o mesmo show continua liberado.
    """
    if banda_eh_paga(band_id):
        return True
    from models_agenda import get_band_event

    if event_id:
        ev = get_band_event(event_id)
        if ev and float(ev.get('fee_total') or 0) > 0:
            return True  # editar o 1º (ou qualquer já aberto) ok no Grátis
    return count_band_shows_with_fee(band_id) < LIMITES_GRATIS_EXTRA['fechamentos_cache']


def pode_pdf_financeiro_banda(band_id: str) -> bool:
    """PDF do caixa da banda = Pro (Meu financeiro pessoal continua livre)."""
    return banda_eh_paga(band_id)


def pode_whatsapp_prep_banda(band_id: str) -> bool:
    """Digest/alerta 'ensaio amanhã' por WhatsApp = Pro."""
    return banda_eh_paga(band_id)


def cta_pro(user_id: str | None = None, *, banda_id: str | None = None, motivo: str = 'limite') -> dict:
    from flask import url_for
    from flask import has_request_context

    preco = int(PLANOS[PLANO_PRO].preco_mensal or 29)
    if has_request_context():
        kwargs = {'plano': PLANO_PRO, 'go': 1}
        if banda_id:
            kwargs['banda_id'] = banda_id
        url = url_for('assinatura_bp.planos', **kwargs)
    else:
        url = f'/assinatura/planos?plano=pro&go=1'
        if banda_id:
            url += f'&banda_id={banda_id}'
    return {
        'plano_sugerido': PLANO_PRO,
        'cta_label': f'Assinar Pro — R$ {preco}/mês',
        'upgrade_url': url,
        'preco_linha': f'Pro — R$ {preco}/mês · noite pronta (setlist + PDF + offline)',
        'titulo': 'Continue com o Pro',
    }


def cta_individual(user_id: str | None = None) -> dict:
    from flask import url_for, has_request_context

    preco = int(PLANOS[PLANO_INDIVIDUAL].preco_mensal or 15)
    if has_request_context():
        url = url_for('assinatura_bp.planos', plano=PLANO_INDIVIDUAL, go=1)
    else:
        url = '/assinatura/planos?plano=individual&go=1'
    return {
        'plano_sugerido': PLANO_INDIVIDUAL,
        'cta_label': f'Assinar Individual — R$ {preco}',
        'upgrade_url': url,
        'preco_linha': f'Individual — R$ {preco}/mês',
        'titulo': 'Continue no Individual',
    }


def resposta_paywall_conversao(mensagem: str, *, banda_id: str | None = None, plano: str = PLANO_PRO):
    from flask import flash, jsonify, redirect, request

    cta = cta_pro(banda_id=banda_id) if plano == PLANO_PRO else cta_individual()
    payload = {
        'erro': 'plano_necessario',
        'mensagem': mensagem,
        **cta,
    }
    wants_json = (
        request.accept_mimetypes.best == 'application/json'
        or request.is_json
        or (request.headers.get('X-Requested-With') or '').lower() == 'xmlhttprequest'
    )
    if wants_json:
        return jsonify(payload), 402
    flash(mensagem, 'warning')
    return redirect(cta['upgrade_url'])


def trial_opt_in_disponivel(band_id: str) -> bool:
    """Trial 7d só se nunca usou e banda ainda Grátis."""
    if banda_eh_paga(band_id):
        return False
    from monetizacao import get_assinatura_banda, TRIAL_AUTO

    if TRIAL_AUTO:
        return False
    a = get_assinatura_banda(band_id)
    return not bool(a.trial_usado)


def iniciar_trial_opt_in(band_id: str, user_id: str) -> bool:
    from monetizacao import iniciar_trial_banda
    from product_funnel import log_funnel_step

    if not trial_opt_in_disponivel(band_id):
        return False
    if not iniciar_trial_banda(band_id):
        return False
    try:
        log_funnel_step(user_id, 'trial_iniciado', meta={'source': 'opt_in_show', 'banda_id': band_id})
    except Exception:
        pass
    return True
