"""Cliente HTTP para Evolution API (WhatsApp Baileys)."""

from __future__ import annotations

import logging
from typing import Any

import requests

from whatsapp_server.config import evolution_api_key, evolution_api_url, evolution_instance

logger = logging.getLogger('setsync.whatsapp.evolution')

_TIMEOUT = 25


def _headers() -> dict[str, str]:
    key = evolution_api_key()
    return {'apikey': key, 'Content-Type': 'application/json'}


def _request(method: str, path: str, **kwargs) -> requests.Response | None:
    url = f'{evolution_api_url()}{path}'
    try:
        return requests.request(method, url, headers=_headers(), timeout=_TIMEOUT, **kwargs)
    except Exception:
        logger.exception('Evolution API indisponível: %s %s', method, path)
        return None


def is_reachable() -> bool:
    resp = _request('GET', '/')
    if resp is None:
        return False
    return resp.status_code < 500


def fetch_instances() -> list[dict[str, Any]]:
    resp = _request('GET', '/instance/fetchInstances')
    if resp is None or not resp.ok:
        return []
    try:
        data = resp.json()
    except ValueError:
        return []
    if isinstance(data, list):
        return data
    return data.get('instances') or []


def instance_exists(name: str | None = None) -> bool:
    inst = name or evolution_instance()
    for row in fetch_instances():
        if (row.get('name') or row.get('instanceName')) == inst:
            return True
    return False


def ensure_instance() -> bool:
    """Cria a instância SetSync se ainda não existir."""
    inst = evolution_instance()
    if instance_exists(inst):
        return True
    resp = _request(
        'POST',
        '/instance/create',
        json={
            'instanceName': inst,
            'integration': 'WHATSAPP-BAILEYS',
            'qrcode': True,
        },
    )
    if resp is None:
        return False
    if resp.ok:
        logger.info('Instância Evolution criada: %s', inst)
        return True
    if resp.status_code == 403 and 'already in use' in (resp.text or '').lower():
        return True
    logger.error('Falha ao criar instância %s: %s %s', inst, resp.status_code, resp.text[:300])
    return False


def connection_state(name: str | None = None) -> dict[str, Any]:
    inst = name or evolution_instance()
    resp = _request('GET', f'/instance/connectionState/{inst}')
    if resp is None or not resp.ok:
        return {'state': 'unavailable', 'instance': inst}
    try:
        data = resp.json()
    except ValueError:
        return {'state': 'unknown', 'instance': inst}
    if isinstance(data, dict) and 'instance' in data:
        return data
    return {'instance': data, 'state': data.get('state', 'unknown')}


def _normalize_state(raw: Any) -> str:
    if raw is None:
        return ''
    if isinstance(raw, dict):
        return _normalize_state(raw.get('state') or raw.get('connectionStatus'))
    return str(raw).lower()


def is_connected(name: str | None = None) -> bool:
    inst = name or evolution_instance()
    for row in fetch_instances():
        row_name = row.get('name') or row.get('instanceName')
        if row_name != inst:
            continue
        status = _normalize_state(row.get('connectionStatus'))
        if status in ('open', 'connected'):
            return True
    data = connection_state(inst)
    state = _normalize_state(data.get('state'))
    if isinstance(data.get('instance'), dict):
        state = state or _normalize_state(data['instance'])
    return state in ('open', 'connected')


def fetch_qrcode(name: str | None = None) -> dict[str, Any]:
    """Retorna QR em base64 para parear o número (com retentativas)."""
    import time

    inst = name or evolution_instance()
    ensure_instance()
    last_error = 'QR não gerado'
    for _ in range(8):
        resp = _request('GET', f'/instance/connect/{inst}')
        if resp is None:
            return {'ok': False, 'error': 'API indisponível'}
        try:
            data = resp.json()
        except ValueError:
            return {'ok': False, 'error': resp.text[:200]}
        if not resp.ok:
            return {'ok': False, 'error': data if isinstance(data, str) else str(data)}
        qrcode = data.get('qrcode') if isinstance(data.get('qrcode'), dict) else {}
        base64 = data.get('base64') or qrcode.get('base64')
        pairing = data.get('pairingCode') or qrcode.get('pairingCode')
        code = data.get('code') or qrcode.get('code')
        if base64 or pairing or code:
            if base64 and not str(base64).startswith('data:'):
                base64 = f'data:image/png;base64,{base64}'
            return {
                'ok': True,
                'base64': base64,
                'pairingCode': pairing,
                'code': code,
            }
        last_error = f'aguardando QR (count={data.get("count", qrcode.get("count", "?"))})'
        time.sleep(2)
    return {'ok': False, 'error': last_error}


def logout_instance(name: str | None = None) -> bool:
    inst = name or evolution_instance()
    resp = _request('DELETE', f'/instance/logout/{inst}')
    return resp is not None and resp.ok


def send_text(
    phone: str,
    text: str,
    name: str | None = None,
    *,
    link_preview: bool = False,
) -> bool:
    inst = name or evolution_instance()
    if not phone or not text.strip():
        return False
    if not is_connected(inst):
        logger.warning('WhatsApp não conectado (instância %s)', inst)
        return False
    text_body = text[:4096]
    payloads: list[dict[str, Any]] = [
        {'number': phone, 'text': text_body, 'linkPreview': bool(link_preview)},
        {'number': phone, 'text': text_body},
    ]
    last_resp = None
    for payload in payloads:
        last_resp = _request('POST', f'/message/sendText/{inst}', json=payload)
        if last_resp is None:
            return False
        if last_resp.ok:
            return True
        if last_resp.status_code not in (400, 422):
            break
    logger.error(
        'Evolution sendText erro %s: %s',
        last_resp.status_code if last_resp else '?',
        ((last_resp.text if last_resp else '') or '')[:500],
    )
    return False
