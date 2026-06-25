"""Google Ads / GA4 — tag global, conversões e funil de inscrição."""

from __future__ import annotations

import hashlib
import os
import re
from typing import Any

_AW_ID_RE = re.compile(r'^AW-\d+$', re.I)
_GA_ID_RE = re.compile(r'^G-[A-Z0-9]+$', re.I)
_GTM_ID_RE = re.compile(r'^GTM-[A-Z0-9]+$', re.I)

_FUNNEL_ENV = {
    'signup': ('GOOGLE_ADS_CONVERSION_SIGNUP', 1.0),
    'primeira_banda': ('GOOGLE_ADS_CONVERSION_PRIMEIRA_BANDA', 5.0),
    'primeira_cifra': ('GOOGLE_ADS_CONVERSION_PRIMEIRA_CIFRA', 10.0),
    'trial_iniciado': ('GOOGLE_ADS_CONVERSION_TRIAL', 15.0),
    'assinatura_paga': ('GOOGLE_ADS_CONVERSION_PAGO', 50.0),
}


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


def _sha256_normalized(value: str) -> str:
    return hashlib.sha256((value or '').strip().lower().encode('utf-8')).hexdigest()


def _phone_e164_digits(phone_raw: str) -> str:
    from whatsapp_service import normalize_whatsapp_phone

    digits = normalize_whatsapp_phone(phone_raw) or ''
    if not digits:
        return ''
    if not digits.startswith('55') and len(digits) >= 10:
        digits = '55' + digits
    return '+' + digits


def enhanced_user_data(user: dict | None) -> dict[str, str]:
    """Dados hasheados para Enhanced Conversions (privacidade)."""
    if not user:
        return {}
    out: dict[str, str] = {}
    email = (user.get('email') or '').strip()
    if email:
        out['sha256_email_address'] = _sha256_normalized(email)
    phone = _phone_e164_digits(user.get('phone') or '')
    if phone:
        out['sha256_phone_number'] = _sha256_normalized(phone)
    return out


def get_google_analytics_id() -> str:
    return _normalize_ga_id(os.getenv('GOOGLE_ANALYTICS_ID', 'G-BKG770S75L'))


def google_analytics_ativo() -> bool:
    return bool(get_google_analytics_id())


def get_google_ads_config() -> dict[str, Any]:
    aw_id = _normalize_aw_id(os.getenv('GOOGLE_ADS_ID', ''))
    ga_id = get_google_analytics_id()
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

    funnel_labels: dict[str, str] = {}
    funnel_values: dict[str, float] = {}
    for key, (env_name, default_val) in _FUNNEL_ENV.items():
        lbl = (os.getenv(env_name) or '').strip()
        if lbl:
            funnel_labels[key] = _signup_send_to(aw_id, lbl)
        funnel_values[key] = default_val
        vraw = (os.getenv(f'{env_name}_VALUE') or '').strip()
        if vraw:
            try:
                funnel_values[key] = float(vraw.replace(',', '.'))
            except ValueError:
                pass

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
        'funnel_labels': funnel_labels,
        'funnel_values': funnel_values,
        'enhanced_conversions': _env_flag('GOOGLE_ADS_ENHANCED', default=True),
    }


def google_ads_ativo() -> bool:
    return get_google_ads_config()['enabled']


def mark_signup_conversion_pending() -> None:
    mark_funnel_event('signup')


def mark_funnel_event(event: str) -> None:
    if not google_ads_ativo():
        return
    from flask import session

    pending = session.get('google_ads_funnel_pending')
    if not isinstance(pending, list):
        pending = []
    if event not in pending:
        pending.append(event)
    session['google_ads_funnel_pending'] = pending
    session.modified = True


def consume_funnel_events() -> list[str]:
    if not google_ads_ativo():
        return []
    from flask import session

    raw = session.pop('google_ads_funnel_pending', None)
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    return [str(raw)]


def signup_conversion_path() -> str:
    return '/auth/cadastro-concluido'


def signup_conversion_url() -> str:
    from security import external_url_for
    return external_url_for('auth.cadastro_concluido')


def consume_signup_conversion() -> bool:
    return 'signup' in consume_funnel_events()
