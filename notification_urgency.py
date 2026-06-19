"""Urgência de notificações — imediatas vs. resumo diário."""

from __future__ import annotations

# Tipos que exigem ação ou atenção imediata (envio na hora em push/e-mail/WhatsApp).
URGENT_NOTIFICATION_TYPES = frozenset({
    'event_scale_assigned',
    'event_scale_substitute_offer',
    'band_invite',
    'event_reminder',
})


def is_urgent_notification(notification_type: str, *, urgent: bool | None = None) -> bool:
    """Define se a notificação deve sair imediatamente nos canais externos."""
    if urgent is True:
        return True
    if urgent is False:
        return False
    if not notification_type:
        return False
    if notification_type.startswith('admin_'):
        return True
    return notification_type in URGENT_NOTIFICATION_TYPES
