"""Resumo diário de notificações não urgentes (push, e-mail e WhatsApp)."""

from __future__ import annotations

import logging
from html import escape

from db import (
    get_user,
    list_notification_digest_for_user,
    list_pending_notification_digest_user_ids,
    mark_notification_digest_sent,
    user_display_name,
    user_wants_notification_channel,
)
from notification_email_service import send_notification_email
from push_notification_service import dispatch_notification_push
from whatsapp_config import canonical_app_url
from whatsapp_service import normalize_whatsapp_phone, send_whatsapp_text

logger = logging.getLogger('setsync.notification.digest')

_DIGEST_TYPE = 'notification_digest'
_MAX_ITEMS = 12


def _format_digest_lines(entries: list[dict]) -> tuple[str, str, str]:
    """Retorna (title, body_text, body_html)."""
    count = len(entries)
    if count == 1:
        title = entries[0].get('title') or 'Nova atualização'
    else:
        title = f'Resumo do dia — {count} atualizações'

    lines: list[str] = []
    for row in entries[:_MAX_ITEMS]:
        line_title = (row.get('title') or '').strip()
        line_body = (row.get('body') or '').strip()
        if line_body:
            lines.append(f'• {line_title}: {line_body}')
        else:
            lines.append(f'• {line_title}')

    if count > _MAX_ITEMS:
        lines.append(f'• … e mais {count - _MAX_ITEMS}')

    body_text = '\n'.join(lines)
    body_html = ''.join(f'<p style="margin:0 0 8px">{escape(l)}</p>' for l in lines)
    return title, body_text, body_html


def _channels_for_digest(user: dict, entries: list[dict]) -> set[str]:
    channels: set[str] = set()
    for row in entries:
        ntype = row.get('type') or ''
        for ch in ('push', 'email', 'whatsapp'):
            if user_wants_notification_channel(user, ch, ntype):
                channels.add(ch)
    return channels


def _whatsapp_message(title: str, body: str) -> str:
    base = canonical_app_url() or ''
    link = f'{base}/dashboard' if base else '/dashboard'
    parts = ['*SetSync*', f'*{title}*', body, f'_Abrir no app:_\n{link}']
    return '\n\n'.join(p for p in parts if p)


def send_user_notification_digest(user_id: str) -> bool:
    """Envia resumo pendente a um usuário. Retorna True se enviou algo."""
    entries = list_notification_digest_for_user(user_id, pending_only=True)
    if not entries:
        return False

    user = get_user(user_id)
    if not user:
        mark_notification_digest_sent(user_id)
        return False

    channels = _channels_for_digest(user, entries)
    if not channels:
        mark_notification_digest_sent(user_id)
        return False

    title, body_text, body_html = _format_digest_lines(entries)
    url_path = '/dashboard'
    sent_any = False

    if 'push' in channels:
        try:
            sent = dispatch_notification_push(
                user_id,
                notification_type=_DIGEST_TYPE,
                title=title,
                body=body_text[:240],
                url_path=url_path,
            )
            sent_any = sent_any or sent > 0
        except Exception:
            logger.exception('Falha no push digest para %s', user_id)

    if 'email' in channels:
        email = (user.get('email') or '').strip()
        if email:
            try:
                if send_notification_email(
                    email,
                    title,
                    body_text,
                    url_path,
                ):
                    sent_any = True
            except Exception:
                logger.exception('Falha no e-mail digest para %s', user_id)

    if 'whatsapp' in channels:
        phone = normalize_whatsapp_phone(user.get('phone') or '')
        if phone:
            try:
                if send_whatsapp_text(phone, _whatsapp_message(title, body_text), link_preview=False):
                    sent_any = True
            except Exception:
                logger.exception('Falha no WhatsApp digest para %s', user_id)

    mark_notification_digest_sent(user_id)
    if sent_any:
        logger.info(
            'Digest diário enviado para %s (%d itens, canais %s)',
            user_display_name(user),
            len(entries),
            ','.join(sorted(channels)),
        )
    return sent_any


def send_pending_notification_digests() -> dict[str, int]:
    """Job diário: um resumo por usuário com notificações não urgentes do dia."""
    stats = {'users': 0, 'sent': 0, 'failed': 0, 'skipped': 0}
    for user_id in list_pending_notification_digest_user_ids():
        stats['users'] += 1
        try:
            if send_user_notification_digest(user_id):
                stats['sent'] += 1
            else:
                stats['skipped'] += 1
        except Exception:
            logger.exception('Falha no digest de notificações para %s', user_id)
            stats['failed'] += 1
    return stats
