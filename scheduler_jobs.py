"""Jobs agendados (vouchers, onboarding, trial)."""

from __future__ import annotations

from datetime import datetime, timedelta

from db import (
    list_voucher_usos_aviso,
    list_voucher_usos_vencendo,
    list_studio_voucher_usos_aviso,
    list_studio_voucher_usos_vencendo,
    marcar_aviso_studio_voucher_enviado,
    marcar_aviso_voucher_enviado,
    update_assinatura,
    list_trials_expiring_soon,
    list_studio_trials_expiring_soon,
)
from monetizacao import PLANOS, PLANOS_ESTUDIO, PLANO_ESTUDIO_PREMIUM
from models_studio import PLANO_ESTUDIO_BASICO, update_studio_subscription
from email_service import send_email
from monetizacao_emails import send_voucher_aviso_email, send_voucher_expirado_email
from onboarding_emails import verificar_e_disparar_onboarding
from retention_emails import verificar_e_disparar_retencao
from agenda_reminders import verificar_e_enviar_lembretes_agenda
from security import external_url_for
from vouchers import STATUS_EXPIRADO
from config import app_now_naive, app_now_str


def verificar_vouchers_vencidos() -> None:
    """Rebaixa bandas com voucher expirado e envia e-mail."""
    agora = app_now_str()  # was strftime('%Y-%m-%d %H:%M:%S')
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


def verificar_studio_vouchers_vencidos() -> None:
    """Rebaixa contas de estúdio com voucher expirado e envia e-mail."""
    agora = app_now_str()
    for row in list_studio_voucher_usos_vencendo(agora):
        user_id = row['user_id']
        update_studio_subscription(
            user_id,
            plano=PLANO_ESTUDIO_BASICO,
            status=STATUS_EXPIRADO,
        )
        plano = row.get('plano', PLANO_ESTUDIO_PREMIUM)
        plano_nome = PLANOS_ESTUDIO.get(plano).nome if plano in PLANOS_ESTUDIO else plano
        email = row.get('owner_email')
        if email:
            send_voucher_expirado_email(email, plano_nome)


def avisar_studio_vouchers_proximo_vencimento() -> None:
    """E-mail 3 dias antes do vencimento do voucher de estúdio."""
    limite = (app_now_naive() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    for row in list_studio_voucher_usos_aviso(limite):
        plano = row.get('plano', PLANO_ESTUDIO_PREMIUM)
        plano_nome = PLANOS_ESTUDIO.get(plano).nome if plano in PLANOS_ESTUDIO else plano
        expira = datetime.strptime(str(row['expira_em'])[:19], '%Y-%m-%d %H:%M:%S')
        dias = max(1, (expira - app_now_naive()).days)
        email = row.get('owner_email')
        if email and send_voucher_aviso_email(email, plano_nome, dias):
            marcar_aviso_studio_voucher_enviado(row['id'])


def avisar_vouchers_proximo_vencimento() -> None:
    """E-mail 3 dias antes do vencimento."""
    limite = (app_now_naive() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    for row in list_voucher_usos_aviso(limite):
        plano = row.get('plano', 'pro')
        plano_nome = PLANOS.get(plano).nome if plano in PLANOS else plano
        expira = datetime.strptime(str(row['expira_em'])[:19], '%Y-%m-%d %H:%M:%S')
        dias = max(1, (expira - app_now_naive()).days)
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


def avisar_studio_trials_proximo_vencimento() -> None:
    """E-mail quando faltam ~3 dias para o trial Premium de estúdio acabar."""
    link = external_url_for('assinatura_bp.planos') + '#estudio'
    for row in list_studio_trials_expiring_soon(days=3):
        email = row.get('owner_email')
        if not email:
            continue
        fim = str(row.get('trial_fim', ''))[:10]
        subject = 'Seu trial Premium de estúdio termina em 3 dias'
        body = (
            f'Seu trial Premium de estúdio termina em breve ({fim}).\n'
            f'Assine para manter salas ilimitadas: {link}'
        )
        html = (
            f'<p>Seu <strong>trial Premium de estúdio</strong> termina em <strong>3 dias</strong>.</p>'
            f'<p><a href="{link}">Ver planos Estúdio</a></p>'
        )
        send_email([email], subject, html, body)


def run_daily_voucher_jobs() -> None:
    avisar_vouchers_proximo_vencimento()
    avisar_studio_vouchers_proximo_vencimento()
    verificar_vouchers_vencidos()
    verificar_studio_vouchers_vencidos()
    avisar_trials_proximo_vencimento()
    avisar_studio_trials_proximo_vencimento()
    verificar_e_disparar_onboarding()
    verificar_e_disparar_retencao()
    from studio_onboarding_emails import verificar_e_disparar_onboarding_estudio
    verificar_e_disparar_onboarding_estudio()


def run_agenda_reminder_jobs() -> None:
    verificar_e_enviar_lembretes_agenda()


def run_whatsapp_cifra_digest_jobs() -> None:
    """Legado: resumos antigos só de cifra (WhatsApp)."""
    from whatsapp_cifra_digest import send_pending_cifra_digests

    send_pending_cifra_digests()


def run_notification_digest_jobs() -> None:
    """Resumo diário de notificações não urgentes (push, e-mail e WhatsApp)."""
    from notification_digest import send_pending_notification_digests

    send_pending_notification_digests()
    run_whatsapp_cifra_digest_jobs()