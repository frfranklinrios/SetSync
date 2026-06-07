#!/usr/bin/env python3
"""Envia mensagem de teste pela API WhatsApp Cloud."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

load_dotenv()

from whatsapp_service import is_configured, normalize_whatsapp_phone, send_whatsapp_text


def main() -> int:
    if len(sys.argv) < 2:
        print('Uso: python scripts/send_test_whatsapp.py 11999999999')
        return 1
    if not is_configured():
        print('Configure WHATSAPP_API_TOKEN e WHATSAPP_PHONE_NUMBER_ID no .env')
        return 1
    phone = normalize_whatsapp_phone(sys.argv[1])
    if not phone:
        print('Número inválido.')
        return 1
    ok = send_whatsapp_text(
        phone,
        '*SetSync* — teste de notificação\n\nSe você recebeu, a API WhatsApp está funcionando.',
    )
    print('Enviado.' if ok else 'Falha — veja os logs do app.')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
