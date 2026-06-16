"""Google Ads / GA4 — tag global e conversão de inscrição (cadastro)."""

from __future__ import annotations

import os
import re
from typing import Any

_AW_ID_RE = re.compile(r'^AW-\d+$', re.I)
_GA_ID_RE = re.compile(r'^G-[A-Z0-9]+$', re.I)
_GTM_ID_RE = re.compile(r'^GTM-[A-Z0-9]+$', re.I)


def _env_flag(name: str, default: bool = False) -> bool:
    v = (os.getenv(name) or '').strip().lower()
    if v in ('1', 'true', 'yes', 'on'):
        return True
    if v in ('0', 'false', 'no', 'off'):
        return False
    return default


def _normalize_aw_id(raw: str) -> str:
    s = (raw or '').strip().upper()
    if not s:
        return ''
    if s.startswith('AW-'):
        return s if _AW_ID_RE.match(s) else ''
    digits = re.sub(r'\D', '', s)
    return f'AW-{digits}' if digits else ''


def _normalize_ga_id(raw: str) -> str:
    s = (raw or '').strip().upper()
    return s if _GA_ID_RE.match(s) else ''


def _normalize_gtm_id(raw: str) -> str:
    s = (raw or '').strip().upper()
    return s if _GTM_ID_RE.match(s) else ''


def _signup_send_to(aw_id: str, label: str) -> str:
    lbl = (label or '').strip()
    if not aw_id or not lbl:
        return ''
    if '/' in lbl:
        return lbl if lbl.upper().startswith('AW-') else f'{aw_id}/{lbl.split("/")[-1]}'
    return f'{aw_id}/{lbl}'


def get_google_ads_config() -> dict[str, Any]:
    """Configuração pública (IDs de tag — sem segredos)."""
    aw_id = _normalize_aw_id(os.getenv('GOOGLE_ADS_ID', ''))
    ga_id = _normalize_ga_id(os.getenv('GOOGLE_ANALYTICS_ID', ''))
    gtm_id = _normalize_gtm_id(os.getenv('GOOGLE_TAG_MANAGER_ID', ''))
    signup_label = (os.getenv('GOOGLE_ADS_CONVERSION_SIGNUP') or '').strip()

    enabled_env = _env_flag('GOOGLE_ADS_ENABLED', default=False)
    has_tag = bool(gtm_id or aw_id)
    enabled = enabled_env and has_tag

    value_raw = (os.getenv('GOOGLE_ADS_CONVERSION_VALUE') or '1.0').strip()
    try:
        conversion_value = float(value_raw.replace(',', '.'))
    except ValueError:
        conversion_value = 1.0

    currency = (os.getenv('GOOGLE_ADS_CONVERSION_CURRENCY') or 'BRL').strip().upper() or 'BRL'

    return {
        'enabled': enabled,
        'aw_id': aw_id,
        'ga_id': ga_id,
        'gtm_id': gtm_id,
        'signup_label': signup_label,
        'signup_send_to': _signup_send_to(aw_id, signup_label),
        'conversion_value': conversion_value,
        'conversion_currency': currency,
        'debug': _env_flag('GOOGLE_ADS_DEBUG', default=False),
        'use_gtm': bool(gtm_id),
        'track_signup_direct': bool(aw_id and signup_label and not gtm_id),
    }


def google_ads_ativo() -> bool:
    return get_google_ads_config()['enabled']


def mark_signup_conversion_pending() -> None:
    """Marca conversão de cadastro para disparar na próxima página autenticada."""
    if not google_ads_ativo():
        return
    from flask import session

    session['google_ads_signup_pending'] = True
    session.modified = True


def signup_conversion_path() -> str:
    return '/auth/cadastro-concluido'


def signup_conversion_url() -> str:
    from security import external_url_for
    return external_url_for('auth.cadastro_concluido')


def consume_signup_conversion() -> bool:
    """Consome evento pendente (uma vez por cadastro)."""
    if not google_ads_ativo():
        return False
    from flask import session

    return bool(session.pop('google_ads_signup_pending', None))
