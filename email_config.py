import os
import re

from dotenv import load_dotenv

# Garante leitura do .env mesmo quando importado fora de app.py
load_dotenv(override=False)


def _parse_default_sender(raw: str | None, fallback_email: str) -> tuple[str, str]:
    """Aceita e-mail simples ou formato ``Nome <email@dominio>``."""
    name_default = (os.getenv('MAIL_SENDER_NAME') or 'SetSync').strip() or 'SetSync'
    text = (raw or '').strip()
    if not text:
        return name_default, fallback_email or 'noreply@setsync.local'
    match = re.match(r'^(.+?)\s*<([^>]+)>$', text)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    if '@' in text:
        return name_default, text
    return name_default, fallback_email or text


# Configurações de e-mail (Flask-Mail) — use .env em produção
# Padrão Gmail; produção SetSync usa Zoho (contato@setsync.com.br) — ver .env.example
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.zoho.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', '1').lower() in ('1', 'true', 'yes')
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', '0').lower() in ('1', 'true', 'yes')
MAIL_USERNAME = (os.getenv('MAIL_USERNAME') or '').strip()
MAIL_PASSWORD = (os.getenv('MAIL_PASSWORD') or '').strip()
MAIL_DEFAULT_SENDER = _parse_default_sender(
    os.getenv('MAIL_DEFAULT_SENDER'),
    MAIL_USERNAME,
)
