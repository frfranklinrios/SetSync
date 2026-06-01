#!/usr/bin/env python3
"""
Cria planos de recorrência Pro e Worship no Mercado Pago.

Uso:
  uv run python scripts/validar_token_mp.py   # primeiro
  uv run python scripts/criar_planos_mp.py

Imprime os IDs para MP_PLAN_PRO_ID e MP_PLAN_WORSHIP_ID no .env
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, '.env'), override=True)

import requests  # noqa: E402

from mercadopago_client import get_mp_access_token, mp_environment  # noqa: E402


def validar_token(token: str) -> None:
    """Falha com mensagem clara se o token não autentica."""
    r = requests.get(
        'https://api.mercadopago.com/users/me',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30,
    )
    if r.status_code == 200:
        return
    if r.status_code == 401:
        env = mp_environment()
        var = 'MP_ACCESS_TOKEN' if env == 'production' else 'MP_ACCESS_TOKEN_TEST'
        raise SystemExit(
            '\n✗ Access Token inválido (401).\n\n'
            'No painel MP copie "Access Token", não "Public Key".\n'
            f'Atualize {var} no .env e rode:\n'
            '  uv run python scripts/validar_token_mp.py\n'
        )
    raise SystemExit(f'\n✗ Erro ao validar token: HTTP {r.status_code}\n{r.text[:400]}\n')


def criar_plano(token: str, reason: str, amount: float) -> str:
    """Cria preapproval_plan via API REST."""
    body = {
        'reason': reason,
        'auto_recurring': {
            'frequency': 1,
            'frequency_type': 'months',
            'transaction_amount': amount,
            'currency_id': 'BRL',
        },
        'back_url': os.getenv('MP_BACK_URL', 'https://setsync.dados.tec.br/assinatura/planos'),
    }
    r = requests.post(
        'https://api.mercadopago.com/preapproval_plan',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        json=body,
        timeout=30,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f'Erro ao criar plano: {json.dumps(r.json(), indent=2, ensure_ascii=False)}')
    return r.json()['id']


def main() -> None:
    token = get_mp_access_token()
    print(f'Ambiente: {mp_environment()}')
    print('Validando Access Token…')
    validar_token(token)

    print('Criando plano Pro (R$ 29/mês)…')
    pro_id = criar_plano(token, 'SetSync Pro', 29.0)
    print('Criando plano Worship (R$ 69/mês)…')
    worship_id = criar_plano(token, 'SetSync Worship', 69.0)

    print()
    print('Cole no .env:')
    print(f'MP_PLAN_PRO_ID={pro_id}')
    print(f'MP_PLAN_WORSHIP_ID={worship_id}')


if __name__ == '__main__':
    main()
