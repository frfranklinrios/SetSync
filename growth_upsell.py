"""Alertas contextuais de upgrade no dashboard."""

from __future__ import annotations

from flask import url_for

from db import count_band_cifras, count_band_members, count_band_setlists, get_owned_bands
from monetizacao import (
    LIMITES_GRATIS,
    PLANOS,
    PLANO_INDIVIDUAL,
    PLANO_PRO,
    PRECO_ESTUDIO_PREMIUM,
    dias_restantes_trial,
    dias_restantes_trial_estudio,
    get_plano_efetivo,
    studio_tem_premium,
    user_pode_compartilhar_cifras,
)

_PRECO_PRO = int(PLANOS[PLANO_PRO].preco_mensal or 29)
_PRECO_INDIVIDUAL = int(PLANOS[PLANO_INDIVIDUAL].preco_mensal or 15)
_PRECO_ESTUDIO = int(PRECO_ESTUDIO_PREMIUM)


def _near_limit_message(current: int, limit: int, recurso: str) -> str | None:
    if current < max(1, limit - 3):
        return None
    if current >= limit:
        return (
            f'Limite do Grátis: {current}/{limit} {recurso}. '
            f'No Pro (R$ {_PRECO_PRO}/mês) isso fica ilimitado + PDF.'
        )
    return (
        f'Você usa {current} de {limit} {recurso}. '
        f'Pro libera tudo por R$ {_PRECO_PRO}/mês — cancele quando quiser.'
    )


def get_dashboard_upsells(user_id: str, *, owned_bands: list | None = None) -> list[dict]:
    """Banners de conversão baseados em uso real."""
    bands = owned_bands if owned_bands is not None else get_owned_bands(user_id)
    alerts: list[dict] = []

    # Solo sem banda: coleção grátis, mas PDF/compartilhar pedem Individual
    if not bands and not user_pode_compartilhar_cifras(user_id):
        from db import count_user_personal_cifras

        n_cifras = count_user_personal_cifras(user_id)
        if n_cifras >= 1:
            alerts.append({
                'level': 'info',
                'title': 'Plano Individual — toca só',
                'message': (
                    f'Você já tem {n_cifras} música(s) na coleção. '
                    f'Individual (R$ {_PRECO_INDIVIDUAL}/mês) libera compartilhar e PDF — '
                    'sem precisar montar banda de ensaio.'
                ),
                'cta_label': f'Assinar Individual — R$ {_PRECO_INDIVIDUAL}',
                'cta_url': url_for('assinatura_bp.planos'),
            })

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
                    'cta_label': f'Assinar Pro — R$ {_PRECO_PRO}',
                    'cta_url': planos_url,
                })

        dias = dias_restantes_trial(band_id)
        if dias is not None and dias <= 7:
            alerts.append({
                'level': 'success' if dias > 3 else 'warning',
                'title': f'Trial Pro — {name}',
                'message': (
                    f'Faltam {dias} dia(s) de Pro. '
                    f'Assine por R$ {_PRECO_PRO}/mês e mantenha PDF + limites liberados.'
                ),
                'cta_label': f'Assinar Pro agora — R$ {_PRECO_PRO}',
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
                    'message': (
                        f'Faltam {dias_st} dia(s) de salas ilimitadas. '
                        f'Premium: R$ {_PRECO_ESTUDIO}/mês.'
                    ),
                    'cta_label': f'Assinar Premium — R$ {_PRECO_ESTUDIO}',
                    'cta_url': url_for('assinatura_bp.planos') + '#estudio',
                })
            elif not studio_tem_premium(user_id):
                alerts.append({
                    'level': 'info',
                    'title': 'Estúdio Premium',
                    'message': (
                        f'Salas ilimitadas, destaque na busca e suporte — '
                        f'R$ {_PRECO_ESTUDIO}/mês.'
                    ),
                    'cta_label': f'Assinar Premium — R$ {_PRECO_ESTUDIO}',
                    'cta_url': url_for('assinatura_bp.planos') + '#estudio',
                })

    return alerts[:5]


def show_referral_card(user_id: str) -> bool:
    """Indicação após primeira setlist OU após usar Modo Tocar."""
    from db import user_play_mode_used

    if user_play_mode_used(user_id):
        return True
    for band in get_owned_bands(user_id):
        if count_band_setlists(band['id']) > 0:
            return True
    return False


def referral_members_url(user_id: str) -> str | None:
    """Primeira banda própria para atalho de convite."""
    bands = get_owned_bands(user_id)
    if not bands:
        return None
    return url_for('bands.members', band_id=bands[0]['id'])
