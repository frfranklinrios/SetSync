"""Envio de notificações por WhatsApp (Meta Cloud API)."""

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
    whatsapp_template_name,
)

logger = logging.getLogger('setsync.whatsapp')


def is_configured() -> bool:
    return bool(
        whatsapp_notifications_enabled()
        and whatsapp_api_token()
        and whatsapp_phone_number_id()
    )


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


def _api_url() -> str:
    pid = whatsapp_phone_number_id()
    ver = whatsapp_api_version()
    return f'https://graph.facebook.com/{ver}/{pid}/messages'


def _post_message(payload: dict[str, Any]) -> bool:
    if not is_configured():
        logger.warning('WhatsApp API não configurada; mensagem não enviada')
        return False
    try:
        resp = requests.post(
            _api_url(),
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
            'WhatsApp API erro %s: %s',
            resp.status_code,
            (resp.text or '')[:500],
        )
        return False
    except Exception:
        logger.exception('Falha ao enviar WhatsApp')
        return False


def _format_notification_text(title: str, body: str, url_path: str | None) -> str:
    lines = [f'*SetSync*', f'*{title}*']
    if body:
        lines.append(body)
    base = canonical_app_url()
    if url_path and base:
        lines.append(f'{base}{url_path}')
    elif url_path:
        lines.append(url_path)
    return '\n\n'.join(lines)


def send_whatsapp_text(to_phone: str, text: str) -> bool:
    phone = normalize_whatsapp_phone(to_phone)
    if not phone or not text.strip():
        return False
    return _post_message({
        'messaging_product': 'whatsapp',
        'to': phone,
        'type': 'text',
        'text': {'preview_url': True, 'body': text[:4096]},
    })


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
    return _post_message({
        'messaging_product': 'whatsapp',
        'to': phone,
        'type': 'template',
        'template': {
            'name': template,
            'language': {'code': 'pt_BR'},
            'components': [{
                'type': 'body',
                'parameters': params,
            }],
        },
    })


def send_notification_message(to_phone: str, title: str, body: str, url_path: str | None) -> bool:
    base = canonical_app_url()
    link = f'{base}{url_path}' if base and url_path else (url_path or base or '')
    if whatsapp_template_name():
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
