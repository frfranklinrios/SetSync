"""Resumo diário de edições de cifra por WhatsApp (um envio por dia)."""

from __future__ import annotations

import logging
from collections import defaultdict

from db import (
    list_pending_whatsapp_cifra_digest_user_ids,
    list_whatsapp_cifra_digest_for_user,
    mark_whatsapp_cifra_digest_sent,
    user_display_name,
    get_user,
)
from whatsapp_config import canonical_app_url
from whatsapp_service import send_whatsapp_text, normalize_whatsapp_phone

logger = logging.getLogger('setsync.whatsapp.digest')


def _format_digest_text(entries: list[dict]) -> tuple[str, str]:
    """Retorna (title, body) para o resumo do dia."""
    by_band: dict[str, list[str]] = defaultdict(list)
    for row in entries:
        band = (row.get('band_name') or 'Banda').strip()
        titulo = (row.get('titulo') or 'Cifra').strip()
        if titulo not in by_band[band]:
            by_band[band].append(titulo)

    if len(by_band) == 1:
        band_name = next(iter(by_band))
        title = f'{band_name} — cifras editadas hoje'
    else:
        title = 'Cifras editadas hoje'

    lines: list[str] = []
    for band_name in sorted(by_band):
        titulos = by_band[band_name]
        if len(by_band) > 1:
            lines.append(f'*{band_name}*')
        for t in titulos:
            lines.append(f'• «{t}»')
        if len(by_band) > 1:
            lines.append('')

    body = '\n'.join(lines).strip()
    if len(entries) == 1:
        body = f'Houve 1 alteração no repertório.\n\n{body}'
    else:
        body = f'Houve {len(entries)} alterações no repertório.\n\n{body}'
    return title, body


def _format_whatsapp_message(title: str, body: str) -> str:
    base = canonical_app_url() or ''
    link = f'{base}/dashboard' if base else '/dashboard'
    parts = ['*SetSync*', f'*{title}*', body, f'_Abrir no app:_\n{link}']
    return '\n\n'.join(p for p in parts if p)


def send_user_cifra_digest(user_id: str) -> bool:
    """Envia resumo pendente a um usuário. Retorna True se enviou."""
    from db import user_wants_whatsapp_notifications

    entries = list_whatsapp_cifra_digest_for_user(user_id, pending_only=True)
    if not entries:
        return False

    user = get_user(user_id)
    if not user or not user_wants_whatsapp_notifications(user):
        mark_whatsapp_cifra_digest_sent(user_id)
        return False

    phone = normalize_whatsapp_phone(user.get('phone') or '')
    if not phone:
        mark_whatsapp_cifra_digest_sent(user_id)
        return False

    title, body = _format_digest_text(entries)
    text = _format_whatsapp_message(title, body)
    if not send_whatsapp_text(phone, text, link_preview=False):
        return False

    mark_whatsapp_cifra_digest_sent(user_id)
    logger.info(
        'Digest cifra enviado para %s (%d itens)',
        user_display_name(user),
        len(entries),
    )
    return True


def send_pending_cifra_digests() -> dict[str, int]:
    """Job diário: um WhatsApp por usuário com resumo das edições do dia."""
    stats = {'users': 0, 'sent': 0, 'failed': 0, 'skipped': 0}
    for user_id in list_pending_whatsapp_cifra_digest_user_ids():
        stats['users'] += 1
        try:
            if send_user_cifra_digest(user_id):
                stats['sent'] += 1
            else:
                stats['skipped'] += 1
        except Exception:
            logger.exception('Falha no digest de cifra para %s', user_id)
            stats['failed'] += 1
    return stats
