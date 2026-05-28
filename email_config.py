import os

# Configurações de e-mail (Flask-Mail) — use .env em produção
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', '1').lower() in ('1', 'true', 'yes')
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
_default_sender = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME or 'noreply@setsync.local')
MAIL_DEFAULT_SENDER = ('SetSync', _default_sender)
