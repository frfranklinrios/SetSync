#!/usr/bin/env python3
"""
Verifica credenciais MP em sandbox e opcionalmente testa checkout + webhook local.

Uso:
  cd /caminho/setsync
  cp .env.example .env   # preencha MP_* 
  python3 scripts/test_mp_sandbox.py check
  python3 scripts/test_mp_sandbox.py preapproval --email test_user@testuser.com
  python3 scripts/test_mp_sandbox.py webhook --preapproval-id ID --secret SEU_SECRET
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

load_dotenv(override=True)


def _ok(msg: str) -> None:
    print(f'  ✓ {msg}')


def _fail(msg: str) -> None:
    print(f'  ✗ {msg}')


def cmd_check() -> int:
    """Valida variáveis de ambiente e conexão com a API."""
    from mercadopago_client import get_mp_access_token, get_mp_sdk, mp_environment, plan_id_for

    print('=== Verificação Mercado Pago (sandbox) ===\n')
    env = mp_environment()
    print(f'Ambiente: {env}')

    try:
        token = get_mp_access_token()
        _ok(f'Token carregado ({token[:12]}…)')
    except RuntimeError as e:
        _fail(str(e))
        return 1

    for plano, var in [('pro', 'MP_PLAN_PRO_ID'), ('worship', 'MP_PLAN_WORSHIP_ID')]:
        pid = os.getenv(var, '').strip()
        if pid:
            _ok(f'{var}={pid[:20]}…')
        else:
            _fail(f'{var} ausente — rode scripts/criar_planos_mp.py')

    secret = os.getenv('MP_WEBHOOK_SECRET', '').strip()
    if secret:
        _ok('MP_WEBHOOK_SECRET definido')
    else:
        _fail('MP_WEBHOOK_SECRET ausente (recomendado para produção)')

    try:
        sdk = get_mp_sdk()
        pro_id = plan_id_for('pro')
        res = sdk.plan().get(pro_id)
        if res.get('status') in (200, 201):
            reason = (res.get('response') or {}).get('reason', '?')
            _ok(f'Plano Pro acessível: {reason}')
        else:
            _fail(f'Plano Pro: HTTP {res.get("status")} — {res}')
            return 1
    except Exception as e:
        _fail(f'API MP: {e}')
        return 1

    print('\nPróximo passo: suba o app e use ngrok para testar webhook.')
    print('  python3 main.py')
    print('  ngrok http 5000')
    print('  URL webhook: https://SEU_SUBDOMINIO.ngrok-free.app/assinatura/webhook?secret=SEU_SECRET')
    return 0


def cmd_preapproval(email: str, plano: str) -> int:
    """Cria uma preapproval de teste e imprime init_point."""
    from mercadopago_client import build_preapproval_checkout_body, checkout_init_point, get_mp_sdk

    sdk = get_mp_sdk()
    body = build_preapproval_checkout_body(
        plano,
        payer_email=email,
        external_reference=f'teste-banda:{plano}',
        back_url=os.getenv('MP_TEST_BACK_URL', 'http://127.0.0.1:5000/assinatura/sucesso'),
        reason=f'SetSync teste {plano}',
    )
    result = sdk.preapproval().create(body)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get('status') not in (200, 201):
        return 1
    resp = result.get('response') or {}
    init = checkout_init_point(result)
    print('\n--- Abra no navegador (sandbox) ---')
    print(init or resp.get('init_point'))
    print('\npreapproval_id:', resp.get('id'))
    return 0


def cmd_webhook(preapproval_id: str, base_url: str, secret: str) -> int:
    """Simula notificação MP no servidor local."""
    url = f'{base_url.rstrip("/")}/assinatura/webhook'
    qs = f'?topic=subscription_preapproval&id={preapproval_id}&secret={secret}'
    full = url + qs
    req = urllib.request.Request(full, method='POST', data=b'{}')
    req.add_header('Content-Type', 'application/json')
    print('POST', full)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print('Status:', resp.status)
            print(resp.read().decode() or '(vazio)')
    except urllib.error.HTTPError as e:
        print('Status:', e.code)
        print(e.read().decode())
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Testes Mercado Pago sandbox — SetSync')
    sub = parser.add_subparsers(dest='cmd', required=True)

    sub.add_parser('check', help='Validar .env e API')

    p_pre = sub.add_parser('preapproval', help='Criar assinatura de teste')
    p_pre.add_argument('--email', default='test_user@testuser.com', help='E-mail pagador teste MP')
    p_pre.add_argument('--plano', choices=('pro', 'worship'), default='pro')

    p_wh = sub.add_parser('webhook', help='Simular webhook local')
    p_wh.add_argument('--preapproval-id', required=True)
    p_wh.add_argument('--base-url', default=os.getenv('MP_TEST_BASE_URL', 'http://127.0.0.1:5000'))
    p_wh.add_argument('--secret', default=os.getenv('MP_WEBHOOK_SECRET', ''))

    args = parser.parse_args()
    if args.cmd == 'check':
        return cmd_check()
    if args.cmd == 'preapproval':
        return cmd_preapproval(args.email, args.plano)
    if args.cmd == 'webhook':
        if not args.secret:
            print('Defina --secret ou MP_WEBHOOK_SECRET no .env', file=sys.stderr)
            return 1
        return cmd_webhook(args.preapproval_id, args.base_url, args.secret)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
