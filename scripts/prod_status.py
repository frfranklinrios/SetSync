#!/usr/bin/env python3
"""Status rápido de produção (mail DNS, backup, sentry, PTR)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def _ok(label: str, good: bool, detail: str = "") -> None:
    mark = "OK" if good else "FAIL"
    print(f"[{mark}] {label}" + (f" — {detail}" if detail else ""))


def main() -> int:
    fails = 0

    # Sentry (opcional — nunca crítico)
    dsn = (os.getenv("SENTRY_DSN") or "").strip()
    if dsn:
        _ok("SENTRY_DSN", True, "definido")
    else:
        print("[INFO] SENTRY_DSN — ausente (opcional)")

    # Backup
    bdir = ROOT / "backups"
    dumps = sorted(
        bdir.glob("setsync-*.sql.gz"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if dumps and dumps[0].stat().st_size > 50_000:
        _ok("Backup Postgres", True, dumps[0].name)
    else:
        _ok("Backup Postgres", False, "sem dump recente")
        fails += 1

    # Mail DNS
    try:
        from mail_dns import check_mail_dns
        from mail_server.server.dkim_sign import dns_record, ensure_dkim_keys

        ensure_dkim_keys()
        checks = check_mail_dns(dkim_value=dns_record())
        for c in checks:
            _ok(c.name, c.ok, (c.detail or "")[:80])
            if not c.ok:
                fails += 1
    except Exception as exc:
        _ok("Mail DNS", False, str(exc))
        fails += 1

    print(f"\nResumo: {fails} pendência(s) crítica(s) de e-mail/DNS.")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
