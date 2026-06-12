"""Recuperação de senha — e-mail e WhatsApp."""

from __future__ import annotations

from email_service import is_configured, send_email
from security import external_url_for


def password_reset_link(token: str) -> str:
    return external_url_for('auth.reset_senha', token=token)


def send_password_reset_email(email: str, token: str) -> bool:
    """Envia link de redefinição de senha. Retorna True se o SMTP entregou."""
    if not is_configured():
        return False

    link = password_reset_link(token)
    subject = 'Redefinir sua senha — SetSync'
    body = (
        'Recebemos um pedido para redefinir sua senha no SetSync.\n\n'
        f'Abra o link abaixo (válido por 1 hora):\n{link}\n\n'
        'Se você não solicitou, ignore este e-mail — sua senha não será alterada.'
    )
    html = (
        '<div style="font-family:system-ui,sans-serif;color:#1c1917;max-width:520px">'
        '<p style="color:#78716c;font-size:13px;margin:0 0 8px">SetSync</p>'
        '<h2 style="margin:0 0 12px;font-size:1.25rem">Redefinir sua senha</h2>'
        '<p>Recebemos um pedido para criar uma nova senha na sua conta.</p>'
        '<p>O link abaixo expira em <strong>1 hora</strong>.</p>'
        f'<p style="margin:24px 0 0">'
        f'<a href="{link}" style="display:inline-block;padding:12px 24px;'
        f'background:#ea580c;color:#fff;text-decoration:none;border-radius:8px;'
        f'font-weight:600">Redefinir minha senha</a></p>'
        f'<p style="margin:20px 0 0;font-size:12px;color:#78716c;word-break:break-all">'
        f'Ou copie e cole no navegador:<br>{link}</p>'
        '<p style="margin:28px 0 0;font-size:12px;color:#a8a29e">'
        'Se você não solicitou, ignore este e-mail.</p>'
        '</div>'
    )
    return send_email([email], subject, html, body)


def send_password_reset_whatsapp(user: dict, token: str) -> bool:
    """Envia o link de recuperação ao WhatsApp cadastrado (mensagem transacional)."""
    from whatsapp_service import is_configured, normalize_whatsapp_phone, send_whatsapp_text

    if not is_configured():
        return False
    phone = normalize_whatsapp_phone(user.get('phone'))
    if not phone:
        return False

    link = password_reset_link(token)
    text = (
        '*SetSync*\n'
        '*Redefinir sua senha*\n\n'
        'Recebemos um pedido para criar uma nova senha na sua conta.\n'
        'O link abaixo expira em *1 hora*.\n\n'
        f'{link}\n\n'
        'Se você não solicitou, ignore esta mensagem.'
    )
    return send_whatsapp_text(phone, text)
