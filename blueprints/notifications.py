import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, jsonify, session

from blueprints.auth import login_required
from db import (
    count_unread_notifications,
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)

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
    items = list_notifications(user_id, limit=40)
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
