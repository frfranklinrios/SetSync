"""Textos e flags de confiança para pagamentos via Mercado Pago."""

from __future__ import annotations

import os


def mercadopago_trust_enabled() -> bool:
    """Exibir selo/copy de pagamento MP (MERCADOPAGO_TRUST_ENABLED=0 desliga)."""
    return os.getenv('MERCADOPAGO_TRUST_ENABLED', '1').strip().lower() not in (
        '0',
        'false',
        'no',
        'off',
    )


def show_mercadopago_trust() -> bool:
    """Mostra mensagem só quando MP está configurado (token presente)."""
    if not mercadopago_trust_enabled():
        return False
    try:
        from mercadopago_client import mp_config_status

        return bool(mp_config_status().get('token_ok'))
    except Exception:
        return False


def mercadopago_trust_email_html() -> str:
    return (
        '<p style="font-size:14px;color:#64748b;margin-top:16px;">'
        '<strong>Pagamento seguro:</strong> ao assinar, você é redirecionado ao '
        '<strong>Mercado Pago</strong>. Seus dados de cartão não passam pelo SetSync.'
        '</p>'
    )
