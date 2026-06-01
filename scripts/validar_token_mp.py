#!/usr/bin/env python3
"""Valida Access Token do Mercado Pago antes de criar planos."""

from __future__ import annotations

import os
import sys

import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, '.env'), override=True)

from mercadopago_client import get_mp_access_token, mp_environment  # noqa: E402


def main() -> int:
    env = mp_environment()
    print(f'Ambiente (.env): {env}')
    try:
        token = get_mp_access_token()
    except RuntimeError as e:
        print(f'✗ {e}')
        return 1

    prefixo = token[:12] + '…'
    print(f'Token carregado: {prefixo} (tamanho {len(token)} caracteres)')

    if token.count('-') < 4:
        print('⚠  Access Token do MP costuma ter vários hífens. Você colou a Public Key por engano?')

    # Teste direto na API (mesmo que o SDK usa)
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get('https://api.mercadopago.com/users/me', headers=headers, timeout=30)
    print(f'GET /users/me → HTTP {r.status_code}')

    if r.status_code == 200:
        data = r.json()
        print(f'✓ Token válido — conta MP id {data.get("id", "?")}')
        r2 = requests.get(
            'https://api.mercadopago.com/preapproval_plan/search',
            headers=headers,
            params={'status': 'active'},
            timeout=30,
        )
        print(f'GET /preapproval_plan/search → HTTP {r2.status_code}')
        if r2.status_code == 200:
            plans = (r2.json() or {}).get('results') or []
            print(f'  Planos de assinatura já existentes: {len(plans)}')
            for p in plans[:5]:
                print(f'    · {p.get("id")} — {p.get("reason")} — R$ {p.get("auto_recurring", {}).get("transaction_amount")}')
        print('\nPode rodar: uv run python scripts/criar_planos_mp.py')
        return 0

    if r.status_code == 401:
        print('✗ Token inválido ou expirado (401 unauthorized)')
        print()
        print('Corrija assim:')
        print('  1. https://www.mercadopago.com.br/developers/panel/app')
        print('  2. Sua aplicação → Credenciais de', 'PRODUÇÃO' if env == 'production' else 'TESTE')
        print('  3. Copie o campo "Access Token" (NÃO "Public Key" — os dois começam com APP_USR-)')
        print('  4. Se produção: ative as credenciais de produção no painel')
        print('  5. Cole no .env em', 'MP_ACCESS_TOKEN' if env == 'production' else 'MP_ACCESS_TOKEN_TEST')
        print('  6. Rode de novo este script')
        return 1

    print('✗ Resposta inesperada:', r.text[:300])
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
