import email
import logging
from email import policy
from email.utils import parseaddr

from aiosmtpd.smtp import AuthResult, SMTP

from mail_server.config import DOMAIN
from mail_server.server.outbound import deliver_external, get_last_error
from mail_server.server.storage import EmailStorage

logger = logging.getLogger(__name__)


def _extract_recipients(message, rcpt_tos: list[str]) -> list[str]:
    seen: set[str] = set()
    recipients: list[str] = []

    for addr in rcpt_tos:
        email_addr = addr.lower().strip()
        if email_addr and email_addr not in seen:
            seen.add(email_addr)
            recipients.append(email_addr)

    for header in ("To", "Cc", "Bcc"):
        for raw in message.get_all(header, []):
            addr = parseaddr(raw)[1].lower().strip()
            if addr and addr not in seen:
                seen.add(addr)
                recipients.append(addr)

    return recipients


class EmailHandler:
    def __init__(self, storage: EmailStorage):
        self.storage = storage

    async def handle_DATA(self, server: SMTP, session, envelope):
        raw = envelope.content
        parsed = email.message_from_bytes(raw, policy=policy.default)

        sender = envelope.mail_from or parseaddr(parsed.get("From", ""))[1] or "unknown@unknown"
        recipients = _extract_recipients(parsed, envelope.rcpt_tos)
        subject = parsed.get("Subject", "(sem assunto)")

        body_text = ""
        body_html = None

        if parsed.is_multipart():
            for part in parsed.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" and not body_text:
                    body_text = part.get_content()
                elif content_type == "text/html" and not body_html:
                    body_html = part.get_content()
        else:
            content_type = parsed.get_content_type()
            content = parsed.get_content()
            if content_type == "text/html":
                body_html = content
            else:
                body_text = content

        message_id = parsed.get("Message-ID", "")

        local_rcpts = [r for r in recipients if r.endswith(f"@{DOMAIN}")]
        external_rcpts = [r for r in recipients if not r.endswith(f"@{DOMAIN}")]
        authenticated = bool(
            getattr(session, 'login_data', None) or getattr(session, 'authenticated', False)
        )

        if external_rcpts:
            if not authenticated:
                logger.warning(
                    "Destinatário externo sem autenticação ignorado: %s",
                    external_rcpts,
                )
            else:
                raw_text = raw.decode('utf-8', errors='replace') if isinstance(raw, bytes) else str(raw)
                if not deliver_external(sender, external_rcpts, raw_text):
                    err = get_last_error() or 'falha na entrega externa'
                    logger.error('Relay externo falhou %s -> %s: %s', sender, external_rcpts, err)
                    return f'550 {err}'
                logger.info(
                    'Email enviado (relay externo): %s -> %s | %s',
                    sender, external_rcpts, subject,
                )

        for recipient in local_rcpts:
            user = await self.storage.get_user_by_email(recipient)
            if not user:
                logger.warning("Caixa inexistente: %s", recipient)
                continue

            await self.storage.save_email(
                sender=sender,
                recipients=recipients,
                subject=subject,
                body_text=body_text or "",
                body_html=body_html,
                owner_email=recipient,
                message_id=message_id,
            )
            logger.info("Email recebido: %s -> %s | %s", sender, recipient, subject)

        if not local_rcpts and not (external_rcpts and authenticated):
            return "550 Nenhum destinatário aceito"

        return "250 Message accepted for delivery"


class SMTPAuthenticator:
    def __init__(self, storage: EmailStorage):
        self.storage = storage

    def __call__(self, server, session, envelope, mechanism, login_data):
        if mechanism not in ("LOGIN", "PLAIN"):
            return AuthResult(success=False, handled=False)

        username, password = login_data
        if isinstance(username, bytes):
            username = username.decode("utf-8", errors="replace")
        if isinstance(password, bytes):
            password = password.decode("utf-8", errors="replace")

        user = self.storage.authenticate_sync(username, password)
        if user:
            return AuthResult(success=True, auth_data=login_data)

        return AuthResult(success=False, message="535 5.7.8 Credenciais inválidas")
