import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, jsonify, request, session

from blueprints.auth import login_required
from db import (
    count_push_subscriptions,
    count_unread_notifications,
    delete_push_subscription,
    get_user,
    get_user_notification_prefs,
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    save_push_subscription,
    update_user_profile,
)
from notification_prefs import NOTIFICATION_CATEGORIES
from push_notification_service import is_push_configured, vapid_public_key

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


def _serialize(items):
    out = []
    for n in items:
        out.append({
            'id': n['id'],
            'type': n['type'],
            'title': n['title'],
            'body': n['body'],
            'url': n.get('url_path') or '',
            'band_id': n.get('band_id'),
            'band_name': n.get('band_name'),
            'actor_name': n.get('actor_name') or '',
            'read': bool(n.get('read_at')),
            'created_at': n.get('created_at'),
        })
    return out


@notifications_bp.route('/api/list')
@login_required
def api_list():
    user_id = session['user_id']
    from db import is_superadmin
    limit = 50 if is_superadmin(user_id) else 40
    items = list_notifications(user_id, limit=limit)
    return jsonify({
        'items': _serialize(items),
        'unread': count_unread_notifications(user_id),
    })


@notifications_bp.route('/api/unread-count')
@login_required
def api_unread_count():
    return jsonify({'unread': count_unread_notifications(session['user_id'])})


@notifications_bp.route('/api/<notification_id>/read', methods=['POST'])
@login_required
def api_mark_read(notification_id):
    ok = mark_notification_read(notification_id, session['user_id'])
    return jsonify({
        'ok': ok,
        'unread': count_unread_notifications(session['user_id']),
    })


@notifications_bp.route('/api/read-all', methods=['POST'])
@login_required
def api_mark_all_read():
    n = mark_all_notifications_read(session['user_id'])
    return jsonify({'ok': True, 'marked': n, 'unread': 0})


@notifications_bp.route('/api/push/vapid-key')
@login_required
def api_push_vapid_key():
    if not is_push_configured():
        return jsonify({'ok': False, 'error': 'push_not_configured'}), 503
    return jsonify({'ok': True, 'publicKey': vapid_public_key()})


@notifications_bp.route('/api/push/status')
@login_required
def api_push_status():
    user = get_user(session['user_id'])
    return jsonify({
        'ok': True,
        'configured': is_push_configured(),
        'push_notify': bool(user and int(user.get('push_notify') or 0) == 1),
        'subscriptions': count_push_subscriptions(session['user_id']),
    })


@notifications_bp.route('/api/push/subscribe', methods=['POST'])
@login_required
def api_push_subscribe():
    if not is_push_configured():
        return jsonify({'ok': False, 'error': 'push_not_configured'}), 503
    data = request.get_json(silent=True) or {}
    endpoint = (data.get('endpoint') or '').strip()
    keys = data.get('keys') or {}
    p256dh = (keys.get('p256dh') or '').strip()
    auth = (keys.get('auth') or '').strip()
    if not endpoint or not p256dh or not auth:
        return jsonify({'ok': False, 'error': 'invalid_subscription'}), 400

    user_id = session['user_id']
    save_push_subscription(
        user_id,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth,
        user_agent=(request.headers.get('User-Agent') or '')[:500],
    )
    update_user_profile(user_id, push_notify=True)
    return jsonify({
        'ok': True,
        'subscriptions': count_push_subscriptions(user_id),
    })


@notifications_bp.route('/api/push/unsubscribe', methods=['POST'])
@login_required
def api_push_unsubscribe():
    data = request.get_json(silent=True) or {}
    endpoint = (data.get('endpoint') or '').strip()
    user_id = session['user_id']
    if endpoint:
        delete_push_subscription(user_id, endpoint)
    else:
        from db import delete_all_push_subscriptions
        delete_all_push_subscriptions(user_id)
        update_user_profile(user_id, push_notify=False)
    return jsonify({
        'ok': True,
        'subscriptions': count_push_subscriptions(user_id),
    })


@notifications_bp.route('/api/prefs')
@login_required
def api_prefs():
    user = get_user(session['user_id'])
    return jsonify({
        'ok': True,
        'push_notify': bool(user and int(user.get('push_notify') or 0) == 1),
        'email_notify': bool(user and (user.get('email_notify') is None or int(user.get('email_notify') or 0) == 1)),
        'whatsapp_notify': bool(user and (user.get('whatsapp_notify') is None or int(user.get('whatsapp_notify') or 0) == 1)),
        'prefs': get_user_notification_prefs(user),
        'categories': {
            cat_id: {
                'label': meta['label'],
                'description': meta.get('description', ''),
            }
            for cat_id, meta in NOTIFICATION_CATEGORIES.items()
        },
    })
