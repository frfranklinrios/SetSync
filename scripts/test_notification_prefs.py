"""Testes de preferências de notificação por categoria."""

from notification_prefs import (
    default_notification_prefs,
    notification_category,
    parse_notification_prefs,
)


def test_notification_category_mapping():
    assert notification_category('event_scale_assigned') == 'escalacao'
    assert notification_category('cifra_updated') == 'cifras'
    assert notification_category('admin_user_registered') is None


def test_default_cifras_push_off():
    prefs = default_notification_prefs()
    assert prefs['categories']['escalacao']['push'] is True
    assert prefs['categories']['cifras']['push'] is False


def test_parse_merges_user_prefs():
    raw = '{"categories":{"cifras":{"push":true,"email":false}}}'
    prefs = parse_notification_prefs(raw)
    assert prefs['categories']['cifras']['push'] is True
    assert prefs['categories']['cifras']['email'] is False
    assert prefs['categories']['cifras']['whatsapp'] is True


def test_user_wants_channel_respects_global_and_category():
    from db import user_wants_notification_channel

    user = {
        'push_notify': 1,
        'email_notify': 1,
        'whatsapp_notify': 1,
        'phone': '5511999999999',
        'notification_prefs_json': None,
    }
    assert user_wants_notification_channel(user, 'push', 'event_scale_assigned') is True
    assert user_wants_notification_channel(user, 'push', 'cifra_updated') is False

    user['push_notify'] = 0
    assert user_wants_notification_channel(user, 'push', 'event_scale_assigned') is False


def test_push_payload_includes_icons(monkeypatch=None):
    import json
    import os
    from push_notification_service import _push_payload

    os.environ['SETSYNC_CANONICAL_URL'] = 'https://setsync.com.br'
    payload = json.loads(_push_payload(
        title='Teste',
        body='Corpo',
        url_path='/bands/',
        notification_type='event_scale_assigned',
    ))
    assert payload['icon'] == 'https://setsync.com.br/static/icons/icon-192.png'
    assert payload['badge'] == 'https://setsync.com.br/static/icons/notification-badge.png'


if __name__ == '__main__':
    test_notification_category_mapping()
    test_default_cifras_push_off()
    test_parse_merges_user_prefs()
    test_user_wants_channel_respects_global_and_category()
    test_push_payload_includes_icons()
    print('ok')
