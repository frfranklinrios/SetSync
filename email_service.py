"""Serviço central de envio de e-mails do SetSync.

Camada única sobre o Flask-Mail. Todo módulo que envia e-mail
(autenticação, onboarding, assinaturas/vouchers) deve usar ``send_email``
daqui — assim o tratamento de configuração ausente e de erros fica
consistente em um só lugar.
"""

from __future__ import annotations

from typing import Sequence

from flask import current_app
from flask_mail import Message


def is_configured() -> bool:
    """True se o Flask-Mail está inicializado e tem credenciais SMTP.

    A extensão ``mail`` é sempre registrada em ``app.py``; o sinal de
    "pronto para enviar" é haver ``MAIL_USERNAME`` e ``MAIL_PASSWORD``.
    """
    if not current_app.extensions.get('mail'):
        return False
    return bool(
        current_app.config.get('MAIL_USERNAME')
        and current_app.config.get('MAIL_PASSWORD')
    )


def send_email(
    recipients: Sequence[str] | str,
    subject: str,
    html: str | None = None,
    body: str | None = None,
) -> bool:
    """Envia um e-mail. Retorna True se enviado, False se ignorado ou falhou.

    Degrada graciosamente: sem SMTP configurado, registra um aviso e retorna
    False em vez de levantar exceção. Falhas de envio são logadas e também
    retornam False — nunca propagam para o chamador.
    """
    if isinstance(recipients, str):
        recipients = [recipients]
    recipients = [r for r in (recipients or []) if r]
    if not recipients:
        return False

    if not is_configured():
        current_app.logger.warning(
            'Flask-Mail não configurado; e-mail não enviado: %s', subject
        )
        return False

    msg = Message(subject=subject, recipients=list(recipients), body=body, html=html)
    try:
        current_app.extensions['mail'].send(msg)
        return True
    except Exception:
        current_app.logger.exception('Falha ao enviar e-mail: %s', subject)
        return False
