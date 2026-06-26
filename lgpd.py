"""Configuração e helpers LGPD (consentimento, contato do titular)."""

from __future__ import annotations

import os

from flask import session


def privacy_contact_email() -> str:
    return (os.getenv('PRIVACY_CONTACT_EMAIL') or 'contato@setsync.com.br').strip()


def dpo_label() -> str:
    return (os.getenv('PRIVACY_DPO_NAME') or 'Encarregado SetSync').strip()


def tracking_requires_consent() -> bool:
    """True se há scripts de rastreamento/anúncios que exigem opt-in."""
    from adsense import adsense_ativo
    from google_ads import google_ads_ativo, google_analytics_ativo

    return adsense_ativo() or google_ads_ativo() or google_analytics_ativo()


def session_tracking_consent() -> bool | None:
    """None = ainda não escolheu; True/False = decisão do titular."""
    if 'cookie_consent_tracking' not in session:
        return None
    return bool(session.get('cookie_consent_tracking'))


def set_session_tracking_consent(allowed: bool) -> None:
    session['cookie_consent_tracking'] = bool(allowed)
    session.modified = True


def may_load_tracking() -> bool:
    if not tracking_requires_consent():
        return False
    return session_tracking_consent() is True
