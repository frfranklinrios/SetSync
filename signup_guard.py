"""Proteção anti-spam no cadastro (honeypot, rate limit, domínio, gibberish)."""

from __future__ import annotations

import logging
import os
import re
import string
import time
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# Domínios comprovadamente usados em bots/spam neste produto + descartáveis comuns.
_DEFAULT_BLOCKED_EMAIL_DOMAINS = frozenset(
    {
        "immenseignite.info",
        "mailinator.com",
        "guerrillamail.com",
        "guerrillamail.net",
        "sharklasers.com",
        "grr.la",
        "tempmail.com",
        "temp-mail.org",
        "throwaway.email",
        "yopmail.com",
        "trashmail.com",
        "10minutemail.com",
        "getnada.com",
        "dispostable.com",
        "fakeinbox.com",
        "maildrop.cc",
    }
)

_VOWELS = set("aeiouáéíóúãõâêôàü")
_HONEYPOT_FIELDS = ("website", "company_url", "fax_number")

# Mensagem genérica — não ensina o bot o que falhou.
GENERIC_REJECT_MSG = (
    "Não foi possível concluir o cadastro agora. "
    "Tente novamente em alguns minutos ou use outro e-mail."
)


def _csv_env(name: str) -> frozenset[str]:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return frozenset()
    return frozenset(p.strip().lower() for p in raw.split(",") if p.strip())


@lru_cache(maxsize=1)
def blocked_email_domains() -> frozenset[str]:
    return _DEFAULT_BLOCKED_EMAIL_DOMAINS | _csv_env("SETSYNC_BLOCKED_EMAIL_DOMAINS")


def email_domain(email: str) -> str:
    e = (email or "").strip().lower()
    _, _, domain = e.partition("@")
    return domain.strip()


def is_blocked_email_domain(email: str) -> bool:
    return email_domain(email) in blocked_email_domains()


def looks_like_gibberish(text: str | None, *, min_len: int = 8) -> bool:
    """Detecta strings tipo teclado aleatório (ex.: nqfnfmnzuq, rhznzdzgoz)."""
    raw = (text or "").strip()
    if len(raw) < min_len:
        return False
    # Nomes com espaço/acento costumam ser reais.
    if any(ch.isspace() for ch in raw):
        return False
    if any(ch.isdigit() for ch in raw):
        return False
    letters = [ch.lower() for ch in raw if ch.isalpha()]
    if len(letters) < min_len:
        return False
    # Só letras a-z (sem acento) e comprimento típico de bot
    if not all(ch in string.ascii_lowercase for ch in letters):
        return False
    if not (8 <= len(letters) <= 16):
        return False
    unique_ratio = len(set(letters)) / len(letters)
    vowel_count = sum(1 for ch in letters if ch in _VOWELS)
    vowel_ratio = vowel_count / len(letters)
    # Poucas vogais + alta variedade de letras → gibberish
    if vowel_ratio <= 0.34 and unique_ratio >= 0.65:
        return True
    # Sequências de 4+ consoantes (comum em bots)
    if re.search(r"[bcdfghjklmnpqrstvwxyz]{4,}", "".join(letters)):
        if vowel_ratio <= 0.40 and unique_ratio >= 0.55:
            return True
    return False


def honeypot_tripped(form: Any) -> bool:
    for name in _HONEYPOT_FIELDS:
        val = (form.get(name) or "").strip()
        if val:
            return True
    return False


def make_signup_timing_token() -> str:
    """Token assinado com timestamp de exibição do formulário."""
    from flask import current_app
    from itsdangerous import URLSafeTimedSerializer

    s = URLSafeTimedSerializer(current_app.secret_key, salt="signup-timing")
    return s.dumps({"t": time.time()})


def signup_filled_too_fast(token: str | None, *, min_seconds: float = 2.5) -> bool:
    """True se o form foi preenchido rápido demais (bot)."""
    if not token:
        # Sem token: tratar como suspeito em POST (bots que POST direto).
        return True
    try:
        from flask import current_app
        from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

        s = URLSafeTimedSerializer(current_app.secret_key, salt="signup-timing")
        data = s.loads(token, max_age=60 * 60 * 6)
        started = float(data.get("t") or 0)
        if started <= 0:
            return True
        return (time.time() - started) < min_seconds
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return True


def check_signup_abuse(
    *,
    username: str,
    display_name: str,
    email: str,
    form: Any,
    remote_addr: str | None,
) -> tuple[bool, str | None, str | None]:
    """
    Valida proteções de cadastro.

    Returns:
        (ok, flash_message, reason_code)
        ok=False → bloquear; flash_message para o usuário; reason_code para log.
    """
    from security import check_rate_limit

    ip = (remote_addr or "unknown").strip() or "unknown"

    if honeypot_tripped(form):
        logger.warning("signup_blocked reason=honeypot ip=%s email=%s", ip, email)
        # Consome rate limit e falha genérica (não confirma honeypot).
        check_rate_limit(f"signup:{ip}", max_attempts=5, window_sec=3600)
        return False, GENERIC_REJECT_MSG, "honeypot"

    if not check_rate_limit(f"signup:{ip}", max_attempts=5, window_sec=3600):
        logger.warning("signup_blocked reason=rate_limit ip=%s", ip)
        return False, GENERIC_REJECT_MSG, "rate_limit"

    if is_blocked_email_domain(email):
        logger.warning(
            "signup_blocked reason=email_domain ip=%s domain=%s",
            ip,
            email_domain(email),
        )
        return False, GENERIC_REJECT_MSG, "email_domain"

    timing = (form.get("form_ts") or "").strip()
    if signup_filled_too_fast(timing):
        logger.warning("signup_blocked reason=too_fast ip=%s email=%s", ip, email)
        return False, GENERIC_REJECT_MSG, "too_fast"

    user_gib = looks_like_gibberish(username)
    name_gib = looks_like_gibberish(display_name)
    if user_gib and name_gib:
        logger.warning(
            "signup_blocked reason=gibberish ip=%s user=%s name=%s",
            ip,
            username,
            display_name,
        )
        return False, GENERIC_REJECT_MSG, "gibberish"

    return True, None, None
