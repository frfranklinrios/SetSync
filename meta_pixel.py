"""Meta Pixel + Conversions API — inscrição e palco real."""

from __future__ import annotations

import hashlib
import logging
import os
import re
import threading
import time
import uuid
from typing import Any

_PIXEL_ID_RE = re.compile(r'^\d{5,20}$')
_DEFAULT_PIXEL = '1577987043861182'
log = logging.getLogger('unissono.meta_pixel')


def get_meta_pixel_id() -> str:
    raw = (os.getenv('META_PIXEL_ID') or _DEFAULT_PIXEL).strip()
    return raw if _PIXEL_ID_RE.match(raw) else ''


def meta_pixel_ativo() -> bool:
    return bool(get_meta_pixel_id())


def _env_flag(name: str, default: bool = False) -> bool:
    v = (os.getenv(name) or '').strip().lower()
    if v in ('1', 'true', 'yes', 'on'):
        return True
    if v in ('0', 'false', 'no', 'off'):
        return False
    return default


def _sha256(value: str) -> str:
    return hashlib.sha256((value or '').strip().lower().encode('utf-8')).hexdigest()


def _phone_digits(phone_raw: str) -> str:
    from whatsapp_service import normalize_whatsapp_phone

    digits = normalize_whatsapp_phone(phone_raw) or ''
    if not digits:
        return ''
    if not digits.startswith('55') and len(digits) >= 10:
        digits = '55' + digits
    return digits


def capture_fbclid() -> None:
    """Guarda fbclid do anúncio para montar fbc na conversão."""
    from flask import request, session

    fbclid = (request.args.get('fbclid') or '').strip()
    if not fbclid or len(fbclid) > 200:
        return
    session['fbclid'] = fbclid
    session['fbclid_ts'] = int(time.time())
    session.modified = True


def _fbc_from_session() -> str:
    from flask import request, session

    cookie = (request.cookies.get('_fbc') or '').strip()
    if cookie:
        return cookie
    fbclid = (session.get('fbclid') or '').strip()
    if not fbclid:
        return ''
    ts = int(session.get('fbclid_ts') or time.time())
    return f'fb.1.{ts * 1000}.{fbclid}'


def _client_ip() -> str:
    from flask import request

    forwarded = (request.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
    return forwarded or (request.remote_addr or '')


def mark_post_signup_landing() -> None:
    from flask import session

    session['meta_post_signup_landing'] = True
    session.modified = True


def consume_post_signup_landing() -> bool:
    from flask import session

    pending = bool(session.pop('meta_post_signup_landing', None))
    if pending:
        session.modified = True
    return pending


def mark_complete_registration_pending(event_id: str | None = None) -> str:
    from flask import session

    eid = (event_id or '').strip() or str(uuid.uuid4())
    session['meta_complete_registration_pending'] = True
    session['meta_event_id'] = eid
    session.modified = True
    return eid


def consume_complete_registration() -> tuple[bool, str]:
    from flask import session

    pending = bool(session.pop('meta_complete_registration_pending', None))
    event_id = str(session.pop('meta_event_id', '') or '')
    if pending or event_id:
        session.modified = True
    return pending, event_id


def marcar_inscricao(user: dict | None) -> str:
    """Chamar no cadastro novo: marca landing + envia CAPI + evento do Pixel."""
    mark_post_signup_landing()
    if not meta_pixel_ativo():
        return ''
    event_id = mark_complete_registration_pending()
    _enviar_capi_async(user, event_id)
    return event_id


def marcar_play_mode_real(user: dict | None) -> str:
    """Primeiro palco com cifra real — evento custom PlayModeReal (CAPI)."""
    if not meta_pixel_ativo():
        return ''
    from flask import request

    event_id = str(uuid.uuid4())
    path = (request.path or '/cifras/minha-colecao/tocar').strip() or '/cifras/minha-colecao/tocar'
    _enviar_capi_async(
        user,
        event_id,
        event_name='PlayModeReal',
        event_source_path=path,
        custom_data={
            'currency': (os.getenv('GOOGLE_ADS_CONVERSION_CURRENCY') or 'BRL').strip().upper() or 'BRL',
            'value': 1.0,
            'content_name': 'play_mode_real',
        },
    )
    return event_id


def _user_data(user: dict | None) -> dict[str, Any]:
    from flask import request

    data: dict[str, Any] = {
        'client_user_agent': (request.headers.get('User-Agent') or '')[:512],
    }
    ip = _client_ip()
    if ip:
        data['client_ip_address'] = ip
    fbp = (request.cookies.get('_fbp') or '').strip()
    if fbp:
        data['fbp'] = fbp
    fbc = _fbc_from_session()
    if fbc:
        data['fbc'] = fbc
    if user:
        email = (user.get('email') or '').strip()
        if email:
            data['em'] = [_sha256(email)]
        phone = _phone_digits(user.get('phone') or '')
        if phone:
            data['ph'] = [_sha256(phone)]
        uid = str(user.get('id') or '')
        if uid:
            data['external_id'] = [_sha256(uid)]
    return data


def _enviar_capi_async(
    user: dict | None,
    event_id: str,
    *,
    event_name: str = 'CompleteRegistration',
    event_source_path: str = '/auth/cadastro-concluido',
    custom_data: dict[str, Any] | None = None,
) -> None:
    token = (os.getenv('META_CAPI_ACCESS_TOKEN') or '').strip()
    pixel = get_meta_pixel_id()
    if not token or not pixel:
        return
    from flask import request

    path = event_source_path if event_source_path.startswith('/') else f'/{event_source_path}'
    payload = {
        'event_name': event_name,
        'event_time': int(time.time()),
        'event_id': event_id,
        'event_source_url': request.url_root.rstrip('/') + path,
        'action_source': 'website',
        'user_data': _user_data(user),
        'custom_data': custom_data or {
            'currency': (os.getenv('GOOGLE_ADS_CONVERSION_CURRENCY') or 'BRL').strip().upper() or 'BRL',
            'value': 1.0,
            'status': 'completed',
            'content_name': 'signup',
        },
    }
    test_code = (os.getenv('META_CAPI_TEST_EVENT_CODE') or '').strip()
    body: dict[str, Any] = {'data': [payload]}
    if test_code:
        body['test_event_code'] = test_code

    def _run() -> None:
        try:
            import httpx

            url = f'https://graph.facebook.com/v21.0/{pixel}/events'
            with httpx.Client(timeout=8.0) as client:
                res = client.post(url, params={'access_token': token}, json=body)
            if res.status_code >= 400:
                log.warning('Meta CAPI %s: %s', res.status_code, (res.text or '')[:240])
            else:
                log.info('Meta CAPI %s ok event_id=%s', event_name, event_id)
        except Exception:
            log.exception('Meta CAPI falhou')

    threading.Thread(target=_run, name='meta-capi', daemon=True).start()
