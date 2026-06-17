"""Web Push (VAPID) para Android PWA e iOS 16.4+."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger('setsync.push')


def vapid_private_key() -> str:
    raw = (os.getenv('VAPID_PRIVATE_KEY') or '').strip()
    if '\\n' in raw:
        raw = raw.replace('\\n', '\n')
    return raw


def is_push_configured() -> bool:
    return bool(vapid_public_key() and vapid_private_key())


def vapid_public_key() -> str:
    return (os.getenv('VAPID_PUBLIC_KEY') or '').strip()


def vapid_subject() -> str:
    return (os.getenv('VAPID_SUBJECT') or 'mailto:contato@setsync.com.br').strip()


def _notification_url(url_path: str | None) -> str:
    base = (os.getenv('SETSYNC_CANONICAL_URL') or '').strip().rstrip('/')
    if not url_path:
        return base or '/'
    if url_path.startswith('http://') or url_path.startswith('https://'):
        return url_path
    return f'{base}{url_path}' if base else url_path


def _push_payload(
    *,
    title: str,
    body: str,
    url_path: str | None,
    notification_type: str,
) -> str:
    return json.dumps({
        'title': title,
        'body': body or '',
        'url': url_path or '/',
        'type': notification_type,
    }, ensure_ascii=False)


def send_push_to_subscription(
    subscription: dict[str, Any],
    *,
    title: str,
    body: str = '',
    url_path: str | None = None,
    notification_type: str = '',
) -> bool:
    if not is_push_configured():
        return False
    try:
        from pywebpush import WebPushException, webpush
    except ImportError:
        logger.warning('pywebpush não instalado — push desativado')
        return False

    sub_info = {
        'endpoint': subscription['endpoint'],
        'keys': {
            'p256dh': subscription['p256dh'],
            'auth': subscription['auth'],
        },
    }
    data = _push_payload(
        title=title,
        body=body,
        url_path=url_path,
        notification_type=notification_type,
    )
    try:
        webpush(
            subscription_info=sub_info,
            data=data,
            vapid_private_key=vapid_private_key(),
            vapid_claims={'sub': vapid_subject()},
        )
        return True
    except WebPushException as exc:
        status = getattr(getattr(exc, 'response', None), 'status_code', None)
        if status in (404, 410):
            from db import remove_push_subscription_by_endpoint
            remove_push_subscription_by_endpoint(subscription['endpoint'])
            logger.info('Subscription push removida (HTTP %s)', status)
        else:
            logger.warning('Falha push %s: %s', subscription.get('endpoint', '')[:48], exc)
        return False
    except Exception:
        logger.exception('Erro ao enviar push')
        return False


def dispatch_notification_push(
    user_id: str,
    *,
    notification_type: str,
    title: str,
    body: str = '',
    url_path: str | None = None,
) -> int:
    """Envia push a todos os dispositivos inscritos do usuário."""
    if not is_push_configured() or not user_id:
        return 0
    from db import (
        get_user,
        list_push_subscriptions,
        user_wants_notification_channel,
    )

    user = get_user(user_id)
    if not user or not user_wants_notification_channel(user, 'push', notification_type):
        return 0
    subs = list_push_subscriptions(user_id)
    if not subs:
        return 0

    sent = 0
    for sub in subs:
        if send_push_to_subscription(
            sub,
            title=title,
            body=body,
            url_path=url_path,
            notification_type=notification_type,
        ):
            sent += 1
    return sent
