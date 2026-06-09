"""Configuração do servidor WhatsApp (Evolution API)."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv(override=False)


def evolution_api_url() -> str:
    return (os.getenv('EVOLUTION_API_URL') or 'http://evolution-api:8080').strip().rstrip('/')


def evolution_api_key() -> str:
    return (os.getenv('EVOLUTION_API_KEY') or '').strip()


def evolution_instance() -> str:
    return (os.getenv('EVOLUTION_INSTANCE') or 'setsync').strip() or 'setsync'
