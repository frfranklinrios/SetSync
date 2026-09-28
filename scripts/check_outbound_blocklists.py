#!/usr/bin/env python3
"""Checa reputação do IP de saída e testa Gmail vs Outlook (opcional).

Uso:
  python3 scripts/check_outbound_blocklists.py
  python3 scripts/check_outbound_blocklists.py --send voce@gmail.com voce@outlook.com
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

IP = (os.getenv("MAIL_OUTBOUND_IP") or "84.247.130.61").strip()
DNSBLS = (
    "zen.spamhaus.org",
    "bl.spamcop.net",
    "b.barracudacentral.org",
    "dnsbl.sorbs.net",
)


def check_dnsbl(ip: str) -> list[tuple[str, str]]:
    rev = ".".join(reversed(ip.split(".")))
    out: list[tuple[str, str]] = []
    for bl in DNSBLS:
        host = f"{rev}.{bl}"
        try:
            socket.gethostbyname(host)
            out.append((bl, "LISTED"))
        except socket.gaierror:
            out.append((bl, "ok"))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", nargs="*", help="Destinos para teste SMTP real")
    args = parser.parse_args()

    print(f"IP de saída: {IP}")
    ptr = ""
    try:
        ptr = socket.gethostbyaddr(IP)[0]
    except Exception:
        ptr = "(sem PTR local)"
    print(f"PTR: {ptr}")

    for bl, status in check_dnsbl(IP):
        print(f"[{'FAIL' if status == 'LISTED' else 'OK'}] DNSBL {bl}: {status}")

    relay = (os.getenv("MAIL_OUTBOUND_RELAY_HOST") or "").strip()
    print(f"Relay: {relay or '(nenhum — Outlook pode falhar com S3150)'}")

    if args.send:
        from flask import Flask
        from flask_mail import Mail

        import email_config
        from email_service import send_email

        app = Flask(__name__)
        app.config.from_object(email_config)
        Mail(app)
        with app.app_context():
            for dest in args.send:
                ok = send_email(
                    [dest],
                    "Teste Uníssono outbound",
                    body="Teste de entregabilidade Uníssono.",
                    html="<p>Teste de entregabilidade Uníssono.</p>",
                )
                print(f"[{'OK' if ok else 'FAIL'}] send → {dest}")

    print(
        "\nSe Outlook falhar com S3150: https://sender.office.com/ ou MAIL_OUTBOUND_RELAY_*"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
