"""Contexto e métricas do painel do administrador master."""

from __future__ import annotations

from db import (
    count_users_without_band,
    get_all_bands,
    get_all_cifras,
    get_all_users,
    get_band_cifras,
    get_band_members,
    get_user,
    list_users_without_band,
)
from models_studio import enrich_studios_for_admin, list_all_studios
from product_funnel import funnel_activation_rows
from whatsapp_service import is_configured as whatsapp_configured


def build_admin_dashboard_context() -> dict:
    users = get_all_users()
    bands = get_all_bands()
    cifras = get_all_cifras()
    studios = enrich_studios_for_admin(list_all_studios())
    users_no_band = count_users_without_band()
    stuck_users = list_users_without_band(10)

    for band in bands:
        owner = get_user(band['owner_id'])
        band['owner'] = owner or {}
        band['members_count'] = len(get_band_members(band['id']))
        band['cifras_count'] = len(get_band_cifras(band['id']))

    return {
        'stats': {
            'bands': len(bands),
            'cifras': len(cifras),
            'users': len(users),
            'studios': len(studios),
            'users_no_band': users_no_band,
        },
        'funnel_rows': funnel_activation_rows(users_total=len(users)),
        'stuck_users': stuck_users,
        'whatsapp_configured': whatsapp_configured(),
    }
