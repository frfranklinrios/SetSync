#!/usr/bin/env python3
"""Valida GOOGLE_MAPS_API_KEY (Places, Embed e restrição de referrer)."""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, '.env'), override=True)

import requests  # noqa: E402

from agenda_maps import google_maps_api_key  # noqa: E402


def _status(label: str, ok: bool, detail: str = '') -> None:
    mark = '✓' if ok else '✗'
    print(f'{mark} {label}' + (f' — {detail}' if detail else ''))


def main() -> None:
    key = google_maps_api_key()
    if not key:
        print('✗ GOOGLE_MAPS_API_KEY não definida no .env')
        raise SystemExit(1)

    print(f'Chave: {key[:8]}…{key[-4:]} ({len(key)} caracteres)')
    if len(key) != 39:
        print('⚠ Comprimento incomum — confira se não há texto extra na linha do .env')

    # Places (servidor)
    r = requests.get(
        'https://maps.googleapis.com/maps/api/place/autocomplete/json',
        params={'input': 'igreja', 'key': key, 'language': 'pt-BR'},
        timeout=20,
    )
    data = r.json()
    places_ok = data.get('status') == 'OK'
    _status('Places API (servidor)', places_ok, data.get('error_message') or data.get('status', ''))

    # Embed (servidor)
    er = requests.get(
        'https://www.google.com/maps/embed/v1/place',
        params={'key': key, 'q': 'Fortaleza', 'language': 'pt-BR'},
        timeout=20,
    )
    embed_ok = er.status_code == 200 and 'rejected your request' not in er.text.lower()
    _status('Maps Embed API (servidor)', embed_ok, f'HTTP {er.status_code}')

    # JavaScript API — simula browser com domínio de produção
    hosts = [
        h.strip()
        for h in (os.getenv('SETSYNC_ALLOWED_HOSTS') or 'setsync.com.br').split(',')
        if h.strip() and h.strip() not in ('localhost', '127.0.0.1')
    ]
    referer = f'https://{hosts[0]}/' if hosts else 'https://setsync.com.br/'
    jr = requests.get(
        'https://maps.googleapis.com/maps/api/js',
        params={'key': key, 'libraries': 'places'},
        headers={'Referer': referer},
        timeout=20,
    )
    js_body = jr.text
    auth_err = 'UrlAuthenticationCommonError' in js_body or 'RefererNotAllowedMapError' in js_body
    invalid = 'InvalidKey' in js_body and 'google.maps.Load' not in js_body[:500]
    js_ok = jr.status_code == 200 and not auth_err and not invalid
    if auth_err:
        _status(
            'Maps JavaScript API (navegador)',
            False,
            f'referrer bloqueado para {referer} — adicione https://{hosts[0] or "seu-dominio"}/* na chave GCP',
        )
    else:
        _status('Maps JavaScript API (navegador)', js_ok, referer)

    print()
    if not (places_ok and embed_ok and js_ok):
        print('Ajuste no Google Cloud Console → Credenciais → sua chave:')
        print('  1. Restrição HTTP: https://setsync.com.br/*, https://www.setsync.com.br/*, https://setsync.dados.tec.br/*')
        print('  2. APIs: Maps JavaScript API, Places API, Maps Embed API')
        print('  3. Faturamento ativo no projeto')
        print('Depois: docker compose -f docker-compose.prod.yml up -d --force-recreate web')
        raise SystemExit(1)

    print('Tudo OK para autocomplete e mapa embutido na agenda.')


if __name__ == '__main__':
    main()
