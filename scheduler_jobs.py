"""Jobs agendados (vencimento de vouchers)."""

from __future__ import annotations

from datetime import datetime, timedelta

from db import (
    list_voucher_usos_aviso,
    list_voucher_usos_vencendo,
    marcar_aviso_voucher_enviado,
    update_assinatura,
)
from monetizacao import PLANOS
from monetizacao_emails import send_voucher_aviso_email, send_voucher_expirado_email
from vouchers import STATUS_EXPIRADO


def verificar_vouchers_vencidos() -> None:
    """Rebaixa bandas com voucher expirado e envia e-mail."""
    agora = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    for row in list_voucher_usos_vencendo(agora):
        banda_id = row['banda_id']
        update_assinatura(
            banda_id,
            plano='gratis',
            status=STATUS_EXPIRADO,
            data_cancelamento=agora,
        )
        plano = row.get('plano', 'pro')
        plano_nome = PLANOS.get(plano).nome if plano in PLANOS else plano
        email = row.get('owner_email')
        if email:
            send_voucher_expirado_email(email, plano_nome)


def avisar_vouchers_proximo_vencimento() -> None:
    """E-mail 3 dias antes do vencimento."""
    limite = (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    for row in list_voucher_usos_aviso(limite):
        plano = row.get('plano', 'pro')
        plano_nome = PLANOS.get(plano).nome if plano in PLANOS else plano
        expira = datetime.strptime(str(row['expira_em'])[:19], '%Y-%m-%d %H:%M:%S')
        dias = max(1, (expira - datetime.utcnow()).days)
        email = row.get('owner_email')
        if email:
            send_voucher_aviso_email(email, plano_nome, dias)
        marcar_aviso_voucher_enviado(row['id'])


def run_daily_voucher_jobs() -> None:
    avisar_vouchers_proximo_vencimento()
    verificar_vouchers_vencidos()
