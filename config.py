import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///data/banda.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = False  # True em produção HTTPS
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 dias
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

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
