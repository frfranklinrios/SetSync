#!/usr/bin/env python3
"""Smoke rápido do plano de dono: canônico, hosts, MP, mail DNS, saúde HTTP."""
from __future__ import annotations

import os
import socket
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

load_dotenv(override=True)


def _ok(msg: str) -> None:
    print(f'  ✓ {msg}')


def _warn(msg: str) -> None:
    print(f'  ! {msg}')


def _fail(msg: str) -> None:
    print(f'  ✗ {msg}')


def check_canonical() -> int:
    print('=== Domínio canônico ===')
    canon = (os.getenv('SETSYNC_CANONICAL_URL') or '').strip().rstrip('/')
    hosts = {h.strip().lower() for h in (os.getenv('SETSYNC_ALLOWED_HOSTS') or '').split(',') if h.strip()}
    rc = 0
    if canon == 'https://unissono.app':
        _ok(f'SETSYNC_CANONICAL_URL={canon}')
    else:
        _fail(f'SETSYNC_CANONICAL_URL deveria ser https://unissono.app (atual: {canon or "vazio"})')
        rc = 1
    for h in ('unissono.app', 'www.unissono.app', 'setsync.com.br'):
        if h in hosts:
            _ok(f'ALLOWED_HOSTS contém {h}')
        else:
            _fail(f'ALLOWED_HOSTS sem {h}')
            rc = 1
    return rc


def check_http() -> int:
    print('\n=== HTTP /health ===')
    rc = 0
    for url in (
        'https://unissono.app/health',
        'https://www.unissono.app/health',
        'https://setsync.com.br/health',
    ):
        try:
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=12) as resp:
                body = resp.read().decode('utf-8', errors='replace')
                code = resp.getcode()
                loc = resp.headers.get('Location') or ''
            if code in (200, 301, 302):
                _ok(f'{url} → {code} ({body.strip()[:40] or loc})')
            else:
                _fail(f'{url} → {code}')
                rc = 1
        except Exception as exc:
            _fail(f'{url}: {exc}')
            rc = 1
    return rc


def check_mp() -> int:
    print('\n=== Mercado Pago ===')
    try:
        from mercadopago_client import get_mp_access_token, get_mp_sdk, mp_environment, mp_status

        env = mp_environment()
        token = get_mp_access_token()
        _ok(f'ambiente={env}, token={token[:12]}…')
        st = mp_status()
        if st.get('pronto_checkout'):
            _ok('checkout banda pronto')
        else:
            _warn(f'checkout banda: {st}')
        if st.get('pronto_checkout_estudio'):
            _ok('checkout estúdio pronto')
        else:
            _warn('checkout estúdio não pronto (confira planos/token)')
        sdk = get_mp_sdk()
        # ping leve: listar user id via /users/me se disponível
        try:
            res = sdk.user().get()
            if res.get('status') in (200, 201):
                _ok(f'API MP user ok (id={ (res.get("response") or {}).get("id") })')
            else:
                _warn(f'API MP user: {res.get("status")}')
        except Exception as exc:
            _warn(f'ping user MP: {exc}')
        return 0
    except Exception as exc:
        _fail(str(exc))
        return 1


def _dns_txt(name: str) -> list[str]:
    try:
        import dns.resolver  # type: ignore

        return [r.to_text().strip('"') for r in dns.resolver.resolve(name, 'TXT')]
    except Exception:
        # fallback dig via getaddrinfo-ish: use socket + no TXT
        return []


def check_mail_dns() -> int:
    print('\n=== DNS e-mail unissono.app ===')
    rc = 0
    try:
        answers = socket.getaddrinfo('mail.unissono.app', 25, type=socket.SOCK_STREAM)
        ips = sorted({a[4][0] for a in answers if a[4]})
        if ips:
            _ok(f'mail.unissono.app → {", ".join(ips)}')
        else:
            _fail('mail.unissono.app sem A/AAAA')
            rc = 1
    except Exception as exc:
        _fail(f'mail.unissono.app: {exc}')
        rc = 1

    # MX via dig subprocess if dnspython ausente
    import subprocess

    mx = subprocess.getoutput('dig +short MX unissono.app').strip()
    if mx:
        _ok(f'MX unissono.app → {mx}')
    else:
        _warn('MX unissono.app ausente — configure mail.unissono.app no DNS')
        rc = 1

    spf = subprocess.getoutput('dig +short TXT unissono.app').strip()
    if 'v=spf1' in spf:
        _ok(f'SPF ok ({spf[:80]})')
    else:
        _warn('SPF TXT ausente ou incompleto')

    dkim = subprocess.getoutput('dig +short TXT unissono._domainkey.unissono.app').strip()
    if dkim:
        _ok(f'DKIM presente ({len(dkim)} chars)')
    else:
        _warn('DKIM unissono._domainkey ausente')
        rc = 1

    domain = (os.getenv('MAIL_DOMAIN') or '').strip()
    admin = (os.getenv('ADMIN_EMAIL') or '').strip()
    if domain == 'unissono.app':
        _ok(f'MAIL_DOMAIN={domain}')
    else:
        _warn(f'MAIL_DOMAIN={domain or "vazio"}')
    if admin.endswith('@unissono.app'):
        _ok(f'ADMIN_EMAIL={admin}')
    else:
        _warn(f'ADMIN_EMAIL={admin or "vazio"}')
    return rc


def main() -> int:
    rc = 0
    rc |= check_canonical()
    rc |= check_http()
    rc |= check_mp()
    rc |= check_mail_dns()
    print('\n=== Fim ===')
    print('OK' if rc == 0 else 'Falhas/avisos acima — corrija DNS/MP se marcado ✗')
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
