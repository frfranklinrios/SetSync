"""Envio de notificações in-app por e-mail (SMTP SetSync)."""

from __future__ import annotations

import logging
import os

from email_service import is_configured, send_email
from security import external_url_for

logger = logging.getLogger('setsync.email_notify')


def _app_base_url() -> str:
    return (os.getenv('SETSYNC_CANONICAL_URL') or '').strip().rstrip('/')


def _notification_link(url_path: str | None) -> str | None:
    if not url_path:
        return _app_base_url() or None
    base = _app_base_url()
    if base:
        return f'{base}{url_path}'
    return url_path


def _html_wrapper(title: str, body_html: str, button_url: str | None, button_label: str) -> str:
    btn = ''
    if button_url:
        btn = (
            f'<p style="margin:24px 0 0">'
            f'<a href="{button_url}" style="display:inline-block;padding:12px 24px;'
            f'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;'
            f'font-weight:600">{button_label}</a></p>'
        )
    return (
        '<div style="font-family:system-ui,sans-serif;color:#1c1917;max-width:520px">'
        f'<p style="color:#78716c;font-size:13px;margin:0 0 8px">SetSync</p>'
        f'<h2 style="margin:0 0 12px;font-size:1.25rem">{title}</h2>'
        f'{body_html}'
        f'{btn}'
        '<p style="margin:28px 0 0;font-size:12px;color:#a8a29e">'
        'Você recebe este e-mail porque ativou alertas no SetSync. '
        'Alertas urgentes (escalação, convites e lembretes) chegam na hora; '
        'demais atualizações vão em um resumo diário. '
        f'<a href="{external_url_for("auth.perfil")}">Ajustar preferências</a>'
        '</p></div>'
    )


def send_notification_email(
    to_email: str,
    title: str,
    body: str = '',
    url_path: str | None = None,
) -> bool:
    link = _notification_link(url_path)
    body_html = f'<p>{body}</p>' if body else ''
    html = _html_wrapper(title, body_html, link, 'Abrir no SetSync')
    text_lines = [title]
    if body:
        text_lines.append(body)
    if link:
        text_lines.append(link)
    text = '\n\n'.join(text_lines)
    return send_email([to_email], f'SetSync — {title}', html, text)


def dispatch_notification_email(
    user_id: str,
    *,
    title: str,
    body: str = '',
    url_path: str | None = None,
    notification_type: str = '',
) -> bool:
    """Envia e-mail ao usuário se tiver opt-in e SMTP configurado."""
    if not is_configured() or not user_id:
        return False
    from db import get_user, user_wants_notification_channel

    user = get_user(user_id)
    if not user or not user_wants_notification_channel(user, 'email', notification_type):
        return False
    email = (user.get('email') or '').strip()
    if not email:
        return False
    try:
        return send_notification_email(email, title, body, url_path)
    except Exception:
        logger.exception('Falha ao enviar notificação por e-mail para %s', user_id)
        return False
