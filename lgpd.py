"""Configuração e helpers LGPD (consentimento, contato do titular)."""

from __future__ import annotations

import os

from flask import current_app, has_request_context, request, session

COOKIE_CONSENT_NAME = "ss_cookie_consent"
COOKIE_CONSENT_MAX_AGE = 365 * 24 * 60 * 60  # 1 ano


def privacy_contact_email() -> str:
    return (os.getenv("PRIVACY_CONTACT_EMAIL") or "contato@unissono.app").strip()


def dpo_label() -> str:
    return (os.getenv("PRIVACY_DPO_NAME") or "Encarregado Uníssono").strip()


def tracking_requires_consent() -> bool:
    """True se há scripts de rastreamento/anúncios que exigem opt-in."""
    from adsense import adsense_ativo
    from google_ads import google_ads_ativo, google_analytics_ativo
    from meta_pixel import meta_pixel_ativo

    return (
        adsense_ativo()
        or google_ads_ativo()
        or google_analytics_ativo()
        or meta_pixel_ativo()
    )


def session_tracking_consent() -> bool | None:
    """None = ainda não escolheu; True/False = decisão do titular."""
    if has_request_context():
        cookie_val = (request.cookies.get(COOKIE_CONSENT_NAME) or "").strip().lower()
        if cookie_val in ("accept", "1", "true"):
            return True
        if cookie_val in ("essential", "reject", "0", "false"):
            return False
    if "cookie_consent_tracking" not in session:
        return None
    return bool(session.get("cookie_consent_tracking"))


def set_session_tracking_consent(allowed: bool) -> None:
    session["cookie_consent_tracking"] = bool(allowed)
    session.modified = True


def apply_consent_cookie(response, allowed: bool) -> None:
    """Persiste a escolha de consentimento por 1 ano fora do cookie de sessão."""
    secure = False
    if has_request_context():
        secure = bool(current_app.config.get("SESSION_COOKIE_SECURE", False))
    response.set_cookie(
        COOKIE_CONSENT_NAME,
        "accept" if allowed else "essential",
        max_age=COOKIE_CONSENT_MAX_AGE,
        path="/",
        samesite="Lax",
        secure=secure,
        httponly=True,
    )


def may_load_tracking() -> bool:
    if not tracking_requires_consent():
        return False
    return session_tracking_consent() is True
