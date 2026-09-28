"""Checagem de DNS de autenticação de e-mail (SPF / DKIM / DMARC)."""

from __future__ import annotations

import os
import socket
from dataclasses import dataclass

from email_config import MAIL_DOMAIN


@dataclass
class DnsCheck:
    name: str
    ok: bool
    detail: str
    expected: str = ""


def _txt(name: str) -> list[str]:
    try:
        import dns.resolver

        answers = dns.resolver.resolve(name, "TXT")
        out: list[str] = []
        for rdata in answers:
            parts = [
                p.decode() if isinstance(p, bytes) else str(p) for p in rdata.strings
            ]
            out.append("".join(parts))
        return out
    except Exception as exc:
        return [f"(erro: {exc})"]


def _a(name: str) -> list[str]:
    try:
        import dns.resolver

        return [str(r) for r in dns.resolver.resolve(name, "A")]
    except Exception:
        return []


def _mx(name: str) -> list[str]:
    try:
        import dns.resolver

        records = sorted(dns.resolver.resolve(name, "MX"), key=lambda r: r.preference)
        return [f"{r.preference} {str(r.exchange).rstrip('.')}" for r in records]
    except Exception:
        return []


def _ptr(ip: str) -> str:
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except Exception:
        return ""


def expected_spf(ip: str, mail_host: str) -> str:
    return f"v=spf1 ip4:{ip} a:{mail_host} ~all"


def expected_dmarc(domain: str) -> str:
    return f"v=DMARC1; p=none; rua=mailto:contato@{domain}; fo=1"


def check_mail_dns(
    domain: str | None = None,
    selector: str = "unissono",
    mail_host: str | None = None,
    outbound_ip: str | None = None,
    dkim_value: str | None = None,
) -> list[DnsCheck]:
    domain = (domain or MAIL_DOMAIN or "unissono.app").strip().lower()
    mail_host = (mail_host or os.getenv("MAIL_HOSTNAME") or f"mail.{domain}").strip()
    ips = _a(mail_host)
    ip = (
        outbound_ip or os.getenv("MAIL_OUTBOUND_IP") or (ips[0] if ips else "")
    ).strip()

    checks: list[DnsCheck] = []

    # A mail.
    checks.append(
        DnsCheck(
            name=f"A {mail_host}",
            ok=bool(ips),
            detail=", ".join(ips) if ips else "ausente",
            expected=ip or "IP da VPS",
        )
    )

    # SPF no apex (não pode ser DKIM).
    apex_txts = _txt(domain)
    apex_joined = " | ".join(apex_txts) if apex_txts else "(nenhum TXT)"
    has_spf = any(t.lower().startswith("v=spf1") for t in apex_txts)
    has_wrong_dkim = any("v=DKIM1" in t.upper() for t in apex_txts)
    spf_ok = has_spf and (not ip or ip in apex_joined)
    detail = apex_joined
    if has_wrong_dkim:
        detail = "DKIM publicado no apex (errado). " + detail
    checks.append(
        DnsCheck(
            name=f"SPF TXT {domain}",
            ok=spf_ok,
            detail=detail,
            expected=expected_spf(ip or "IP_DA_VPS", mail_host),
        )
    )

    # DKIM no seletor correto.
    dkim_host = f"{selector}._domainkey.{domain}"
    dkim_txts = _txt(dkim_host)
    dkim_joined = " | ".join(dkim_txts) if dkim_txts else "(ausente)"
    has_dkim = any(t.upper().startswith("V=DKIM1") and "p=" in t for t in dkim_txts)
    key_ok = True
    if dkim_value and has_dkim:
        published = next((t for t in dkim_txts if "p=" in t), "")
        # Compara só a parte p= (sem espaços).
        want_p = "".join(dkim_value.split()).split("p=", 1)[-1]
        got_p = "".join(published.split()).split("p=", 1)[-1]
        key_ok = want_p == got_p
        if not key_ok:
            dkim_joined = "chave divergente/corrompida. " + dkim_joined
    checks.append(
        DnsCheck(
            name=f"DKIM TXT {dkim_host}",
            ok=has_dkim and key_ok,
            detail=dkim_joined,
            expected=dkim_value or "v=DKIM1; k=rsa; p=...",
        )
    )

    # DMARC.
    dmarc_host = f"_dmarc.{domain}"
    dmarc_txts = _txt(dmarc_host)
    dmarc_joined = " | ".join(dmarc_txts) if dmarc_txts else "(ausente)"
    has_dmarc = any(t.upper().startswith("V=DMARC1") for t in dmarc_txts)
    checks.append(
        DnsCheck(
            name=f"DMARC TXT {dmarc_host}",
            ok=has_dmarc,
            detail=dmarc_joined,
            expected=expected_dmarc(domain),
        )
    )

    # MX (necessário para receber em @domínio; envio outbound não exige).
    mxs = _mx(domain)
    has_mx = bool(mxs)
    checks.append(
        DnsCheck(
            name=f"MX {domain}",
            ok=has_mx,
            detail=", ".join(mxs)
            if mxs
            else "(nenhum — recebimento @domínio não funciona)",
            expected=f"10 {mail_host}",
        )
    )

    # PTR.
    if ip:
        ptr = _ptr(ip)
        checks.append(
            DnsCheck(
                name=f"PTR {ip}",
                ok=bool(ptr) and mail_host.rstrip(".") in (ptr or "").rstrip("."),
                detail=ptr or "(sem reverse DNS / Contabo padrão)",
                expected=mail_host,
            )
        )

    # Relay (informativo — Outlook/S3150; Gmail costuma funcionar sem relay).
    relay_host = (os.getenv("MAIL_OUTBOUND_RELAY_HOST") or "").strip()
    relay_user = (os.getenv("MAIL_OUTBOUND_RELAY_USER") or "").strip()
    if relay_host:
        detail = relay_host
        if relay_user:
            detail += f" (user {relay_user})"
        checks.append(
            DnsCheck(
                name="Relay SMTP outbound",
                ok=True,
                detail=detail,
                expected="",
            )
        )
    else:
        checks.append(
            DnsCheck(
                name="Relay SMTP outbound",
                ok=True,
                detail=(
                    "não configurado (ok para Gmail). Opcional: MAIL_OUTBOUND_RELAY_* "
                    "se precisar de Outlook/Hotmail."
                ),
                expected="",
            )
        )

    return checks
