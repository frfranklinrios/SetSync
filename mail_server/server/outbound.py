import logging
import smtplib

import dns.resolver

from mail_server.config import DOMAIN, MAIL_HOSTNAME
from mail_server.server.dkim_sign import sign_message

logger = logging.getLogger(__name__)

last_error: str = ""


def get_last_error() -> str:
    return last_error


def _set_error(msg: str) -> bool:
    global last_error
    last_error = msg
    logger.error(msg)
    return False


def _mx_host(domain: str) -> str:
    try:
        records = dns.resolver.resolve(domain, "MX")
        best = sorted(records, key=lambda r: r.preference)[0]
        return str(best.exchange).rstrip(".")
    except Exception as exc:
        logger.warning("MX lookup falhou para %s: %s — usando domínio direto", domain, exc)
        return domain


def _decode_smtp_error(code: int, resp: bytes) -> str:
    text = resp.decode("utf-8", errors="replace") if isinstance(resp, bytes) else str(resp)
    if "unauthenticated" in text.lower() or "spf" in text.lower() or "dkim" in text.lower():
        return (
            "Gmail bloqueou: falta autenticação DNS (SPF/DKIM). "
            "Adicione o registro DKIM no Registro.br — rode: "
            "docker exec setsync-mail python scripts/show_dkim.py"
        )
    return f"Servidor remoto recusou ({code}): {text[:200]}"


def deliver_external(sender: str, recipients: list[str], message: str) -> bool:
    """Entrega e-mail diretamente nos servidores MX do destinatário."""
    global last_error
    last_error = ""

    signed = sign_message(message)
    by_domain: dict[str, list[str]] = {}
    for addr in recipients:
        domain = addr.split("@", 1)[1].lower()
        by_domain.setdefault(domain, []).append(addr)

    for domain, rcpts in by_domain.items():
        mx = _mx_host(domain)
        try:
            with smtplib.SMTP(mx, 25, timeout=60) as server:
                server.ehlo(MAIL_HOSTNAME or DOMAIN)
                code, resp = server.mail(sender)
                if code >= 400:
                    return _set_error(_decode_smtp_error(code, resp))

                for rcpt in rcpts:
                    code, resp = server.rcpt(rcpt)
                    if code >= 400:
                        return _set_error(_decode_smtp_error(code, resp))

                code, resp = server.data(signed)
                if code >= 400:
                    return _set_error(_decode_smtp_error(code, resp))

            logger.info("Entrega externa OK via %s: %s -> %s", mx, sender, rcpts)
        except smtplib.SMTPException as exc:
            return _set_error(f"Falha SMTP para {mx}: {exc}")

    return True
