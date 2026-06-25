"""Alertas contextuais de upgrade no dashboard."""

from __future__ import annotations

from flask import url_for

from db import count_band_cifras, count_band_members, count_band_setlists, get_owned_bands
from monetizacao import (
    LIMITES_GRATIS,
    dias_restantes_trial,
    dias_restantes_trial_estudio,
    get_plano_efetivo,
    studio_tem_premium,
)


def _near_limit_message(current: int, limit: int, recurso: str) -> str | None:
    if current < max(1, limit - 3):
        return None
    if current >= limit:
        return f'Limite do plano grátis: {current}/{limit} {recurso}.'
    return f'Você usa {current} de {limit} {recurso} no plano grátis.'


def get_dashboard_upsells(user_id: str, *, owned_bands: list | None = None) -> list[dict]:
    """Banners de conversão baseados em uso real."""
    bands = owned_bands if owned_bands is not None else get_owned_bands(user_id)
    alerts: list[dict] = []

    for band in bands:
        band_id = band['id']
        if get_plano_efetivo(band_id) != 'gratis':
            continue
        name = band.get('name') or 'sua banda'
        planos_url = url_for('assinatura_bp.planos', banda_id=band_id)

        for recurso, limit, counter, label in (
            ('músicas', LIMITES_GRATIS['musica'], count_band_cifras, 'músicas'),
            ('setlists', LIMITES_GRATIS['setlist'], count_band_setlists, 'setlists'),
            ('integrantes', LIMITES_GRATIS['integrante'], count_band_members, 'integrantes'),
        ):
            current = counter(band_id)
            msg = _near_limit_message(current, limit, label)
            if msg:
                alerts.append({
                    'level': 'warning' if current >= limit else 'info',
                    'title': f'{name} — {recurso}',
                    'message': msg,
                    'cta_label': 'Ver planos Pro',
                    'cta_url': planos_url,
                })

        dias = dias_restantes_trial(band_id)
        if dias is not None and dias <= 7:
            alerts.append({
                'level': 'success' if dias > 3 else 'warning',
                'title': f'Trial Pro — {name}',
                'message': f'Faltam {dias} dia(s) de trial com recursos ilimitados.',
                'cta_label': 'Assinar Pro',
                'cta_url': planos_url,
            })

    if not studio_tem_premium(user_id):
        from models_studio import list_studios_by_owner
        studios = list_studios_by_owner(user_id)
        if studios:
            dias_st = dias_restantes_trial_estudio(user_id)
            if dias_st is not None and dias_st <= 7:
                alerts.append({
                    'level': 'warning' if dias_st <= 3 else 'info',
                    'title': 'Trial Premium do estúdio',
                    'message': f'Faltam {dias_st} dia(s) para salas ilimitadas.',
                    'cta_label': 'Ver planos Estúdio',
                    'cta_url': url_for('assinatura_bp.planos') + '#estudio',
                })
            elif not studio_tem_premium(user_id):
                alerts.append({
                    'level': 'info',
                    'title': 'Estúdio Premium',
                    'message': 'Salas ilimitadas e mais visibilidade por R$ 49/mês.',
                    'cta_label': 'Conhecer Premium',
                    'cta_url': url_for('assinatura_bp.planos') + '#estudio',
                })

    return alerts[:5]


def show_referral_card(user_id: str) -> bool:
    """Indicação após primeira setlist montada."""
    for band in get_owned_bands(user_id):
        if count_band_setlists(band['id']) > 0:
            return True
    return False
