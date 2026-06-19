#!/usr/bin/env python3
"""Testes de urgência e fila de resumo diário de notificações."""

from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

os.environ.setdefault('DATABASE_URL', f'sqlite:///{tempfile.mkdtemp()}/test.db')


def main() -> int:
    from notification_urgency import is_urgent_notification
    from db import (
        init_db,
        create_user,
        create_band,
        add_band_member,
        create_notification,
        list_notification_digest_for_user,
        list_pending_notification_digest_user_ids,
        get_user,
    )

    assert is_urgent_notification('event_scale_assigned')
    assert is_urgent_notification('band_invite')
    assert not is_urgent_notification('cifra_updated')
    assert not is_urgent_notification('setlist_created')
    assert is_urgent_notification('member_removed', urgent=True)

    init_db()
    uid = create_user('notify@test.com', 'notify@test.com', 'hash', display_name='Notify User')
    band_id = create_band('Banda', '', uid)
    add_band_member(band_id, uid, 'owner')
    user = get_user(uid)
    user['email_notify'] = 1
    user['whatsapp_notify'] = 1
    user['push_notify'] = 1
    user['phone'] = '5511999999999'

    create_notification(
        uid,
        band_id=band_id,
        actor_user_id=uid,
        type='cifra_created',
        title='Nova cifra',
        body='Teste de digest',
        url_path='/dashboard',
    )

    pending = list_notification_digest_for_user(uid, pending_only=True)
    assert len(pending) == 1, 'cifra_created deve ir para fila do resumo'
    assert uid in list_pending_notification_digest_user_ids()

    create_notification(
        uid,
        band_id=band_id,
        actor_user_id=None,
        type='band_invite',
        title='Convite urgente',
        body='Aceite agora',
        url_path='/convites',
    )

    pending_after = list_notification_digest_for_user(uid, pending_only=True)
    assert len(pending_after) == 1, 'urgente não entra na fila'

    print('ok urgência e fila de digest')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
