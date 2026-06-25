#!/usr/bin/env python3
"""Smoke: todas as rotas Flask — espera status < 500 (GET com sessão + IDs reais)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FAILURES: list[str] = []
WARNINGS: list[str] = []
OK_COUNT = 0

# POST que alteram dados ou exigem payload — só checamos se existem na url_map
SKIP_POST = frozenset({
    'auth.logout',
    'bands.delete',
    'bands.invite',
    'bands.remove_member',
    'cifras.delete',
    'cifras.save_transpose',
    'cifras.leadsheet_api_analisar',
    'cifras.leadsheet_api_gerar',
    'cifras.leadsheet_api_salvar',
    'cifras_import.api_processar_cifra',
    'setlists.delete',
    'setlists.remove_cifra',
    'setlists.reorder_ajax',
    'setlists.public_link_manage',
    'setlists.set_vocalist',
    'setlists.set_cifra_vocalist',
    'assinatura_bp.iniciar',
    'assinatura_bp.webhook',
    'assinatura_bp.admin_vouchers_criar',
    'assinatura_bp.admin_vouchers_desativar',
    'assinatura_bp.voucher_resgatar',
    'notifications.api_mark_read',
    'notifications.api_mark_all_read',
    'studios.upload_studio_photo',
    'studios.upload_room_photo',
    'studios.delete_studio_photo_route',
    'studios.confirm_booking',
    'studios.reject_booking',
    'studios.cancel_booking',
    'studios.register_studio',
    'studios.new_room',
    'studios.edit_room',
    'studios.edit_studio',
    'studios.room_availability',
    'studios.room_blocks',
    'studios.book_room',
})

# Redirecionam para Google ou precisam de query especial
SKIP_GET = frozenset({
    'auth.google',
    'auth.google_callback',
    'auth.convite',  # token inválido → redirect ok
    'auth.reset_senha',
    'exportar_setlist_pdf',  # alias legado
})

ACCEPT_STATUS = frozenset({200, 201, 204, 301, 302, 303, 304, 400, 401, 403, 404, 405})


def load_context() -> dict:
    from db import get_user_by_username, get_user_bands, get_band_cifras, is_superadmin
    from models_setlist import get_band_setlists, get_setlist

    ctx: dict = {}
    for uname in ('frfranklin.rios', 'franklin', 'tiagofl'):
        u = get_user_by_username(uname)
        if u:
            ctx['user'] = u
            break
    if not ctx.get('user'):
        from db import get_db
        c = get_db().cursor()
        c.execute('SELECT id, username FROM users LIMIT 1')
        row = c.fetchone()
        if not row:
            raise RuntimeError('Nenhum usuário no banco')
        ctx['user'] = dict(row)

    uid = ctx['user']['id']
    ctx['user_id'] = uid
    ctx['is_superadmin'] = is_superadmin(uid)

    bands = get_user_bands(uid)
    if not bands:
        from db import get_all_bands
        bands = get_all_bands()[:1]
    if not bands:
        raise RuntimeError('Nenhuma banda no banco')
    ctx['band'] = bands[0]
    ctx['band_id'] = bands[0]['id']

    cifras = get_band_cifras(ctx['band_id'])
    ctx['cifra'] = cifras[0] if cifras else None
    ctx['cifra_id'] = cifras[0]['id'] if cifras else '00000000-0000-0000-0000-000000000000'

    sl = get_band_setlists(ctx['band_id'])
    ctx['setlist'] = sl[0] if sl else None
    ctx['setlist_id'] = sl[0]['id'] if sl else 1

    if ctx['setlist']:
        s = get_setlist(ctx['setlist_id'])
        ctx['public_token'] = (s or {}).get('public_share_token') or 'smoke-token'
    else:
        ctx['public_token'] = 'smoke-token'

    c = __import__('db').get_db().cursor()
    c.execute('SELECT codigo FROM vouchers WHERE ativo = 1 LIMIT 1')
    v = c.fetchone()
    ctx['voucher_codigo'] = v['codigo'] if v else 'SMOKE'

    c.execute('SELECT id FROM notifications WHERE user_id = ? LIMIT 1', (uid,))
    n = c.fetchone()
    ctx['notification_id'] = n['id'] if n else '00000000-0000-0000-0000-000000000000'

    ctx['plano'] = 'pro'
    ctx['user_id_to_remove'] = uid
    ctx['job_id'] = 'smoke-job'
    ctx['nome_arquivo'] = 'teste.txt'
    ctx['token'] = 'invalid-token-ok'

    c.execute('SELECT id FROM studios LIMIT 1')
    st = c.fetchone()
    ctx['studio_id'] = st['id'] if st else '00000000-0000-0000-0000-000000000001'
    c.execute('SELECT id FROM studio_rooms LIMIT 1')
    rm = c.fetchone()
    ctx['room_id'] = rm['id'] if rm else '00000000-0000-0000-0000-000000000002'
    c.execute('SELECT id FROM studio_bookings LIMIT 1')
    bk = c.fetchone()
    ctx['booking_id'] = bk['id'] if bk else '00000000-0000-0000-0000-000000000003'

    return ctx


def fill_rule(rule: str, ctx: dict) -> str | None:
    """Substitui placeholders; retorna None se faltar dado obrigatório."""
    if '<cifra_id>' in rule and not ctx.get('cifra'):
        return None
    if '<setlist_id>' in rule and not ctx.get('setlist'):
        return None

    url = rule
    replacements = [
        ('<band_id>', ctx['band_id']),
        ('<cifra_id>', ctx['cifra_id']),
        ('<setlist_id>', str(ctx['setlist_id'])),
        ('<user_id_to_remove>', ctx['user_id_to_remove']),
        ('<token>', ctx.get('public_token') or ctx['token']),
        ('<codigo>', ctx['voucher_codigo']),
        ('<plano>', ctx['plano']),
        ('<notification_id>', ctx['notification_id']),
        ('<job_id>', ctx['job_id']),
        ('<nome_arquivo>', ctx['nome_arquivo']),
        ('<studio_id>', ctx['studio_id']),
        ('<room_id>', ctx['room_id']),
        ('<booking_id>', ctx['booking_id']),
    ]
    for key, val in replacements:
        url = url.replace(key, str(val))
    return url


def run() -> int:
    from app import app

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    print('=== Smoke rotas SetSync ===\n')
    ctx = load_context()
    print(f"Usuário: {ctx['user']['username']} | Banda: {ctx['band']['name']}")
    print(f"Cifra: {'sim' if ctx.get('cifra') else 'não'} | Setlist: {'sim' if ctx.get('setlist') else 'não'}\n")

    global OK_COUNT
    tested = 0

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = ctx['user_id']
            sess['username'] = ctx['user']['username']
            sess['is_superadmin'] = ctx['is_superadmin']
            dn = (ctx['user'].get('display_name') or '').strip()
            sess['display_name'] = dn or ctx['user']['username']

        rules = sorted(app.url_map.iter_rules(), key=lambda r: r.rule)
        for rule in rules:
            if rule.endpoint == 'static':
                continue

            methods = rule.methods - {'HEAD', 'OPTIONS'}
            is_get = 'GET' in methods
            is_post = 'POST' in methods and not is_get

            if is_post:
                if rule.endpoint in SKIP_POST:
                    continue
                method = 'POST'
            elif is_get:
                if rule.endpoint in SKIP_GET:
                    continue
                method = 'GET'
            else:
                continue

            url = fill_rule(rule.rule, ctx)
            if url is None:
                WARNINGS.append(f'SKIP (sem dados) {method} {rule.rule}')
                continue

            tested += 1
            try:
                if method == 'GET':
                    resp = client.get(url, follow_redirects=False)
                else:
                    resp = client.post(url, follow_redirects=False)
            except Exception as e:
                FAILURES.append(f'EXC {method} {url} ({rule.endpoint}): {e}')
                continue

            sc = resp.status_code
            if sc >= 500:
                body = (resp.get_data(as_text=True) or '')[:200]
                FAILURES.append(f'{sc} {method} {url} ({rule.endpoint}) {body!r}')
            elif sc not in ACCEPT_STATUS:
                WARNINGS.append(f'{sc} {method} {url} ({rule.endpoint})')
            else:
                OK_COUNT += 1

        # Rotas públicas sem login
        client.get('/auth/logout', method='POST')  # clear? skip
        with client.session_transaction() as sess:
            sess.clear()

        public_gets = [
            '/', '/health', '/login', '/auth/login', '/auth/register',
            '/ajuda', '/igrejas', '/estudios', '/offline', '/manifest.webmanifest', '/sw.js', '/ads.txt',
            f'/setlists/letras/{ctx.get("public_token", "x")}',
            f'/setlists/compartilhar/{ctx.get("public_token", "x")}',
        ]
        for path in public_gets:
            if path == '/login':
                path = '/auth/login'
            tested += 1
            resp = client.get(path, follow_redirects=False)
            sc = resp.status_code
            if sc >= 500:
                FAILURES.append(f'{sc} GET público {path}')
            else:
                OK_COUNT += 1

    print(f'Testadas: {tested} requisições')
    print(f'OK (status aceito): {OK_COUNT}')
    if WARNINGS:
        print(f'\nAvisos ({len(WARNINGS)}):')
        for w in WARNINGS[:15]:
            print(f'  {w}')
        if len(WARNINGS) > 15:
            print(f'  ... +{len(WARNINGS) - 15}')
    if FAILURES:
        print(f'\nFalhas ({len(FAILURES)}):')
        for f in FAILURES:
            print(f'  {f}')
        return 1
    print('\nTodas as rotas testadas passaram (nenhum erro 5xx).')
    return 0


if __name__ == '__main__':
    raise SystemExit(run())
