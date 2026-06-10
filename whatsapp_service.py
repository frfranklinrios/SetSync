"""Envio de notificações por WhatsApp (Evolution API ou Meta Cloud API)."""

from __future__ import annotations

import logging
import re
from typing import Any

import requests

from whatsapp_config import (
    canonical_app_url,
    whatsapp_api_token,
    whatsapp_api_version,
    whatsapp_notifications_enabled,
    whatsapp_phone_number_id,
    whatsapp_provider,
    whatsapp_template_name,
)

logger = logging.getLogger('setsync.whatsapp')


def _meta_configured() -> bool:
    return bool(whatsapp_api_token() and whatsapp_phone_number_id())


def _evolution_configured() -> bool:
    from whatsapp_server.config import evolution_api_key

    return bool(evolution_api_key())


def is_configured() -> bool:
    if not whatsapp_notifications_enabled():
        return False
    provider = whatsapp_provider()
    if provider == 'meta':
        return _meta_configured()
    return _evolution_configured()


def normalize_whatsapp_phone(raw: str | None) -> str | None:
    """Normaliza para E.164 sem '+' (ex.: 5511999999999)."""
    digits = re.sub(r'\D', '', raw or '')
    if not digits:
        return None
    if digits.startswith('55'):
        if len(digits) >= 12:
            return digits
        return None
    if 10 <= len(digits) <= 11:
        return '55' + digits
    if len(digits) >= 12:
        return digits
    return None


def format_whatsapp_display(phone: str | None) -> str:
    """Formata número armazenado para exibição (ex.: +55 (11) 99999-9999)."""
    digits = re.sub(r'\D', '', phone or '')
    if not digits:
        return ''
    if digits.startswith('55') and len(digits) >= 12:
        ddd = digits[2:4]
        rest = digits[4:]
        if len(rest) == 9:
            return f'+55 ({ddd}) {rest[:5]}-{rest[5:]}'
        if len(rest) == 8:
            return f'+55 ({ddd}) {rest[:4]}-{rest[4:]}'
    return f'+{digits}'


def _format_notification_text(title: str, body: str, url_path: str | None) -> str:
    lines = ['*SetSync*', f'*{title}*']
    if body:
        lines.append(body)
    base = canonical_app_url()
    if url_path and base:
        lines.append(f'{base}{url_path}')
    elif url_path:
        lines.append(url_path)
    return '\n\n'.join(lines)


# ── Meta Cloud API ────────────────────────────────────────────────────────────

def _meta_api_url() -> str:
    pid = whatsapp_phone_number_id()
    ver = whatsapp_api_version()
    return f'https://graph.facebook.com/{ver}/{pid}/messages'


def _meta_post(payload: dict[str, Any]) -> bool:
    try:
        resp = requests.post(
            _meta_api_url(),
            headers={
                'Authorization': f'Bearer {whatsapp_api_token()}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=20,
        )
        if resp.ok:
            return True
        logger.error(
            'WhatsApp Meta API erro %s: %s',
            resp.status_code,
            (resp.text or '')[:500],
        )
        return False
    except Exception:
        logger.exception('Falha ao enviar WhatsApp (Meta)')
        return False


def send_whatsapp_template(to_phone: str, title: str, body: str, link: str) -> bool:
    phone = normalize_whatsapp_phone(to_phone)
    template = whatsapp_template_name()
    if not phone or not template:
        return False
    params = [
        {'type': 'text', 'text': (title or 'SetSync')[:200]},
        {'type': 'text', 'text': (body or ' ')[:800]},
        {'type': 'text', 'text': (link or canonical_app_url() or 'setsync.com.br')[:200]},
    ]
    return _meta_post({
        'messaging_product': 'whatsapp',
        'to': phone,
        'type': 'template',
        'template': {
            'name': template,
            'language': {'code': 'pt_BR'},
            'components': [{'type': 'body', 'parameters': params}],
        },
    })


def _send_meta_text(to_phone: str, text: str) -> bool:
    phone = normalize_whatsapp_phone(to_phone)
    if not phone or not text.strip():
        return False
    return _meta_post({
        'messaging_product': 'whatsapp',
        'to': phone,
        'type': 'text',
        'text': {'preview_url': True, 'body': text[:4096]},
    })


# ── Evolution API (servidor local) ──────────────────────────────────────────────

def _send_evolution_text(to_phone: str, text: str) -> bool:
    from whatsapp_server.client import send_text

    phone = normalize_whatsapp_phone(to_phone)
    if not phone:
        return False
    return send_text(phone, text)


# ── API pública ───────────────────────────────────────────────────────────────

def send_whatsapp_text(to_phone: str, text: str) -> bool:
    if not is_configured():
        logger.warning('WhatsApp não configurado; mensagem não enviada')
        return False
    if whatsapp_provider() == 'meta':
        return _send_meta_text(to_phone, text)
    return _send_evolution_text(to_phone, text)


def send_notification_message(to_phone: str, title: str, body: str, url_path: str | None) -> bool:
    base = canonical_app_url()
    link = f'{base}{url_path}' if base and url_path else (url_path or base or '')
    if whatsapp_provider() == 'meta' and whatsapp_template_name():
        return send_whatsapp_template(to_phone, title, body, link)
    text = _format_notification_text(title, body, url_path)
    return send_whatsapp_text(to_phone, text)


def dispatch_notification_whatsapp(
    user_id: str,
    *,
    title: str,
    body: str = '',
    url_path: str | None = None,
) -> bool:
    """Envia WhatsApp ao usuário se tiver telefone e opt-in ativo."""
    if not is_configured() or not user_id:
        return False
    from db import get_user, user_wants_whatsapp_notifications

    user = get_user(user_id)
    if not user or not user_wants_whatsapp_notifications(user):
        return False
    phone = user.get('phone') or ''
    if not phone:
        return False
    return send_notification_message(phone, title, body, url_path)


def provider_status() -> dict[str, Any]:
    """Status para painel admin."""
    provider = whatsapp_provider()
    out: dict[str, Any] = {
        'provider': provider,
        'enabled': whatsapp_notifications_enabled(),
        'configured': is_configured(),
    }
    if provider == 'meta':
        out['connected'] = _meta_configured()
        return out
    from whatsapp_server.client import connection_state, is_connected, is_reachable
    from whatsapp_server.config import evolution_api_url, evolution_instance

    out['api_url'] = evolution_api_url()
    out['instance'] = evolution_instance()
    out['api_reachable'] = is_reachable()
    out['connected'] = is_connected() if out['api_reachable'] else False
    out['connection'] = connection_state() if out['api_reachable'] else {}
    return out
