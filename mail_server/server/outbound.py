import logging
import os
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
    low = text.lower()
    if "block list" in low or "s3150" in low or "blocked using" in low:
        return (
            f"Destinatário bloqueou o IP de saída (reputação/blocklist). "
            f"Peça delist ao provedor ou use relay SMTP externo. Detalhe: {text[:180]}"
        )
    if "unauthenticated" in low or "spf" in low or "dkim" in low or "dmarc" in low:
        return (
            "Falta autenticação DNS (SPF/DKIM). "
            "No GoDaddy, o TXT do apex deve ser SPF (não DKIM) e o DKIM deve ficar em "
            "unissono._domainkey — rode: "
            "docker exec setsync-mail python -m mail_server.show_dkim"
        )
    return f"Servidor remoto recusou ({code}): {text[:200]}"


def _relay_settings() -> tuple[str, int, bool, str, str] | None:
    host = (os.getenv("MAIL_OUTBOUND_RELAY_HOST") or "").strip()
    if not host:
        return None
    port = int(os.getenv("MAIL_OUTBOUND_RELAY_PORT") or "587")
    use_tls = (os.getenv("MAIL_OUTBOUND_RELAY_TLS") or "1").lower() in ("1", "true", "yes")
    user = (os.getenv("MAIL_OUTBOUND_RELAY_USER") or "").strip()
    password = (os.getenv("MAIL_OUTBOUND_RELAY_PASSWORD") or "").strip()
    return host, port, use_tls, user, password


def _deliver_via_relay(
    sender: str,
    recipients: list[str],
    signed: bytes,
    host: str,
    port: int,
    use_tls: bool,
    user: str,
    password: str,
) -> bool:
    try:
        with smtplib.SMTP(host, port, timeout=60) as server:
            server.ehlo(MAIL_HOSTNAME or DOMAIN)
            if use_tls:
                server.starttls()
                server.ehlo(MAIL_HOSTNAME or DOMAIN)
            if user:
                server.login(user, password)
            code, resp = server.mail(sender)
            if code >= 400:
                return _set_error(_decode_smtp_error(code, resp))
            for rcpt in recipients:
                code, resp = server.rcpt(rcpt)
                if code >= 400:
                    return _set_error(_decode_smtp_error(code, resp))
            code, resp = server.data(signed)
            if code >= 400:
                return _set_error(_decode_smtp_error(code, resp))
        logger.info("Entrega via relay %s: %s -> %s", host, sender, recipients)
        return True
    except smtplib.SMTPException as exc:
        return _set_error(f"Falha SMTP no relay {host}: {exc}")


def deliver_external(sender: str, recipients: list[str], message: str) -> bool:
    """Entrega e-mail diretamente nos servidores MX do destinatário (ou relay)."""
    global last_error
    last_error = ""

    signed = sign_message(message)
    relay = _relay_settings()
    if relay:
        host, port, use_tls, user, password = relay
        return _deliver_via_relay(
            sender, recipients, signed, host, port, use_tls, user, password
        )

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
