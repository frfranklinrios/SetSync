import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid

from mail_server.config import DOMAIN, SENDER_NAME, SMTP_CONNECT_HOST, SMTP_SUBMISSION_PORT
from mail_server.server.outbound import deliver_external, get_last_error

logger = logging.getLogger(__name__)

last_send_error: str = ""


def get_last_send_error() -> str:
    return last_send_error or get_last_error()


def send_email(
    sender: str,
    recipients: list[str],
    subject: str,
    body: str,
    password: str,
    html_body: str | None = None,
    sender_name: str | None = None,
) -> bool:
    global last_send_error
    last_send_error = ""

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((sender_name or SENDER_NAME, sender))
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=DOMAIN)
    msg["MIME-Version"] = "1.0"

    msg.attach(MIMEText(body, "plain", "utf-8"))
    if html_body:
        msg.attach(MIMEText(html_body, "html", "utf-8"))

    msg_str = msg.as_string()
    local = [r for r in recipients if r.lower().endswith(f"@{DOMAIN}")]
    external = [r for r in recipients if not r.lower().endswith(f"@{DOMAIN}")]

    if external:
        if not deliver_external(sender, external, msg_str):
            last_send_error = get_last_error()
            return False

    if local:
        try:
            with smtplib.SMTP(SMTP_CONNECT_HOST, SMTP_SUBMISSION_PORT) as server:
                server.ehlo()
                server.login(sender, password)
                server.sendmail(sender, local, msg_str)
        except smtplib.SMTPException as exc:
            last_send_error = f"Erro ao entregar localmente: {exc}"
            logger.error(last_send_error)
            return False

    if not local and not external:
        last_send_error = "Nenhum destinatário informado"
        return False

    logger.info("Email enviado: %s -> %s", sender, recipients)
    return True
