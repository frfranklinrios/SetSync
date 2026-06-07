"""Configuração da API WhatsApp Cloud (Meta) para notificações."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv(override=False)


def whatsapp_api_token() -> str:
    return (
        os.getenv('WHATSAPP_API_TOKEN', '').strip()
        or os.getenv('WHATSAPP_ACCESS_TOKEN', '').strip()
    )


def whatsapp_phone_number_id() -> str:
    return os.getenv('WHATSAPP_PHONE_NUMBER_ID', '').strip()


def whatsapp_api_version() -> str:
    return os.getenv('WHATSAPP_API_VERSION', 'v21.0').strip() or 'v21.0'


def whatsapp_template_name() -> str:
    """Template aprovado no Meta Business (opcional)."""
    return os.getenv('WHATSAPP_TEMPLATE_NAME', '').strip()


def whatsapp_notifications_enabled() -> bool:
    return os.getenv('WHATSAPP_NOTIFICATIONS_ENABLED', '1').lower() in (
        '1', 'true', 'yes', 'on',
    )


def canonical_app_url() -> str:
    return (os.getenv('SETSYNC_CANONICAL_URL') or '').strip().rstrip('/')
