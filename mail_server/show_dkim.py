"""Imprime os registros DNS necessários para autenticação de e-mail.

Uso:
    docker exec setsync-mail python -m mail_server.show_dkim
"""

from __future__ import annotations

import os
import socket

from mail_server.config import DOMAIN, MAIL_HOSTNAME
from mail_server.server.dkim_sign import dns_host, dns_record, ensure_dkim_keys


def _outbound_ip() -> str:
    env_ip = (os.getenv("MAIL_OUTBOUND_IP") or "").strip()
    if env_ip:
        return env_ip
    try:
        return socket.gethostbyname(MAIL_HOSTNAME)
    except OSError:
        return "IP_DA_VPS"


def main() -> None:
    ensure_dkim_keys()
    ip = _outbound_ip()
    spf = f"v=spf1 ip4:{ip} a:{MAIL_HOSTNAME} ~all"
    dmarc = f"v=DMARC1; p=none; rua=mailto:contato@{DOMAIN}; fo=1"
    dkim = dns_record()
    host = dns_host()

    print("=== DNS de e-mail Uníssono (GoDaddy / domaincontrol) ===\n")
    print("1) TXT do apex (substituir o TXT atual que começa com v=DKIM1 — está errado):")
    print(f"   Nome:  @  (ou {DOMAIN})")
    print(f"   Valor: {spf}\n")
    print("2) TXT DKIM (criar — hoje não existe neste hostname):")
    print(f"   Nome:  unissono._domainkey")
    print(f"   Valor: {dkim}\n")
    print("   FQDN esperado:", host)
    print()
    print("3) TXT DMARC (criar):")
    print("   Nome:  _dmarc")
    print(f"   Valor: {dmarc}\n")
    print("4) MX (opcional, só se o mail local receber mensagem):")
    print(f"   Nome:  @")
    print(f"   Valor: {MAIL_HOSTNAME}  (prioridade 10)\n")
    print("5) PTR / Reverse DNS (painel Contabo):")
    print(f"   {ip} → {MAIL_HOSTNAME}")
    print()
    print("Se o Gmail ainda bloquear com S3150 (blocklist Contabo), use relay externo")
    print("(Zoho/SES/Brevo) ou peça delist — ver docs/06-deploy-contabo.md")


if __name__ == "__main__":
    main()
