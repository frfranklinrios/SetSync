"""Cliente Mercado Pago (SDK) com seleção sandbox/produção."""

from __future__ import annotations

import os

import mercadopago


def mp_environment() -> str:
    return (os.getenv('MP_ENVIRONMENT') or 'sandbox').strip().lower()


def get_mp_access_token() -> str:
    """Token conforme MP_ENVIRONMENT."""
    if mp_environment() == 'production':
        token = (os.getenv('MP_ACCESS_TOKEN') or '').strip()
    else:
        token = (os.getenv('MP_ACCESS_TOKEN_TEST') or os.getenv('MP_ACCESS_TOKEN') or '').strip()
    if not token:
        raise RuntimeError('Token Mercado Pago não configurado (MP_ACCESS_TOKEN / MP_ACCESS_TOKEN_TEST)')
    return token


def get_mp_sdk() -> mercadopago.SDK:
    return mercadopago.SDK(get_mp_access_token())


def plan_id_for(plano: str) -> str:
    """ID do plano de recorrência no MP."""
    key = 'MP_PLAN_PRO_ID' if plano == 'pro' else 'MP_PLAN_WORSHIP_ID'
    plan_id = (os.getenv(key) or '').strip()
    if not plan_id:
        raise RuntimeError(f'Variável {key} não configurada')
    return plan_id


def _valor_preenchido(valor: str | None) -> bool:
    v = (valor or '').strip()
    if not v:
        return False
    marcadores_vazio = ('COLE_', 'SEU_', 'XXXX', 'AQUI', 'opcional')
    return not any(m in v.upper() for m in marcadores_vazio)


def mp_config_status() -> dict:
    """
    Estado da configuração MP para a UI e scripts de teste.
    """
    env = mp_environment()
    token_var = 'MP_ACCESS_TOKEN' if env == 'production' else 'MP_ACCESS_TOKEN_TEST'
    token = (os.getenv(token_var) or os.getenv('MP_ACCESS_TOKEN') or '').strip()
    pro_id = (os.getenv('MP_PLAN_PRO_ID') or '').strip()
    worship_id = (os.getenv('MP_PLAN_WORSHIP_ID') or '').strip()
    webhook = (os.getenv('MP_WEBHOOK_SECRET') or '').strip()

    token_ok = _valor_preenchido(token)
    planos_ok = _valor_preenchido(pro_id) and _valor_preenchido(worship_id)
    pronto = token_ok and planos_ok

    faltando = []
    if not token_ok:
        faltando.append(f'Preencha {token_var} no .env (Access Token de teste ou produção)')
    if not _valor_preenchido(pro_id) or not _valor_preenchido(worship_id):
        faltando.append('Rode: uv run python scripts/criar_planos_mp.py e copie MP_PLAN_PRO_ID / MP_PLAN_WORSHIP_ID')

    return {
        'environment': env,
        'token_var': token_var,
        'token_ok': token_ok,
        'planos_ok': planos_ok,
        'webhook_ok': _valor_preenchido(webhook),
        'pronto_checkout': pronto,
        'faltando': faltando,
    }


def checkout_init_point(response: dict) -> str:
    """URL de checkout (sandbox ou produção)."""
    body = response.get('response') or response
    if mp_environment() == 'sandbox':
        return body.get('sandbox_init_point') or body.get('init_point', '')
    return body.get('init_point') or body.get('sandbox_init_point', '')
