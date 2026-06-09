#!/usr/bin/env python3
"""Envia comunicado de atualizações (in-app + e-mail + WhatsApp) a todos os usuários.

Uso:
    python scripts/enviar_atualizacoes.py --dry-run
    python scripts/enviar_atualizacoes.py
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

load_dotenv()

from product_updates import CAMPAIGN_AGENDA_2026_06, enviar_comunicado


def main() -> int:
    parser = argparse.ArgumentParser(description='Comunicado SetSync por e-mail e WhatsApp')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Só conta quantos receberiam, sem enviar',
    )
    parser.add_argument(
        '--campaign',
        default=CAMPAIGN_AGENDA_2026_06,
        help='ID da campanha (padrão: agenda jun/2026)',
    )
    args = parser.parse_args()

    from app import app

    with app.app_context():
        from db import init_db
        from email_service import is_configured as email_ok
        from whatsapp_service import is_configured as wa_ok

        init_db()
        print(f'Campanha: {args.campaign}')
        print(f'SMTP:     {"ok" if email_ok() else "off"}')
        print(f'WhatsApp: {"ok" if wa_ok() else "off"}')
        if args.dry_run:
            print('Modo:     dry-run\n')
        else:
            print('Modo:     envio real\n')

        stats = enviar_comunicado(args.campaign, dry_run=args.dry_run)
        print(
            f'Total {stats["total"]} | '
            f'enviados {stats["enviados"]} | '
            f'já tinham {stats["pulados"]} | '
            f'erros {stats["erros"]}'
        )
    return 0 if stats['erros'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
