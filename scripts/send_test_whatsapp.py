#!/usr/bin/env python3
"""Envia mensagem de teste pelo servidor WhatsApp (Evolution ou Meta)."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

load_dotenv()

from whatsapp_config import whatsapp_provider
from whatsapp_service import is_configured, normalize_whatsapp_phone, send_whatsapp_text


def main() -> int:
    if len(sys.argv) < 2:
        print('Uso: python scripts/send_test_whatsapp.py 11999999999')
        return 2
    if not is_configured():
        provider = whatsapp_provider()
        if provider == 'meta':
            print('Configure WHATSAPP_API_TOKEN e WHATSAPP_PHONE_NUMBER_ID no .env')
        else:
            print('Configure EVOLUTION_API_KEY no .env e suba evolution-api')
            print('Pareie o número em /admin/whatsapp/')
        return 1
    phone = normalize_whatsapp_phone(sys.argv[1])
    if not phone:
        print('Número inválido.')
        return 1
    print(f'Provider: {whatsapp_provider()}')
    print(f'Destino:  {phone}\n')
    ok = send_whatsapp_text(
        phone,
        '*SetSync* — teste de notificação\n\nSe você recebeu, o WhatsApp está funcionando.',
    )
    if ok:
        print('OK: mensagem enviada.')
        return 0
    print('FALHOU — veja logs (container web ou evolution-api).')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
