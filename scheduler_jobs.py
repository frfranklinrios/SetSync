"""Jobs agendados (vouchers, onboarding, trial)."""

from __future__ import annotations

from datetime import datetime, timedelta

from db import (
    list_voucher_usos_aviso,
    list_voucher_usos_vencendo,
    marcar_aviso_voucher_enviado,
    update_assinatura,
    list_trials_expiring_soon,
)
from monetizacao import PLANOS
from email_service import send_email
from monetizacao_emails import send_voucher_aviso_email, send_voucher_expirado_email
from onboarding_emails import verificar_e_disparar_onboarding
from retention_emails import verificar_e_disparar_retencao
from agenda_reminders import verificar_e_enviar_lembretes_agenda
from security import external_url_for
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
        if email and send_voucher_aviso_email(email, plano_nome, dias):
            marcar_aviso_voucher_enviado(row['id'])


def avisar_trials_proximo_vencimento() -> None:
    """E-mail quando faltam ~3 dias para o trial Pro acabar."""
    link = external_url_for('assinatura_bp.planos')
    for row in list_trials_expiring_soon(days=3):
        email = row.get('owner_email')
        if not email:
            continue
        fim = str(row.get('trial_fim', ''))[:10]
        subject = 'Seu trial Pro termina em 3 dias'
        body = (
            f'Seu trial Pro na banda {row.get("band_name", "")} termina em breve ({fim}).\n'
            f'Assine para manter recursos ilimitados: {link}'
        )
        html = (
            f'<p>Seu <strong>trial Pro</strong> termina em <strong>3 dias</strong>.</p>'
            f'<p><a href="{link}">Fazer upgrade — R$ 29/mês</a></p>'
        )
        send_email([email], subject, html, body)


def run_daily_voucher_jobs() -> None:
    avisar_vouchers_proximo_vencimento()
    verificar_vouchers_vencidos()
    avisar_trials_proximo_vencimento()
    verificar_e_disparar_onboarding()
    verificar_e_disparar_retencao()


def run_agenda_reminder_jobs() -> None:
    verificar_e_enviar_lembretes_agenda()


def run_whatsapp_cifra_digest_jobs() -> None:
    """Um WhatsApp por usuário com resumo das cifras editadas no dia."""
    from whatsapp_cifra_digest import send_pending_cifra_digests

    send_pending_cifra_digests()
