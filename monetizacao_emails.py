"""E-mails relacionados a assinaturas e vouchers."""

from __future__ import annotations

from email_service import send_email
from security import external_url_for


def send_voucher_expirado_email(email: str, plano_nome: str) -> None:
    link = external_url_for('assinatura_bp.planos')
    subject = 'Seu período gratuito no SetSync acabou'
    body = (
        f'Seu acesso ao plano {plano_nome} no SetSync terminou.\n\n'
        f'Assine agora para continuar sem limites: {link}'
    )
    html = (
        f'<p>Seu acesso ao plano <strong>{plano_nome}</strong> no SetSync terminou.</p>'
        f'<p><a href="{link}" style="display:inline-block;padding:12px 24px;'
        f'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;">'
        f'Assinar agora</a></p>'
    )
    send_email([email], subject, html, body)


def send_voucher_aviso_email(email: str, plano_nome: str, dias_restantes: int) -> None:
    link = external_url_for('assinatura_bp.planos')
    subject = f'Seu acesso {plano_nome} vence em {dias_restantes} dias'
    body = (
        f'Seu acesso Pro no SetSync vence em {dias_restantes} dias. '
        f'Assine para não perder nada: {link}'
    )
    html = (
        f'<p>Seu acesso <strong>{plano_nome}</strong> vence em '
        f'<strong>{dias_restantes} dias</strong>.</p>'
        f'<p><a href="{link}">Assinar agora</a></p>'
    )
    send_email([email], subject, html, body)


def send_indicacao_recompensa_email(email: str, dias: int) -> None:
    subject = 'Alguém usou seu link! Você ganhou dias grátis.'
    body = f'Alguém usou seu voucher de indicação! Você ganhou {dias} dias grátis no SetSync.'
    html = f'<p>Alguém usou seu link de indicação!</p><p>Você ganhou <strong>{dias} dias grátis</strong>.</p>'
    send_email([email], subject, html, body)
