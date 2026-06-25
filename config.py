import os
from datetime import timedelta
from dotenv import load_dotenv

# override=False: variáveis do Docker/systemd têm prioridade sobre .env no disco
load_dotenv(override=False)


def _session_lifetime() -> timedelta:
    """Duração do cookie de sessão (padrão 2 dias)."""
    try:
        days = int(os.getenv('SESSION_LIFETIME_DAYS', '2'))
    except ValueError:
        days = 2
    return timedelta(days=max(1, days))


def _secret_key() -> str:
    from security import assert_secret_key_usable
    return assert_secret_key_usable(os.getenv('SECRET_KEY'))


class Config:
    """Configurações base"""
    SECRET_KEY = _secret_key()
    WTF_CSRF_TIME_LIMIT = None
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///data/banda.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = False  # True em produção HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = _session_lifetime()
    SESSION_REFRESH_EACH_REQUEST = True
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


def google_oauth_enabled() -> bool:
    """Login com Google só quando client_id e secret estão configurados."""
    return bool(
        (os.getenv('GOOGLE_CLIENT_ID') or '').strip()
        and (os.getenv('GOOGLE_CLIENT_SECRET') or '').strip()
    )

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # HTTPS atrás do Nginx: mantenha 1. Só HTTP (teste): SESSION_COOKIE_SECURE=0 no .env
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', '1').lower() in (
        '1', 'true', 'yes',
    )

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def app_timezone_name() -> str:
    """Fuso horário do app (padrão: Fortaleza, CE)."""
    return (os.getenv('SETSYNC_TIMEZONE') or 'America/Fortaleza').strip()


def app_now():
    """Data/hora atual no fuso configurado (Fortaleza por padrão)."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo(app_timezone_name()))


def app_tz():
    """ZoneInfo do fuso configurado."""
    from zoneinfo import ZoneInfo

    try:
        return ZoneInfo(app_timezone_name())
    except Exception:
        return ZoneInfo('America/Fortaleza')


def app_now_naive():
    """Data/hora local (Fortaleza) sem tzinfo — compatível com timestamps no banco."""
    return app_now().replace(tzinfo=None)


def app_now_str() -> str:
    """Timestamp local YYYY-MM-DD HH:MM:SS para o banco."""
    return app_now_naive().strftime('%Y-%m-%d %H:%M:%S')


def app_today_str() -> str:
    """Data local YYYY-MM-DD (Fortaleza por padrão)."""
    return app_now().strftime('%Y-%m-%d')


def whatsapp_number() -> str:
    """Número WhatsApp (DDI+DDD+número, sem +). WHATSAPP_NUMBER ou SETSYNC_WHATSAPP."""
    return (
        os.getenv('WHATSAPP_NUMBER', '').strip()
        or os.getenv('SETSYNC_WHATSAPP', '').strip()
    )


def whatsapp_message() -> str:
    return os.getenv(
        'WHATSAPP_MESSAGE',
        'Olá! Tenho interesse no SetSync para minha banda.',
    ).strip()
