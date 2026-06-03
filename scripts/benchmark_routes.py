#!/usr/bin/env python3
"""Benchmark: latência de rotas críticas (test client com sessão real)."""
from __future__ import annotations

import os
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault('SESSION_COOKIE_SECURE', '0')
os.environ['SETSYNC_CANONICAL_URL'] = ''


def load_ctx() -> dict:
    from db import get_band_cifras, get_user_by_username, get_user_bands, is_superadmin
    from models_setlist import get_band_setlists

    for uname in ('frfranklin.rios', 'franklin', 'tiagofl'):
        u = get_user_by_username(uname)
        if u:
            break
    else:
        raise RuntimeError('sem usuário')
    bands = get_user_bands(u['id'])
    band = bands[0]
    cifras = get_band_cifras(band['id'])
    sl = get_band_setlists(band['id'])
    token = None
    if sl:
        from models_setlist import get_setlist
        s = get_setlist(sl[0]['id'])
        token = (s or {}).get('public_share_token')
    return {
        'user': u,
        'band_id': band['id'],
        'cifra_id': cifras[0]['id'] if cifras else None,
        'setlist_id': sl[0]['id'] if sl else None,
        'public_token': token,
        'is_superadmin': is_superadmin(u['id']),
    }


def bench(client, method: str, path: str, n: int = 3, **kw) -> dict:
    times: list[float] = []
    status = None
    size = 0
    for _ in range(n):
        t0 = time.perf_counter()
        if method == 'GET':
            r = client.get(path, follow_redirects=False, **kw)
        else:
            r = client.post(path, follow_redirects=False, **kw)
        times.append((time.perf_counter() - t0) * 1000)
        status = r.status_code
        size = len(r.get_data())
    return {
        'path': path,
        'status': status,
        'ms_min': min(times),
        'ms_avg': statistics.mean(times),
        'ms_max': max(times),
        'bytes': size,
    }


def main() -> int:
    from app import app

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    ctx = load_ctx()
    u = ctx['user']
    routes = [
        ('GET', '/health'),
        ('GET', '/auth/login'),
        ('GET', '/dashboard'),
        ('GET', f'/bands/{ctx["band_id"]}'),
        ('GET', f'/bands/{ctx["band_id"]}/settings'),
        ('GET', '/cifras/'),
    ]
    if ctx['cifra_id']:
        routes.append(('GET', f'/cifras/{ctx["cifra_id"]}'))
        routes.append(('GET', f'/cifras/{ctx["cifra_id"]}/tocar'))
    if ctx['setlist_id']:
        routes.append(('GET', f'/setlists/{ctx["setlist_id"]}'))
        routes.append(('GET', f'/setlists/{ctx["setlist_id"]}/tocar'))
    if ctx['public_token']:
        routes.append(('GET', f'/setlists/letras/{ctx["public_token"]}'))
        routes.append(('GET', f'/setlists/letras/{ctx["public_token"]}/dados.json'))
    if ctx['is_superadmin']:
        routes.append(('GET', '/admin/'))

    print('=== Benchmark SetSync (3 amostras/rota) ===')
    print(f'Usuário: {u["username"]}\n')
    print(f'{"Rota":<52} {"HTTP":>4} {"ms avg":>8} {"ms max":>8} {"KB":>7}')
    print('-' * 85)

    slow: list[tuple] = []
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = u['id']
            sess['username'] = u['username']
            sess['display_name'] = (u.get('display_name') or u['username']).strip()
            sess['is_superadmin'] = ctx['is_superadmin']

        for method, path in routes:
            row = bench(client, method, path, n=3)
            kb = row['bytes'] / 1024
            print(
                f'{path:<52} {row["status"]:>4} {row["ms_avg"]:>7.0f} '
                f'{row["ms_max"]:>8.0f} {kb:>6.1f}'
            )
            if row['ms_avg'] > 500:
                slow.append((path, row['ms_avg'], row['bytes']))

    if slow:
        print('\n--- Rotas lentas (>500 ms média) ---')
        for path, ms, b in sorted(slow, key=lambda x: -x[1]):
            print(f'  {path}: {ms:.0f} ms ({b/1024:.1f} KB)')
    print()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
