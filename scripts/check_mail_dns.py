#!/usr/bin/env python3
"""Verifica SPF/DKIM/DMARC do domínio Uníssono.

Uso:
    python scripts/check_mail_dns.py
    docker compose -f docker-compose.prod.yml exec web python scripts/check_mail_dns.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv

    load_dotenv(override=False)
except ImportError:
    pass


def main() -> int:
    from mail_dns import check_mail_dns

    dkim_value = None
    try:
        from mail_server.server.dkim_sign import dns_record, ensure_dkim_keys

        ensure_dkim_keys()
        dkim_value = dns_record()
    except Exception as exc:
        print(f"(aviso) não foi possível ler chave DKIM local: {exc}")

    checks = check_mail_dns(dkim_value=dkim_value)
    failed = 0
    for c in checks:
        status = "OK" if c.ok else "FALHA"
        if not c.ok:
            failed += 1
        print(f"[{status}] {c.name}")
        print(f"        atual:    {c.detail[:200]}")
        if c.expected and not c.ok:
            print(f"        esperado: {c.expected[:200]}")
        print()

    if failed:
        print(
            f"{failed} checagem(ns) falhou/aram. Corrija no DNS (GoDaddy) e rode de novo."
        )
        print(
            "Registros prontos: docker exec setsync-mail python -m mail_server.show_dkim"
        )
        return 1
    print("DNS de e-mail parece ok.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
