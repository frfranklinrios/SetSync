from __future__ import annotations

import time

from flask import Blueprint, Response, jsonify, request, session, stream_with_context

from blueprints.auth import login_required
from db import is_band_member
from realtime_hub import publish, subscribe, unsubscribe

realtime_bp = Blueprint('realtime', __name__, url_prefix='/api/realtime')


def notify_band(band_id: str, event: str, data: dict | None = None) -> None:
    """Dispara evento SSE para clientes inscritos na banda."""
    if band_id:
        publish(str(band_id), event, data)


@realtime_bp.route('/band/<band_id>/events')
@login_required
def band_events(band_id: str):
    user_id = session.get('user_id')
    if not user_id or not is_band_member(band_id, user_id):
        return Response('forbidden', status=403)

    q = subscribe(band_id)

    @stream_with_context
    def generate():
        try:
            yield ': connected\n\n'
            while True:
                try:
                    msg = q.get(timeout=25)
                    yield f'data: {msg}\n\n'
                except Exception:
                    yield f': keepalive {int(time.time())}\n\n'
        finally:
            unsubscribe(band_id, q)

    resp = Response(generate(), mimetype='text/event-stream')
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['X-Accel-Buffering'] = 'no'
    return resp


@realtime_bp.route('/band/<band_id>/play-state', methods=['POST'])
@login_required
def set_play_state(band_id: str):
    """Publica música atual do Modo Tocar para outros membros da banda (SSE)."""
    user_id = session.get('user_id')
    if not user_id or not is_band_member(band_id, user_id):
        return jsonify({'ok': False, 'error': 'forbidden'}), 403
    data = request.get_json(silent=True) or {}
    song_index = data.get('song_index')
    if song_index is None:
        return jsonify({'ok': False, 'error': 'song_index obrigatório'}), 400
    payload = {
        'setlist_id': data.get('setlist_id'),
        'song_index': int(song_index),
        'cifra_id': data.get('cifra_id'),
        'leader_id': user_id,
        'leader_name': session.get('username') or '',
    }
    publish(str(band_id), 'play_sync', payload)
    return jsonify({'ok': True})
